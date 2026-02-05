from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Country(Base):
    __tablename__ = 'countries'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Fields
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(2), unique=True, nullable=True)  # ISO country code (e.g., "DE", "US")

    # Relationships
    areas = relationship("Area", back_populates="country", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return self.name