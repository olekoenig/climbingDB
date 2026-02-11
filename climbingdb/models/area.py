from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base


class Area(Base):
    __tablename__ = 'areas'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Fields
    name = Column(String(200), nullable=False, index=True)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=True, index=True)
    notes = Column(Text, nullable=True)

    # Relationships
    country = relationship("Country", back_populates="areas")
    crags = relationship("Crag", back_populates="area", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Area(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return self.name

    @property
    def full_location(self):
        """Return 'Area, Country' if country exists."""
        if self.country:
            return f"{self.name}, {self.country.name}"
        return self.name