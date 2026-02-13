"""
Mixins for shared model fields.
"""

from sqlalchemy import Column, String, Float, Text
from sqlalchemy.orm import validates
from climbingdb.grade import Grade


class ClimbableMixin:
    """Shared fields for anything that can be climbed (routes and pitches)."""

    # Climbing details
    grade = Column(String(20), nullable=False)
    ole_grade = Column(Float, nullable=False, index=True)
    style = Column(String(20), nullable=True)

    # Quality and notes
    stars = Column(Float, default=0.0)
    shortnote = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    gear = Column(Text, nullable=True)

    # Multipitch specific
    ernsthaftigkeit = Column(String(10), nullable=True)

    @validates('grade')
    def compute_ole_grade(self, key, grade_value):
        """Automatically compute ole_grade when grade is set."""
        if grade_value:
            self.ole_grade = Grade(grade_value).conv_grade()
        return grade_value
