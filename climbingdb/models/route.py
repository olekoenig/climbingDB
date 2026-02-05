from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, Text, Boolean, JSON
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from .base import Base
from ..grade import Grade


class Route(Base):
    __tablename__ = 'routes'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Basic info
    name = Column(String(200), nullable=False, index=True)
    grade = Column(String(20), nullable=False)  # e.g., "8a", "V10", "7b+"
    ole_grade = Column(Float, nullable=False, index=True)  # Numeric grade for sorting/filtering

    # Location
    crag_id = Column(Integer, ForeignKey('crags.id'), nullable=False, index=True)

    # Climbing details
    discipline = Column(String(20), nullable=False, index=True)  # 'Sportclimb', 'Boulder', 'Multipitch'
    style = Column(String(20), nullable=True)  # 'o.s.', 'F', 'RP', etc.
    date = Column(Date, nullable=True, index=True)

    # Quality and notes
    stars = Column(Integer, default=0)  # 0-3 stars
    shortnote = Column(String(200), nullable=True)  # Brief note (soft, hard, etc.)
    notes = Column(Text, nullable=True)  # Detailed notes

    # Project/milestone status
    is_project = Column(Boolean, default=False, index=True)
    is_milestone = Column(Boolean, default=False, index=True)

    # Multipitch specific
    ernsthaftigkeit = Column(String(10), nullable=True)  # Seriousness rating (X, R, etc.)
    pitches = Column(JSON, nullable=True)  # List of pitch grades: ["7a", "7b", "7a+"]
    length = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    crag = relationship("Crag", back_populates="routes")

    @validates('grade')
    def compute_ole_grade(self, key, grade_value):
        """Automatically compute ole_grade when grade is set."""
        if grade_value:
            self.ole_grade = Grade(grade_value).conv_grade()
        return grade_value

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