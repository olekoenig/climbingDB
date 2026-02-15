from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from .base import Base


class Crag(Base):
    __tablename__ = 'crags'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Fields
    name = Column(String(200), nullable=False, index=True)
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False, index=True)

    notes = Column(Text, nullable=True)

    # Relationships
    area = relationship("Area", back_populates="crags")
    routes = relationship("Route", back_populates="crag", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Crag(id={self.id}, name='{self.name}', area='{self.area.name if self.area else None}')>"

    def __str__(self):
        return self.name

    @property
    def full_location(self):
        """Return 'Crag, Area, Country'."""
        if self.area:
            return f"{self.name}, {self.area.full_location}"
        return self.name