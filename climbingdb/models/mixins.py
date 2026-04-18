"""
Mixins for shared model fields.
"""

from sqlalchemy import Column, String, Float, Text, Integer, inspect
from sqlalchemy.orm import validates
from climbingdb.grade import Grade


class ClimbableMixin:
    """Shared fields for anything that can be climbed (routes, boulders, pitches)."""
    grade = Column(String(20), nullable=False)
    ole_grade = Column(Float, nullable=False, index=True)
    style = Column(String(20), nullable=True)

    stars = Column(Integer, default=0)
    shortnote = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    gear = Column(Text, nullable=True)

    @validates('grade')
    def compute_ole_grade(self, key, grade_value):
        """Automatically compute ole_grade when grade is set."""
        if grade_value:
            self.ole_grade = Grade(grade_value).conv_grade()
        return grade_value


class UpdateableMixin:
    """Mixin providing field introspection for safe updates."""

    # Fields that should never be updated externally
    _excluded_fields = {'id'}

    @classmethod
    def get_updatable_fields(cls):
        """Get column names that can be safely updated. Excludes primary and foreign keys."""
        mapper = inspect(cls).mapper
        excluded = cls._excluded_fields | {
            c.key for c in mapper.column_attrs
            if any(col.foreign_keys for col in c.columns) or any(col.primary_key for col in c.columns)
        }
        return {c.key for c in mapper.column_attrs} - excluded