from fastapi import FastAPI, HTTPException, Form, Depends, status, UploadFile, File
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json
import pendulum
from minio import Minio
from minio.error import S3Error
import io, secrets
from uuid import uuid4
import os

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "fields-bucket")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

app = FastAPI()

# Ensure bucket exists on startup
@app.on_event("startup")
def ensure_minio_bucket():
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
    except S3Error as e:
        print(f"MinIO bucket error: {e}")

# Helper for timezone
def now_tz():
    return pendulum.now('Asia/Tashkent')

# Pydantic Models
class Photo(BaseModel):
    id: int
    photo: str
    photo_url: str
    title: Optional[str]
    created_at: datetime = Field(default_factory=now_tz)
    updated_at: datetime = Field(default_factory=now_tz)

class Pest(BaseModel):
    id: int
    photos: List[Photo]
    name: str
    name_cyrillic: str

class DamageDetail(BaseModel):
    id: int
    title: str
    low_min_value: float
    low_max_value: float
    medium_min_value: float
    medium_max_value: float
    high_min_value: float
    high_max_value: float
    created_at: datetime
    plant: int
    pest: int

class Damage(BaseModel):
    id: int
    damage: DamageDetail
    ball: float
    risk: str
    value: float
    created_at: datetime

class Struggle(BaseModel):
    id: int
    pest: Pest
    photos: List[Photo]
    damage: Damage
    struggle_type: str
    spread_area: float
    description: str
    created_at: datetime

class Plant(BaseModel):
    id: int
    name: str
    name_cyrillic: str
    code: str

class PlantMonitoring(BaseModel):
    plant: Plant
    area: float
    photos: List[Photo]
    struggles: List[Struggle]
    risk: Optional[str]

class CheckedLocation(BaseModel):
    type: str
    coordinates: List[float]

class Monitoring(BaseModel):
    id: int
    plants: List[PlantMonitoring]
    checked_location: CheckedLocation
    plant_area: float
    checked_area: float
    is_after_cleared: bool
    is_clear: bool
    monitoring_time: datetime
    risk: str

class District(BaseModel):
    id: int
    name: str
    name_cyrillic: str
    soato_code: str

class Region(BaseModel):
    id: int
    name: str
    name_cyrillic: str
    soato_code: str

class Farmer(BaseModel):
    id: int
    name: str
    tax_or_unique_number: str
    owner_name: str
    phone_number: str
    address: str
    data_from: str
    type: str

class Geometry(BaseModel):
    type: str
    coordinates: List[List[List[float]]]

class Centroid(BaseModel):
    type: str
    coordinates: List[float]

class Warehouse(BaseModel):
    id: int
    warehouse_type: str
    surface: Optional[float]
    volume: float
    description: Optional[str]
    created_at: datetime

class Field(BaseModel):
    id: int
    district: District
    region: Region
    warehouse: Optional[Warehouse]
    farmer: Farmer
    monitorings: List[Monitoring]
    unique_id: str
    geometry: Geometry
    centroid: Centroid
    area: float
    massiv_name: str
    cadastre_number: str
    ball_bonitet: float
    contour_number: str
    status: str
    data_from: str
    type: str
    risk: str
    info: str
    updated_at: datetime
    created_at: datetime

# In-memory storage
fields_db: List[Field] = []

# Basic Auth
security = HTTPBasic()
USERNAME = "admin"
PASSWORD = "securepassword"

def verify_credentials(creds: HTTPBasicCredentials = Depends(security)):
    valid_user = secrets.compare_digest(creds.username, USERNAME)
    valid_pass = secrets.compare_digest(creds.password, PASSWORD)
    if not (valid_user and valid_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"}
        )
    return creds.username

# Create Field endpoint
@app.post("/fields/", response_model=Field, dependencies=[Depends(verify_credentials)])
async def create_field(
    id: int = Form(...),
    district: str = Form(...),
    region: str = Form(...),
    warehouse: Optional[str] = Form(None),
    farmer: str = Form(...),
    monitorings: str = Form(...),
    unique_id: str = Form(...),
    geometry: str = Form(...),
    centroid: str = Form(...),
    area: float = Form(...),
    massiv_name: str = Form(...),
    cadastre_number: str = Form(...),
    ball_bonitet: float = Form(...),
    contour_number: str = Form(...),
    status: str = Form(...),
    data_from: str = Form(...),
    type: str = Form(...),
    risk: str = Form(...),
    info: str = Form(...),
    updated_at: str = Form(...),
    created_at: str = Form(...),
    photos: Optional[List[UploadFile]] = File(None)
):
    try:
        field_dict = {
            "id": id,
            "district": json.loads(district),
            "region": json.loads(region),
            "warehouse": json.loads(warehouse) if warehouse else None,
            "farmer": json.loads(farmer),
            "monitorings": json.loads(monitorings),
            "unique_id": unique_id,
            "geometry": json.loads(geometry),
            "centroid": json.loads(centroid),
            "area": area,
            "massiv_name": massiv_name,
            "cadastre_number": cadastre_number,
            "ball_bonitet": ball_bonitet,
            "contour_number": contour_number,
            "status": status,
            "data_from": data_from,
            "type": type,
            "risk": risk,
            "info": info,
            "updated_at": datetime.fromisoformat(updated_at),
            "created_at": datetime.fromisoformat(created_at)
        }
        field = Field(**field_dict)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in form data")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Handle photo uploads
    if photos:
        for uploaded in photos:
            obj_name = f"photos/{uuid4().hex}_{uploaded.filename}"
            content = await uploaded.read()
            minio_client.put_object(
                MINIO_BUCKET,
                obj_name,
                io.BytesIO(content),
                length=len(content),
                content_type=uploaded.content_type
            )
            url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{obj_name}"
            photo_obj = Photo(
                id=len(fields_db) + 1,
                photo=obj_name,
                photo_url=url,
                title=None
            )
            # Append to first monitoring's first plant photos for example
            field.monitorings[0].plants[0].photos.append(photo_obj)

    fields_db.append(field)
    return field

@app.get("/fields/", response_model=List[Field], dependencies=[Depends(verify_credentials)])
async def list_fields():
    return fields_db

@app.get("/fields/{field_id}", response_model=Field, dependencies=[Depends(verify_credentials)])
async def get_field(field_id: int):
    for f in fields_db:
        if f.id == field_id:
            return f
    raise HTTPException(status_code=404, detail="Field not found")
