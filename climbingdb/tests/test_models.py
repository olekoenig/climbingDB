"""
Test SQLAlchemy models.

Run as:
    python3 -m unittest climbingdb.tests.test_models
"""

import unittest
import os

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from climbingdb.models import SessionLocal, init_db, drop_all, engine
from climbingdb.models import Country, Area, Crag, Route, User, Pitch, Ascent


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
            name="Action Directe",
            consensus_grade="9a",
            crag=crag,
            discipline="Sportclimb"
        )
        self.session.add(route)
        ascent = Ascent(
            user_id=user.id,
            route = route,
            style = "F"
        )
        self.session.add(ascent)
        self.session.commit()

        self.assertEqual(ascent.user.username, "climber")
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
            name="China Beach",
            consensus_grade="5.14b",
            crag=crag,
            discipline="Sportclimb"
        )
        self.session.add(route)
        self.session.commit()

        self.assertEqual(route.consensus_ole_grade, 33)

    def test_multipitch_with_pitches(self):
        """Test multipitch route with pitch objects."""
        user = User(username="alpinist", email="alp@example.com", password_hash="hash")
        self.session.add(user)
        self.session.commit()

        country = Country(name="Italy")
        area = Area(name="Dolomites", country=country)
        crag = Crag(name="Cima Grande", area=area)

        multipitch = Route(
            name="Comici",
            consensus_grade="7-",
            crag=crag,
            discipline="Multipitch",
            length=550
        )
        self.session.add(multipitch)
        self.session.flush()

        pitch1 = Pitch(route=multipitch, pitch_number=1, pitch_consensus_grade="6a", pitch_name="Start")
        pitch2 = Pitch(route=multipitch, pitch_number=2, pitch_consensus_grade="6c", pitch_name="Crux")
        pitch3 = Pitch(route=multipitch, pitch_number=3, pitch_consensus_grade="6b")

        self.session.add_all([pitch1, pitch2, pitch3])
        self.session.commit()

        self.assertEqual(len(multipitch.pitches), 3)
        self.assertEqual(multipitch.pitches[0].pitch_consensus_grade, "6a")
        self.assertEqual(multipitch.pitches[1].pitch_name, "Crux")

    def test_pitch_ole_grade_computation(self):
        """Test that pitch grades are computed like routes."""
        user = User(username="test", email="test@test.com", password_hash="hash")
        self.session.add(user)
        self.session.commit()

        country = Country(name="Test")
        area = Area(name="Test", country=country)
        crag = Crag(name="Test", area=area)
        route = Route(name="Test", consensus_grade="7a", crag=crag, discipline="Multipitch")

        self.session.add(route)
        self.session.flush()

        pitch = Pitch(route=route, pitch_number=1, pitch_consensus_grade="8a")
        self.session.add(pitch)
        self.session.commit()

        self.assertEqual(pitch.pitch_consensus_ole_grade, 29.5)


if __name__ == "__main__":
    unittest.main()