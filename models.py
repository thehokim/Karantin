from pydantic import BaseModel, Field # type: ignore
from typing import List, Optional
from datetime import datetime


class Photo(BaseModel):
    id: int
    photo: str
    photo_url: str
    title: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


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


class Field(BaseModel):
    id: int
    district: District
    region: Region
    warehouse: Optional[str]
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


class Warehouse(BaseModel):
    id: int
    warehouse_type: str
    surface: Optional[float]
    volume: float
    description: Optional[str]
    created_at: datetime
