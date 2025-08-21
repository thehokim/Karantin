from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()


class Photo(Base):
    __tablename__ = 'photos'
    
    id = Column(Integer, primary_key=True, index=True)
    photo = Column(String, nullable=False)
    photo_url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Pest(Base):
    __tablename__ = 'pests'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_cyrillic = Column(String, nullable=False)
    
    # Relationships
    photos = relationship("Photo", secondary="pest_photos", back_populates="pests")
    damage_details = relationship("DamageDetail", back_populates="pest")
    struggles = relationship("Struggle", back_populates="pest")


class PestPhoto(Base):
    __tablename__ = 'pest_photos'
    
    pest_id = Column(Integer, ForeignKey('pests.id'), primary_key=True)
    photo_id = Column(Integer, ForeignKey('photos.id'), primary_key=True)


class Plant(Base):
    __tablename__ = 'plants'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_cyrillic = Column(String, nullable=False)
    code = Column(String, nullable=False)
    
    # Relationships
    damage_details = relationship("DamageDetail", back_populates="plant")
    plant_monitorings = relationship("PlantMonitoring", back_populates="plant")


class DamageDetail(Base):
    __tablename__ = 'damage_details'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    low_min_value = Column(Float, nullable=False)
    low_max_value = Column(Float, nullable=False)
    medium_min_value = Column(Float, nullable=False)
    medium_max_value = Column(Float, nullable=False)
    high_min_value = Column(Float, nullable=False)
    high_max_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    plant_id = Column(Integer, ForeignKey('plants.id'))
    pest_id = Column(Integer, ForeignKey('pests.id'))
    
    # Relationships
    plant = relationship("Plant", back_populates="damage_details")
    pest = relationship("Pest", back_populates="damage_details")
    damages = relationship("Damage", back_populates="damage_detail")


class Damage(Base):
    __tablename__ = 'damages'
    
    id = Column(Integer, primary_key=True, index=True)
    damage_detail_id = Column(Integer, ForeignKey('damage_details.id'))
    ball = Column(Float, nullable=False)
    risk = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    damage_detail = relationship("DamageDetail", back_populates="damages")
    struggles = relationship("Struggle", back_populates="damage")


class Struggle(Base):
    __tablename__ = 'struggles'
    
    id = Column(Integer, primary_key=True, index=True)
    pest_id = Column(Integer, ForeignKey('pests.id'))
    damage_id = Column(Integer, ForeignKey('damages.id'))
    plant_monitoring_id = Column(Integer, ForeignKey('plant_monitorings.id'))
    struggle_type = Column(String, nullable=False)
    spread_area = Column(Float, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pest = relationship("Pest", back_populates="struggles")
    damage = relationship("Damage", back_populates="struggles")
    plant_monitoring = relationship("PlantMonitoring", back_populates="struggles")
    photos = relationship("Photo", secondary="struggle_photos")


class StrugglePhoto(Base):
    __tablename__ = 'struggle_photos'
    
    struggle_id = Column(Integer, ForeignKey('struggles.id'), primary_key=True)
    photo_id = Column(Integer, ForeignKey('photos.id'), primary_key=True)


class PlantMonitoring(Base):
    __tablename__ = 'plant_monitorings'
    
    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey('plants.id'))
    monitoring_id = Column(Integer, ForeignKey('monitorings.id'))
    area = Column(Float, nullable=False)
    risk = Column(String, nullable=True)
    
    # Relationships
    plant = relationship("Plant", back_populates="plant_monitorings")
    monitoring = relationship("Monitoring", back_populates="plant_monitorings")
    struggles = relationship("Struggle", back_populates="plant_monitoring")
    photos = relationship("Photo", secondary="plant_monitoring_photos")


class PlantMonitoringPhoto(Base):
    __tablename__ = 'plant_monitoring_photos'
    
    plant_monitoring_id = Column(Integer, ForeignKey('plant_monitorings.id'), primary_key=True)
    photo_id = Column(Integer, ForeignKey('photos.id'), primary_key=True)


class Monitoring(Base):
    __tablename__ = 'monitorings'
    
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey('fields.id'))
    checked_location = Column(JSON)  # Store GeoJSON
    plant_area = Column(Float, nullable=False)
    checked_area = Column(Float, nullable=False)
    is_after_cleared = Column(Boolean, default=False)
    is_clear = Column(Boolean, default=False)
    monitoring_time = Column(DateTime, nullable=False)
    risk = Column(String, nullable=False)
    
    # Relationships
    field = relationship("Field", back_populates="monitorings")
    plant_monitorings = relationship("PlantMonitoring", back_populates="monitoring")


class District(Base):
    __tablename__ = 'districts'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_cyrillic = Column(String, nullable=False)
    soato_code = Column(String, nullable=False)
    
    # Relationships
    fields = relationship("Field", back_populates="district")


class Region(Base):
    __tablename__ = 'regions'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_cyrillic = Column(String, nullable=False)
    soato_code = Column(String, nullable=False)
    
    # Relationships
    fields = relationship("Field", back_populates="region")


class Farmer(Base):
    __tablename__ = 'farmers'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tax_or_unique_number = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    data_from = Column(String, nullable=False)
    type = Column(String, nullable=False)
    
    # Relationships
    fields = relationship("Field", back_populates="farmer")


class Field(Base):
    __tablename__ = 'fields'
    
    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey('districts.id'))
    region_id = Column(Integer, ForeignKey('regions.id'))
    warehouse = Column(String, nullable=True)
    farmer_id = Column(Integer, ForeignKey('farmers.id'))
    unique_id = Column(String, nullable=False, unique=True)
    geometry = Column(JSON)  # Store GeoJSON geometry
    centroid = Column(JSON)  # Store GeoJSON point
    area = Column(Float, nullable=False)
    massiv_name = Column(String, nullable=False)
    cadastre_number = Column(String, nullable=False)
    ball_bonitet = Column(Float, nullable=False)
    contour_number = Column(String, nullable=False)
    status = Column(String, nullable=False)
    data_from = Column(String, nullable=False)
    type = Column(String, nullable=False)
    risk = Column(String, nullable=False)
    info = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    district = relationship("District", back_populates="fields")
    region = relationship("Region", back_populates="fields")
    farmer = relationship("Farmer", back_populates="fields")
    monitorings = relationship("Monitoring", back_populates="field")


class Warehouse(Base):
    __tablename__ = 'warehouses'
    
    id = Column(Integer, primary_key=True, index=True)
    warehouse_type = Column(String, nullable=False)
    surface = Column(Float, nullable=True)
    volume = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Add back_populates for Photo relationships
Photo.pests = relationship("Pest", secondary="pest_photos", back_populates="photos")