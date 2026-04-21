from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from climbingdb.models.base import Base
from climbingdb.models.mixins import RouteMixin, UpdateableMixin


class Route(Base, RouteMixin, UpdateableMixin):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    crag_id = Column(Integer, ForeignKey('crags.id'), nullable=False, index=True)
    discipline = Column(String(20), nullable=False, index=True)  # 'Sportclimb', 'Boulder', 'Multipitch'

    first_ascent = Column(Date)
    first_ascensionist = Column(String)

    latitude = Column(Float)
    longitude = Column(Float)

    # Use DateTime instead of Date (-> with seconds)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    crag = relationship("Crag", back_populates="routes")
    ascents = relationship("Ascent", back_populates="route", cascade="all, delete-orphan")
    pitches = relationship("Pitch", back_populates="route", cascade="all, delete-orphan")

    # Excluded fields when updating in frontend
    _excluded_fields = {'id', 'crag_id'}  # crag updated via relationship

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