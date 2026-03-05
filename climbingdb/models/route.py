from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from climbingdb.models.base import Base


class Route(Base):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    crag_id = Column(Integer, ForeignKey('crags.id'), nullable=False, index=True)
    discipline = Column(String(20), nullable=False, index=True)  # 'Sportclimb', 'Boulder', 'Multipitch'

    consensus_grade = Column(String)  # Average grade
    consensus_ole_grade = Column(Float)
    consensus_stars = Column(Float)

    first_ascent = Column(Date)
    first_ascensionist = Column(String)

    length = Column(Float)
    bolts = Column(Integer)
    ernsthaftigkeit = Column(String(10))

    latitude = Column(Float)
    longitude = Column(Float)

    description = Column(Text)  # Non user-dependent route description
    photo_urls = Column(JSON)  # Wall picture, potentially with first pitch indicated

    timestamp = datetime.now(timezone.utc)
    created_at = Column(Date, default=timestamp)
    updated_at = Column(Date, default=timestamp, onupdate=timestamp)

    # Relationships
    crag = relationship("Crag", back_populates="routes")
    ascents = relationship("Ascent", back_populates="route")
    pitches = relationship("Pitch", back_populates="route")

    def __repr__(self):
        return f"<Route(id={self.id}, name='{self.name}', grade='{self.consensus_grade}', discipline='{self.discipline}')>"

    def __str__(self):
        return f"{self.name} ({self.consensus_grade})"

    @property
    def area(self):
        """Convenience property to access area directly."""
        return self.crag.area if self.crag else None

    @property
    def country(self):
        """Convenience property to access country directly."""
        return self.crag.area.country if self.crag and self.crag.area else None

    @property
    def full_location(self):
        """Return 'Crag, Area, Country'."""
        if self.crag:
            return self.crag.full_location
        return "Unknown"