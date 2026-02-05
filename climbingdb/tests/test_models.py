"""
Test SQLAlchemy models.

Run as:
    python3 -m unittest climbingdb.tests.test_models
"""

import unittest

from climbingdb.models import Base, engine, SessionLocal, init_db, drop_all
from climbingdb.models import Country, Area, Crag, Route


class TestModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests."""
        # Use in-memory SQLite for testing
        drop_all()
        init_db()

    def setUp(self):
        """Create a fresh session for each test."""
        self.session = SessionLocal()
        self.session.query(Route).delete()
        self.session.query(Crag).delete()
        self.session.query(Area).delete()
        self.session.query(Country).delete()
        self.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        self.session.rollback()
        self.session.close()

    def test_create_country(self):
        """Test creating a country."""
        country = Country(name="Germany", code="DE")
        self.session.add(country)
        self.session.commit()

        self.assertIsNotNone(country.id)
        self.assertEqual(country.name, "Germany")
        self.assertEqual(country.code, "DE")
        self.assertEqual(str(country), "Germany")

    def test_create_area(self):
        """Test creating an area with country relationship."""
        country = Country(name="Switzerland", code="CH")
        area = Area(name="Magic Wood", country=country)
        self.session.add(area)
        self.session.commit()

        self.assertIsNotNone(area.id)
        self.assertEqual(area.name, "Magic Wood")
        self.assertEqual(area.country.name, "Switzerland")
        self.assertEqual(area.full_location, "Magic Wood, Switzerland")

    def test_create_crag(self):
        """Test creating a crag with area relationship."""
        country = Country(name="Germany", code="DE")
        area = Area(name="Frankenjura", country=country)
        crag = Crag(name="Waldkopf", area=area)
        self.session.add(crag)
        self.session.commit()

        self.assertIsNotNone(crag.id)
        self.assertEqual(crag.name, "Waldkopf")
        self.assertEqual(crag.area.name, "Frankenjura")
        self.assertEqual(crag.full_location, "Waldkopf, Frankenjura, Germany")

    def test_create_route(self):
        """Test creating a route with all relationships."""
        country = Country(name="Germany", code="DE")
        area = Area(name="Frankenjura", country=country)
        crag = Crag(name="Waldkopf", area=area)
        route = Route(
            name="Action Directe",
            grade="9a",
            crag=crag,
            discipline="Sportclimb",
            style="F",
            stars=3.0,
            shortnote="hard"
        )
        self.session.add(route)
        self.session.commit()

        self.assertIsNotNone(route.id)
        self.assertEqual(route.name, "Action Directe")
        self.assertEqual(route.grade, "9a")
        self.assertEqual(route.discipline, "Sportclimb")
        self.assertEqual(route.crag.name, "Waldkopf")
        self.assertEqual(route.area.name, "Frankenjura")
        self.assertEqual(route.country.name, "Germany")

    def test_ole_grade_computation(self):
        """Test that ole_grade is automatically computed from grade."""
        country = Country(name="USA")
        area = Area(name="Rumney", country=country)
        crag = Crag(name="Waimea", area=area)

        route = Route(
            name="China Beach",
            grade="8c",
            crag=crag,
            discipline="Sportclimb"
        )
        self.session.add(route)
        self.session.commit()

        # ole_grade should be computed automatically
        self.assertIsNotNone(route.ole_grade)
        self.assertEqual(route.ole_grade, 33)

    def test_relationships_cascade(self):
        """Test that relationships work correctly."""
        country = Country(name="Spain")
        area = Area(name="Siurana", country=country)
        crag = Crag(name="El Pati", area=area)
        self.session.add_all([country, area, crag])
        self.session.commit()

        # Test forward relationships
        self.assertEqual(len(country.areas), 1)
        self.assertEqual(len(area.crags), 1)
        self.assertEqual(country.areas[0].name, "Siurana")
        self.assertEqual(area.crags[0].name, "El Pati")

    def test_boulder_grade(self):
        """Test boulder grade conversion."""
        country = Country(name="USA")
        area = Area(name="Bishop", country=country)
        crag = Crag(name="Buttermilks", area=area)

        boulder = Route(
            name="Evilution",
            grade="V10",
            crag=crag,
            discipline="Boulder"
        )
        self.session.add(boulder)
        self.session.commit()

        self.assertEqual(boulder.grade, "V10")
        self.assertEqual(boulder.ole_grade, 10)  # V10 = 10 in vermin scale

    def test_multipitch_route(self):
        """Test multipitch with pitches and ernsthaftigkeit."""
        country = Country(name="Switzerland")
        area = Area(name="Rätikon", country=country)
        crag = Crag(name="5. Kirchlispitze", area=area)

        multipitch = Route(
            name="Hannibals Albtraum",
            grade="7c",
            crag=crag,
            discipline="Multipitch",
            ernsthaftigkeit="pp",
            pitches=["7a+", "7b+", "7b+", "7c", "7a+"]
        )
        self.session.add(multipitch)
        self.session.commit()

        self.assertEqual(multipitch.ernsthaftigkeit, "pp")
        self.assertEqual(len(multipitch.pitches), 5)
        self.assertEqual(multipitch.pitches[2], "7b+")

    def test_project_flag(self):
        """Test project status."""
        country = Country(name="Germany")
        area = Area(name="Frankenjura", country=country)
        crag = Crag(name="Krottenseer Turm", area=area)

        project = Route(
            name="Wallstreet",
            grade="8c",
            crag=crag,
            discipline="Sportclimb",
            is_project=True
        )
        self.session.add(project)
        self.session.commit()

        self.assertTrue(project.is_project)

    def test_query_routes_by_discipline(self):
        """Test querying routes by discipline."""
        country = Country(name="Test Country")
        area = Area(name="Test Area", country=country)
        crag = Crag(name="Test Crag", area=area)

        sport = Route(name="Sport Route", grade="7a", crag=crag, discipline="Sportclimb")
        boulder = Route(name="Boulder Problem", grade="V5", crag=crag, discipline="Boulder")

        self.session.add_all([sport, boulder])
        self.session.commit()

        sport_routes = self.session.query(Route).filter(Route.discipline == "Sportclimb").all()
        boulder_routes = self.session.query(Route).filter(Route.discipline == "Boulder").all()

        self.assertEqual(len(sport_routes), 1)
        self.assertEqual(len(boulder_routes), 1)
        self.assertEqual(sport_routes[0].name, "Sport Route")


if __name__ == "__main__":
    unittest.main()