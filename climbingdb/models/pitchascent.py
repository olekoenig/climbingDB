from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from climbingdb.models.base import Base
from climbingdb.models.mixins import ClimbableMixin


class PitchAscent(Base, ClimbableMixin):
    __tablename__ = 'pitchascents'

    id = Column(Integer, primary_key=True)
    ascent_id = Column(Integer, ForeignKey('ascents.id'))
    pitch_id = Column(Integer, ForeignKey('pitches.id'))

    led = Column(Boolean, default=True)

    ascent = relationship("Ascent", back_populates="pitch_ascents")
    pitch = relationship("Pitch", back_populates="pitch_ascents")