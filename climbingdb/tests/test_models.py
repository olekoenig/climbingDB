"""
Test SQLAlchemy models.

Run as:
    python3 -m unittest climbingdb.tests.test_models
"""

import unittest
import os

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from climbingdb.models import SessionLocal, init_db, drop_all, engine
from climbingdb.models import Country, Area, Crag, Route, User, Pitch


class TestModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Only drop/init if using local SQLite (not production)
        if 'memory' in str(engine.url):
            print(engine.url)
            drop_all()
            init_db()
        else:
            # Skip tests if connected to production database
            print("skipping")
            raise unittest.SkipTest("Skipping model tests - not connected to test database")


    def setUp(self):
        """Create fresh session and clear data for each test."""
        self.session = SessionLocal()

        # Only clear if using SQLite
        if 'sqlite' in str(engine.url):
            self.session.query(Pitch).delete()
            self.session.query(Route).delete()
            self.session.query(Crag).delete()
            self.session.query(Area).delete()
            self.session.query(Country).delete()
            self.session.query(User).delete()
            self.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        self.session.close()

    def test_create_user(self):
        """Test creating a user."""
        user = User(username="testuser", email="test@example.com", password_hash="hashed")
        self.session.add(user)
        self.session.commit()

        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "testuser")

    def test_create_route_with_user(self):
        """Test creating a route with user ownership."""
        user = User(username="climber", email="climber@example.com", password_hash="hash")
        self.session.add(user)
        self.session.commit()

        country = Country(name="Germany", code="DE")
        area = Area(name="Frankenjura", country=country)
        crag = Crag(name="Waldkopf", area=area)
        route = Route(
            user_id=user.id,
            name="Action Directe",
            grade="9a",
            crag=crag,
            discipline="Sportclimb",
            style="RP",
            stars=3
        )
        self.session.add(route)
        self.session.commit()

        self.assertEqual(route.user.username, "climber")
        self.assertEqual(route.name, "Action Directe")

    def test_ole_grade_computation(self):
        """Test automatic ole_grade computation from ClimbableMixin."""
        user = User(username="test", email="test@test.com", password_hash="hash")
        self.session.add(user)
        self.session.commit()

        country = Country(name="USA")
        area = Area(name="Rumney", country=country)
        crag = Crag(name="Waimea", area=area)

        route = Route(
            user_id=user.id,
            name="China Beach",
            grade="5.14b",
            crag=crag,
            discipline="Sportclimb"
        )
        self.session.add(route)
        self.session.commit()

        self.assertEqual(route.ole_grade, 33)

    def test_multipitch_with_pitches(self):
        """Test multipitch route with pitch objects."""
        user = User(username="alpinist", email="alp@example.com", password_hash="hash")
        self.session.add(user)
        self.session.commit()

        country = Country(name="Italy")
        area = Area(name="Dolomites", country=country)
        crag = Crag(name="Cima Grande", area=area)

        multipitch = Route(
            user_id=user.id,
            name="Comici",
            grade="7-",
            crag=crag,
            discipline="Multipitch",
            length=550
        )
        self.session.add(multipitch)
        self.session.flush()

        pitch1 = Pitch(route=multipitch, pitch_number=1, grade="6a", led=True, pitch_name="Start")
        pitch2 = Pitch(route=multipitch, pitch_number=2, grade="6c", led=True, pitch_name="Crux")
        pitch3 = Pitch(route=multipitch, pitch_number=3, grade="6b", led=False)

        self.session.add_all([pitch1, pitch2, pitch3])
        self.session.commit()

        self.assertEqual(len(multipitch.pitches), 3)
        self.assertEqual(multipitch.pitches[0].grade, "6a")
        self.assertEqual(multipitch.pitches[1].pitch_name, "Crux")
        self.assertFalse(multipitch.pitches[2].led)

    def test_pitch_ole_grade_computation(self):
        """Test that pitch grades are computed like routes."""
        user = User(username="test", email="test@test.com", password_hash="hash")
        self.session.add(user)
        self.session.commit()

        country = Country(name="Test")
        area = Area(name="Test", country=country)
        crag = Crag(name="Test", area=area)
        route = Route(user_id=user.id, name="Test", grade="7a", crag=crag, discipline="Multipitch")

        self.session.add(route)
        self.session.flush()

        pitch = Pitch(route=route, pitch_number=1, grade="8a", led=True)
        self.session.add(pitch)
        self.session.commit()

        self.assertEqual(pitch.ole_grade, 29.5)

    def test_query_routes_by_user(self):
        """Test user isolation."""
        user1 = User(username="user1", email="u1@test.com", password_hash="hash")
        user2 = User(username="user2", email="u2@test.com", password_hash="hash")
        self.session.add(user1)
        self.session.add(user2)
        self.session.commit()

        country = Country(name="Test")
        area = Area(name="Test", country=country)
        crag = Crag(name="Test", area=area)

        route1 = Route(user_id=user1.id, name="User1 Route", grade="7a", crag=crag, discipline="Sportclimb")
        route2 = Route(user_id=user2.id, name="User2 Route", grade="7b", crag=crag, discipline="Sportclimb")

        self.session.add_all([route1, route2])
        self.session.commit()

        user1_routes = self.session.query(Route).filter(Route.user_id == user1.id).all()
        user2_routes = self.session.query(Route).filter(Route.user_id == user2.id).all()

        self.assertEqual(len(user1_routes), 1)
        self.assertEqual(len(user2_routes), 1)
        self.assertEqual(user1_routes[0].name, "User1 Route")


if __name__ == "__main__":
    unittest.main()