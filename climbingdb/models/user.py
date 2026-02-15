"""
User model for authentication and route ownership.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class User(Base):
    __tablename__ = 'users'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # User credentials
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Never store plain passwords
    email = Column(String(100), unique=True, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    routes = relationship("Route", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

    def __str__(self):
        return self.username