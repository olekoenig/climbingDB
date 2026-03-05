from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from climbingdb.models.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)

    # Mandatory user credentials
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Voluntary information
    name = Column(String(50))
    email = Column(String(100), unique=True)
    bio = Column(Text)
    profile_picture_url = Column(String)
    location = Column(String)

    # Privacy settings
    profile_visibility = Column(String, default='private')  # 'private', 'friends', 'public'
    show_email = Column(Boolean, default=False)
    show_location = Column(Boolean, default=True)
    show_statistics = Column(Boolean, default=True)
    show_notes = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_login = Column(DateTime)

    # Relationships
    ascents = relationship("Ascent", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

    def __str__(self):
        return self.username