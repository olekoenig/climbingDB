from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from climbingdb.models.base import Base
from climbingdb.models.mixins import RouteMixin, UpdateableMixin


class Pitch(Base, RouteMixin, UpdateableMixin):
    __tablename__ = 'pitches'

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.id'), index=True)

    pitch_name = Column(String(200), nullable=True)  # pitch name can be Null (route name must not)
    pitch_number = Column(Integer)

    route = relationship("Route", back_populates="pitches")
    pitch_ascents = relationship("PitchAscent", back_populates="pitch")

    _excluded_fields = {'id', 'route_id'}
