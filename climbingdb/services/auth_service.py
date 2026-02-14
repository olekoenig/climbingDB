"""
Authentication service for user management.
"""

import bcrypt
from climbingdb.models import SessionLocal, User


class AuthService:
    """Handle user authentication and management."""

    def __init__(self):
        self.session = SessionLocal()

    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def authenticate_user(self, username, password):
        """
        Authenticate a user.

        Returns:
            User object if successful, None otherwise
        """
        user = self.session.query(User).filter(User.username == username).first()

        if not user:
            return None

        # Check password
        if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return user
        return None

    def create_user(self, username, email, password):
        """
        Create a new user.

        Returns:
            (success: bool, message: str, user: User or None)
        """
        # Validation
        if len(username) < 3:
            return False, "Username must be at least 3 characters", None

        if '@' not in email:
            return False, "Invalid email address", None

        # Check if username exists
        existing_user = self.session.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already exists", None

        # Check if email exists
        existing_email = self.session.query(User).filter(User.email == email).first()
        if existing_email:
            return False, "Email already registered", None

        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=self.hash_password(password)
        )

        self.session.add(user)
        self.session.commit()

        return True, "Account created successfully!", user

    def change_password(self, user_id, old_password, new_password):
        """
        Change a user's password.

        Returns:
            (success: bool, message: str)
        """
        user = self.session.query(User).filter(User.id == user_id).first()

        if not user:
            return False, "User not found"

        # Verify old password
        if user.password_hash != self.hash_password(old_password):
            return False, "Current password is incorrect"

        # Update password
        user.password_hash = self.hash_password(new_password)
        self.session.commit()

        return True, "Password changed successfully!"

    def get_user_by_id(self, user_id):
        """Get user by ID."""
        return self.session.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username):
        """Get user by username."""
        return self.session.query(User).filter(User.username == username).first()