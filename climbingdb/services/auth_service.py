"""
Authentication service for user management.
"""

import bcrypt
from climbingdb.models import SessionLocal, User, Ascent


class AuthService:
    def __init__(self):
        self.session = SessionLocal()

    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def authenticate_user(self, username, password):
        user = self.session.query(User).filter(User.username == username).first()

        if not user:
            return None

        # Check password
        if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return user
        return None

    def create_user(self, username, password, email=None):
        if len(username) < 3:
            return False, "Username must be at least 3 characters", None

        existing_user = self.session.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already exists", None

        if email:
            existing_email = self.session.query(User).filter(User.email == email).first()
            if existing_email:
                return False, "Email already registered", None

        user = User(
            username=username,
            password_hash=self.hash_password(password),
            email=email if email else None
        )

        self.session.add(user)
        self.session.commit()

        return True, "Account created successfully!", user

    def change_password(self, user_id, old_password, new_password):
        user = self.session.query(User).filter(User.id == user_id).first()

        if not user:
            return False, "User not found"

        if user.password_hash != self.hash_password(old_password):
            return False, "Current password is incorrect"

        user.password_hash = self.hash_password(new_password)
        self.session.commit()

        return True, "Password changed successfully!"

    def get_user_by_id(self, user_id):
        return self.session.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username):
        return self.session.query(User).filter(User.username == username).first()

    def delete_all_ascents(self, user_id: int) -> int:
        count = self.session.query(Ascent).filter(
            Ascent.user_id == user_id
        ).count()

        self.session.query(Ascent).filter(
            Ascent.user_id == user_id
        ).delete()

        self.session.commit()
        return count

    def delete_account(self, user_id: int) -> None:
        user = self.session.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError("User not found")

        self.session.delete(user)  # Cascade deletes ascents + pitch_ascents
        self.session.commit()