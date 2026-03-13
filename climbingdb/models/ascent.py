from sqlalchemy import Column, Integer, ForeignKey, Float, Date, Boolean, JSON
from sqlalchemy.orm import relationship

from climbingdb.models.base import Base
from climbingdb.models.mixins import ClimbableMixin


class Ascent(Base, ClimbableMixin):
    __tablename__ = 'ascents'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    route_id = Column(Integer, ForeignKey('routes.id'), nullable=False, index=True)

    date = Column(Date)
    is_project = Column(Boolean)
    is_milestone = Column(Boolean)

    personal_photo_urls = Column(JSON)

    # Multipitch fields
    ascent_time = Column(Float, nullable=True)  # [hours]

    user = relationship("User", back_populates="ascents")
    route = relationship("Route", back_populates="ascents")
    pitch_ascents = relationship("PitchAscent", back_populates="ascent")