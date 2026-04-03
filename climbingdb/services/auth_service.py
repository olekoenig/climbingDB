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

        if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return user
        return None

    @staticmethod
    def _validate_password(password):
        errors = []
        if len(password) < 8:
            errors.append("Password needs at least 8 characters.")
        #if not any(c.isupper() for c in password):
        #    errors.append("Password needs at least one uppercase letter.")
        #if not any(c.isdigit() for c in password):
        #    errors.append("Password needs at least one number.")
        return errors

    def _validate_username(self, username):
        errors = []
        if len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if self.session.query(User).filter(User.username == username).first():
            errors.append("Username already exists.")
        return errors

    def _validate_email(self, email):
        errors = []
        if self.session.query(User).filter(User.email == email).first():
            errors.append("Email already registered.")
        return errors

    def create_user(self, username, password, email=None):
        errors = []
        errors.extend(self._validate_username(username))
        errors.extend(self._validate_password(password))
        if email:
            errors.extend(self._validate_email(email))

        if errors:
            return False, errors, None

        user = User(
            username=username,
            password_hash=self.hash_password(password),
            email=email if email else None
        )

        self.session.add(user)
        self.session.commit()

        return True, [], user

    def change_password(self, user_id, old_password, new_password):
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            return False, ["User not found."]

        if not bcrypt.checkpw(old_password.encode(), user.password_hash.encode()):
            return False, ["Current password is incorrect."]

        errors = self._validate_password(new_password)
        if errors:
            return False, errors

        user.password_hash = self.hash_password(new_password)
        self.session.commit()

        return True, []

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