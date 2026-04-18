from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from climbingdb.models.base import Base
from climbingdb.models.mixins import ClimbableMixin, UpdateableMixin


class PitchAscent(Base, ClimbableMixin, UpdateableMixin):
    __tablename__ = 'pitchascents'

    id = Column(Integer, primary_key=True)
    ascent_id = Column(Integer, ForeignKey('ascents.id'), index=True)
    pitch_id = Column(Integer, ForeignKey('pitches.id'), index=True)

    led = Column(Boolean, default=True)

    ascent = relationship("Ascent", back_populates="pitch_ascents")
    pitch = relationship("Pitch", back_populates="pitch_ascents")

    _excluded_fields = {'id', 'ascent_id', 'pitch_id'}