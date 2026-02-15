from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship

from climbingdb.models.base import Base
from climbingdb.models.mixins import ClimbableMixin


class Pitch(Base, ClimbableMixin):  # Inherits same shared fields
    __tablename__ = 'pitches'

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.id'), nullable=False)

    # Pitch-specific fields
    led = Column(Boolean, default=True)
    pitch_number = Column(Integer, nullable=False)
    pitch_length = Column(Float, nullable=True)  # [meters]
    pitch_name = Column(String(200), nullable=True)

    # Relationship
    route = relationship("Route", back_populates="pitches")
