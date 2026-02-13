from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from climbingdb.models.base import Base
from climbingdb.models.mixins import ClimbableMixin


class Route(Base, ClimbableMixin):
    __tablename__ = 'routes'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Global ascent info
    name = Column(String(200), nullable=False, index=True)
    crag_id = Column(Integer, ForeignKey('crags.id'), nullable=False, index=True)
    discipline = Column(String(20), nullable=False, index=True)  # 'Sportclimb', 'Boulder', 'Multipitch'
    date = Column(Date, nullable=True, index=True)
    stars = Column(Integer, default=0)
    is_project = Column(Boolean, default=False, index=True)
    is_milestone = Column(Boolean, default=False, index=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Multipitch specific
    ascent_time = Column(Float, nullable=True)  # [hours]
    pitch_number = Column(Integer, nullable=True)
    length = Column(Float, nullable=True)

    timestamp = datetime.now(timezone.utc)
    created_at = Column(Date, default=timestamp)
    updated_at = Column(Date, default=timestamp, onupdate=timestamp)

    # Relationships
    user = relationship("User", back_populates="routes")
    crag = relationship("Crag", back_populates="routes")
    pitches = relationship("Pitch", back_populates="route")

    def __repr__(self):
        return f"<Route(id={self.id}, name='{self.name}', grade='{self.grade}', discipline='{self.discipline}')>"

    def __str__(self):
        return f"{self.name} ({self.grade})"

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