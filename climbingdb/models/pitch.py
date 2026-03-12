from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship, validates

from climbingdb.models.base import Base
from climbingdb.grade import Grade


class Pitch(Base):
    __tablename__ = 'pitches'

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.id'), index=True)

    # Reference info about the pitch
    pitch_consensus_grade = Column(String)
    pitch_consensus_ole_grade = Column(Float)
    pitch_number = Column(Integer)
    pitch_name = Column(String)
    pitch_length = Column(Float)
    pitch_ernsthaftigkeit = Column(String(10), nullable=True)
    pitch_description = Column(Text)  # non-user dependent pitch description

    route = relationship("Route", back_populates="pitches")
    pitch_ascents = relationship("PitchAscent", back_populates="pitch")

    @validates('pitch_consensus_grade')
    def compute_pitch_consensus_ole_grade(self, key, grade_value):
        if grade_value:
            self.pitch_consensus_ole_grade = Grade(grade_value).conv_grade()
        return grade_value