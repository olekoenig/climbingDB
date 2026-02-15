"""
Climbing database service layer.
"""

from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload, contains_eager
import pandas as pd
from datetime import datetime

from ..models import SessionLocal, Route, Crag, Area, Country, Pitch
from ..grade import Grade


class ClimbingService:
    """Service class to query the climbing database."""

    def __init__(self, user_id=None):
        self.session = SessionLocal()
        self.user_id = user_id

    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()

    def __str__(self):
        df = self.get_filtered_routes()[['name', 'grade', 'style', 'crag', 'shortnote', 'notes', 'date', 'stars']]
        return df.__str__()

    def _base_query(self):
        """Get base query filtered by user_id if set."""
        query = self.session.query(Route)
        if self.user_id:
            query = query.filter(Route.user_id == self.user_id)
        return query

    def _routes_to_dataframe(self, routes) -> pd.DataFrame:
        """Convert list of Route objects to pandas DataFrame."""
        if not routes:
            return pd.DataFrame({
                'id': pd.Series(dtype='int'),
                'name': pd.Series(dtype='str'),
                'grade': pd.Series(dtype='str'),
                'ole_grade': pd.Series(dtype='float'),
                'discipline': pd.Series(dtype='str'),
                'style': pd.Series(dtype='str'),
                'date': pd.Series(dtype='datetime64[D]'),
                'stars': pd.Series(dtype='int'),
                'shortnote': pd.Series(dtype='str'),
                'notes': pd.Series(dtype='str'),
                'gear': pd.Series(dtype='str'),
                'crag': pd.Series(dtype='str'),
                'area': pd.Series(dtype='str'),
                'country': pd.Series(dtype='str'),
                'ernsthaftigkeit': pd.Series(dtype='str'),
                'length': pd.Series(dtype='float'),
                'ascent_time': pd.Series(dtype='float'),
                'pitch_number': pd.Series(dtype='int'),
                'is_project': pd.Series(dtype='bool'),
                'is_milestone': pd.Series(dtype='bool'),
                'pitches_data': pd.Series(dtype='object')
            })

        data = []
        for route in routes:
            pitches_data = None
            if route.discipline == "Multipitch":
                if route.pitches:
                    pitches_data = {
                        'led': [p.led for p in route.pitches],
                        'grade': [p.grade for p in route.pitches],
                        'ole_grade': [p.ole_grade for p in route.pitches]
                    }
                else:
                    # Somewhat of a hack to make multipitch visualization work
                    pitches_data = {'ole_grade': [route.ole_grade]}

            row = {
                'id': route.id,
                'name': route.name,
                'grade': route.grade,
                'ole_grade': route.ole_grade,
                'discipline': route.discipline,
                'style': route.style if route.style else '',
                'date': route.date,
                'stars': route.stars,
                'shortnote': route.shortnote if route.shortnote else '',
                'notes': route.notes if route.notes else '',
                'gear': route.gear if route.gear else '',
                'crag': route.crag.name if route.crag else '',
                'area': route.area.name if route.area else '',
                'country': route.country.name if route.country else '',
                'ernsthaftigkeit': route.ernsthaftigkeit if route.ernsthaftigkeit else '',
                'length': route.length,
                'ascent_time': route.ascent_time,
                'pitch_number': route.pitch_number,
                'is_project': route.is_project,
                'is_milestone': route.is_milestone,
                'pitches_data': pitches_data
            }
            data.append(row)

        return pd.DataFrame(data)

    def get_filtered_routes(self, discipline="Sportclimb",
                            crag=None, area=None, grade=None, style=None,
                            stars=None, operation="=="):
        """Return filtered routes as DataFrame."""
        query = self._base_query()

        if discipline != "Multipitch":
            query = query.filter(Route.is_project == False)

        if area or crag:
            query = query.join(Route.crag).join(Crag.area)
            query = query.options(contains_eager(Route.crag).contains_eager(Crag.area))

            if area:
                query = query.filter(Area.name == area)
            if crag:
                query = query.filter(Crag.name == crag)
        else:
            query = query.options(joinedload(Route.crag).joinedload(Crag.area))

        if discipline:
            query = query.filter(Route.discipline == discipline)

        if style:
            query = query.filter(Route.style == style)

        if stars is not None:
            query = query.filter(Route.stars >= stars)

        if grade:
            ole_grade = Grade(grade).conv_grade()
            if operation == ">=":
                query = query.filter(Route.ole_grade >= ole_grade)
            else:
                query = query.filter(
                    or_(Route.ole_grade == ole_grade, Route.ole_grade == ole_grade + 0.5)
                )

        routes = query.order_by(Route.ole_grade.desc()).all()
        return self._routes_to_dataframe(routes)

    def get_multipitches(self):
        """Get all multipitch routes."""
        query = self._base_query().filter(Route.discipline == "Multipitch")
        query = query.join(Route.crag).join(Crag.area)
        routes = query.order_by(Route.ole_grade.asc()).all()
        return self._routes_to_dataframe(routes)

    def get_boulders(self):
        """Get all boulder problems."""
        query = self._base_query().filter(
            and_(Route.discipline == "Boulder", Route.is_project == False)
        )
        query = query.join(Route.crag).join(Crag.area)
        routes = query.order_by(Route.ole_grade.asc()).all()
        return self._routes_to_dataframe(routes)

    def get_projects(self, crag=None, area=None):
        """Get projects, optionally filtered by crag or area."""
        query = self._base_query().filter(Route.is_project == True)
        query = query.join(Route.crag).join(Crag.area)

        if area:
            query = query.filter(Area.name == area)
        if crag:
            query = query.filter(Crag.name == crag)

        routes = query.order_by(Route.ole_grade.asc()).all()
        return self._routes_to_dataframe(routes)

    def get_milestones(self):
        """Get milestone routes."""
        query = self._base_query().filter(Route.is_milestone == True)
        query = query.join(Route.crag).join(Crag.area)
        routes = query.order_by(Route.ole_grade.asc()).all()
        return self._routes_to_dataframe(routes)

    def add_route(self, name, grade, discipline, crag_name, area_name, country_name,
                  style=None, date=None, stars=0, shortnote=None, notes=None,
                  gear=None, is_project=False, is_milestone=False,
                  ernsthaftigkeit=None, length=None, ascent_time=None, pitch_number=None,
                  pitches=None, latitude=None, longitude=None):
        """Create a new route with optional pitches."""
        if not self.user_id:
            raise ValueError("user_id required to add routes")

        country = None
        if country_name:
            country = self.session.query(Country).filter(Country.name == country_name).first()
            if not country:
                country = Country(name=country_name)
                self.session.add(country)
                self.session.flush()

        area = self.session.query(Area).filter(Area.name == area_name).first()
        if not area:
            area = Area(name=area_name, country=country)
            self.session.add(area)
            self.session.flush()

        crag = self.session.query(Crag).filter(
            Crag.name == crag_name,
            Crag.area_id == area.id
        ).first()
        if not crag:
            crag = Crag(name=crag_name, area=area)
            self.session.add(crag)
            self.session.flush()

        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()

        route = Route(
            user_id=self.user_id,
            name=name,
            grade=grade,
            discipline=discipline,
            crag=crag,
            style=style,
            date=date,
            stars=int(stars),
            shortnote=shortnote,
            notes=notes,
            gear=gear,
            is_project=is_project,
            is_milestone=is_milestone,
            ernsthaftigkeit=ernsthaftigkeit,
            length=length,
            ascent_time=ascent_time,
            pitch_number=pitch_number,
            latitude=latitude,
            longitude=longitude
        )

        self.session.add(route)
        self.session.flush()

        if discipline == "Multipitch" and pitches:
            for i, pitch_data in enumerate(pitches):
                pitch = Pitch(
                    route=route,
                    pitch_number=i + 1,
                    grade=pitch_data.get('grade', ''),
                    led=pitch_data.get('led', True),
                    style=pitch_data.get('style'),
                    stars=pitch_data.get('stars', 0),
                    shortnote=pitch_data.get('shortnote'),
                    notes=pitch_data.get('notes'),
                    gear=pitch_data.get('gear'),
                    ernsthaftigkeit=pitch_data.get('ernsthaftigkeit'),
                    pitch_length=pitch_data.get('pitch_length'),
                    pitch_name=pitch_data.get('pitch_name')
                )
                self.session.add(pitch)

        self.session.commit()
        return route

    def update_route(self, route_id: int, **kwargs):
        """Update an existing route."""
        route = self.session.query(Route).filter(Route.id == route_id).first()

        if not route:
            return None

        for field in ['name', 'grade', 'discipline', 'style', 'stars',
                      'shortnote', 'notes', 'gear', 'is_project', 'is_milestone',
                      'ernsthaftigkeit', 'length', 'ascent_time', 'pitch_number']:
            if field in kwargs:
                setattr(route, field, kwargs[field])

        if 'date' in kwargs:
            date = kwargs['date']
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()
            route.date = date

        if 'crag_name' in kwargs or 'area_name' in kwargs:
            area_name = kwargs.get('area_name')
            crag_name = kwargs.get('crag_name')
            country_name = kwargs.get('country_name')

            if area_name:
                country = None
                if country_name:
                    country = self.session.query(Country).filter(Country.name == country_name).first()
                    if not country:
                        country = Country(name=country_name)
                        self.session.add(country)
                        self.session.flush()

                area = self.session.query(Area).filter(Area.name == area_name).first()
                if not area:
                    area = Area(name=area_name, country=country)
                    self.session.add(area)
                    self.session.flush()

                if crag_name:
                    crag = self.session.query(Crag).filter(
                        Crag.name == crag_name,
                        Crag.area_id == area.id
                    ).first()
                    if not crag:
                        crag = Crag(name=crag_name, area=area)
                        self.session.add(crag)
                        self.session.flush()

                    route.crag = crag

        self.session.commit()
        return route

    def delete_route(self, route_id: int) -> bool:
        """Delete a route."""
        route = self.session.query(Route).filter(Route.id == route_id).first()

        if not route:
            return False

        self.session.delete(route)
        self.session.commit()
        return True

    def get_route_by_id(self, route_id: int):
        # Debug: Check what database we're connected to
        """
        from sqlalchemy import text
        db_info = self.session.execute(text("SELECT 1")).fetchone()
        print(f"Connected to: {self.session.bind.url}")

        # Check if route exists at all (no user filter)
        route_all = self.session.query(Route).filter(Route.id == route_id).first()
        if route_all:
            print(f"Route {route_id} exists, user_id: {route_all.user_id}")
        else:
            print(f"Route {route_id} doesn't exist in database")
            # Show what IDs DO exist
            all_ids = [r.id for r in self.session.query(Route.id).all()]
            print(f"Sample route IDs in database: {all_ids}")
        """
        return self._base_query().filter(Route.id == route_id).first()

    def get_route_by_name(self, name, crag_name=None):
        query = self._base_query().filter(Route.name == name)

        if crag_name:
            query = query.join(Route.crag).filter(Crag.name == crag_name)

        return query.first()


if __name__ == "__main__":
    print("Testing ClimbingService")
    db = ClimbingService()

    print("\n=== Statistics ===")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\n=== Boulders ===")
    boulders = db.get_boulders()
    print(boulders[['name', 'grade', 'style', 'crag', 'shortnote', 'date', 'stars']].tail(10))

    print("\n=== Filtered routes (8a+ sportclimbs) ===")
    routes = db.get_filtered_routes(discipline="Sportclimb", grade="8a", operation=">=")
    print(routes[['name', 'grade', 'crag', 'area']].head(10))