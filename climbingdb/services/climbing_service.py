"""
Climbing database service layer with Route/Ascent separation.
"""

from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload, contains_eager
import pandas as pd
from datetime import datetime

from climbingdb.models import SessionLocal, Route, Crag, Area, Country, Pitch, Ascent, PitchAscent
from climbingdb.grade import Grade


class ClimbingService:
    """Service class to query climbing database."""

    def __init__(self, user_id=None):
        self.session = SessionLocal()
        self.user_id = user_id

    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()

    def _base_query(self):
        """Get base query for user's ascents."""
        query = self.session.query(Ascent).join(Ascent.route)
        if self.user_id:
            query = query.filter(Ascent.user_id == self.user_id)
        return query

    def _ascents_to_dataframe(self, ascents) -> pd.DataFrame:
        """Convert list of Ascent objects to DataFrame."""
        if not ascents:
            return pd.DataFrame({
                'id': pd.Series(dtype='int64'),
                'name': pd.Series(dtype='str'),
                'grade': pd.Series(dtype='str'),
                'ole_grade': pd.Series(dtype='float64'),
                'discipline': pd.Series(dtype='str'),
                'style': pd.Series(dtype='str'),
                'date': pd.Series(dtype='datetime64[D]'),
                'stars': pd.Series(dtype='int64'),
                'shortnote': pd.Series(dtype='str'),
                'notes': pd.Series(dtype='str'),
                'gear': pd.Series(dtype='str'),
                'crag': pd.Series(dtype='str'),
                'area': pd.Series(dtype='str'),
                'country': pd.Series(dtype='str'),
                'ernsthaftigkeit': pd.Series(dtype='str'),
                'length': pd.Series(dtype='float64'),
                'ascent_time': pd.Series(dtype='float64'),
                'pitch_number': pd.Series(dtype='int64'),
                'is_project': pd.Series(dtype='bool'),
                'is_milestone': pd.Series(dtype='bool'),
                'pitches_data': pd.Series(dtype='object')
            })

        data = []
        for ascent in ascents:
            route = ascent.route

            # Get pitch ascent data
            pitches_data = None
            if route.discipline == "Multipitch":
                if ascent.pitch_ascents:
                    sorted_pitch_ascents = sorted(ascent.pitch_ascents, key=lambda pa: pa.pitch.pitch_number)
                    pitches_data = {
                        'led': [pa.led for pa in sorted_pitch_ascents],
                        'grade': [pa.grade for pa in sorted_pitch_ascents],
                        'ole_grade': [pa.ole_grade for pa in sorted_pitch_ascents]
                    }
                else:
                    pitches_data = {'ole_grade': [ascent.ole_grade]}

            row = {
                'id': ascent.id,  # Ascent ID
                'route_id': route.id,  # Route ID
                'name': route.name,
                'grade': ascent.grade,  # User's grade
                'ole_grade': ascent.ole_grade,
                'discipline': route.discipline,
                'style': ascent.style if ascent.style else '',
                'date': ascent.date,
                'stars': ascent.stars,
                'shortnote': ascent.shortnote if ascent.shortnote else '',
                'notes': ascent.notes if ascent.notes else '',
                'gear': ascent.gear if ascent.gear else '',
                'crag': route.crag.name if route.crag else '',
                'area': route.crag.area.name if route.crag and route.crag.area else '',
                'country': route.crag.area.country.name if route.crag and route.crag.area and route.crag.area.country else '',
                'ernsthaftigkeit': route.ernsthaftigkeit if route.ernsthaftigkeit else '',
                'length': route.length,
                'ascent_time': ascent.ascent_time,
                'pitch_number': len(ascent.pitch_ascents) if ascent.pitch_ascents else None,
                'is_project': ascent.is_project,
                'is_milestone': ascent.is_milestone,
                'pitches_data': pitches_data
            }
            data.append(row)

        return pd.DataFrame(data)

    def get_filtered_routes(self, discipline="Sportclimb",
                            crag=None, area=None, grade=None, style=None,
                            stars=None, operation="=="):
        """Return filtered ascents as DataFrame."""
        query = self._base_query().filter(Ascent.is_project == False)

        # Eager load route and location
        if area or crag:
            query = query.join(Route.crag).join(Crag.area)
            query = query.options(
                contains_eager(Ascent.route).contains_eager(Route.crag).contains_eager(Crag.area)
            )
            if area:
                query = query.filter(Area.name == area)
            if crag:
                query = query.filter(Crag.name == crag)
        else:
            query = query.options(
                joinedload(Ascent.route).joinedload(Route.crag).joinedload(Crag.area)
            )

        if discipline:
            query = query.filter(Route.discipline == discipline)

        if style:
            query = query.filter(Ascent.style == style)

        if stars is not None:
            query = query.filter(Ascent.stars >= stars)

        if grade:
            ole_grade = Grade(grade).conv_grade()
            if operation == ">=":
                query = query.filter(Ascent.ole_grade >= ole_grade)
            else:
                query = query.filter(
                    or_(Ascent.ole_grade == ole_grade, Ascent.ole_grade == ole_grade + 0.5)
                )

        # Eager load pitch ascents for multipitches
        query = query.options(joinedload(Ascent.pitch_ascents).joinedload(PitchAscent.pitch))

        ascents = query.order_by(Ascent.ole_grade.desc()).all()
        return self._ascents_to_dataframe(ascents)

    def get_multipitches(self):
        """Get all multipitch ascents."""
        query = self._base_query().filter(
            and_(Route.discipline == "Multipitch", Ascent.is_project == False)
        )
        query = query.join(Route.crag).join(Crag.area)
        query = query.options(joinedload(Ascent.pitch_ascents).joinedload(PitchAscent.pitch))
        ascents = query.order_by(Ascent.ole_grade.asc()).all()
        return self._ascents_to_dataframe(ascents)

    def get_boulders(self):
        """Get all boulder ascents."""
        query = self._base_query().filter(
            and_(Route.discipline == "Boulder", Ascent.is_project == False)
        )
        query = query.join(Route.crag).join(Crag.area)
        ascents = query.order_by(Ascent.ole_grade.asc()).all()
        return self._ascents_to_dataframe(ascents)

    def get_projects(self, crag=None, area=None):
        """Get project ascents."""
        query = self._base_query().filter(Ascent.is_project == True)
        query = query.join(Route.crag).join(Crag.area)

        if area:
            query = query.filter(Area.name == area)
        if crag:
            query = query.filter(Crag.name == crag)

        ascents = query.order_by(Ascent.ole_grade.asc()).all()
        return self._ascents_to_dataframe(ascents)

    def get_milestones(self):
        """Get milestone ascents."""
        query = self._base_query().filter(Ascent.is_milestone == True)
        query = query.join(Route.crag).join(Crag.area)
        ascents = query.order_by(Ascent.ole_grade.asc()).all()
        return self._ascents_to_dataframe(ascents)

    def add_ascent(self, name, grade, discipline, crag_name, area_name, country_name,
                   style=None, date=None, stars=0, shortnote=None, notes=None,
                   gear=None, is_project=False, is_milestone=False,
                   ernsthaftigkeit=None, length=None, ascent_time=None,
                   pitches=None, latitude=None, longitude=None):
        """Create ascent (and route if it doesn't exist)."""
        if not self.user_id:
            raise ValueError("user_id required to add ascents")

        try:
            # Get/create location
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

            # Check if Route exists
            route = self.session.query(Route).filter(
                Route.name == name,
                Route.crag_id == crag.id
            ).first()

            if not route:
                # Create new Route
                route = Route(
                    name=name,
                    crag=crag,
                    discipline=discipline,
                    consensus_grade=grade,
                    length=length,
                    latitude=latitude,
                    longitude=longitude
                )
                self.session.add(route)
                self.session.flush()

            # Create Ascent for this user
            ascent = Ascent(
                user_id=self.user_id,
                route=route,
                grade=grade,
                style=style,
                date=date,
                stars=int(stars),
                shortnote=shortnote,
                notes=notes,
                gear=gear,
                ernsthaftigkeit=ernsthaftigkeit,
                is_project=is_project,
                is_milestone=is_milestone,
                ascent_time=ascent_time
            )
            self.session.add(ascent)
            self.session.flush()

            # Add pitches for multipitch
            if discipline == "Multipitch" and pitches:
                for i, pitch_data in enumerate(pitches):
                    # Check if Pitch exists
                    pitch = self.session.query(Pitch).filter(
                        Pitch.route_id == route.id,
                        Pitch.pitch_number == i + 1
                    ).first()

                    if not pitch:
                        # Create universal Pitch
                        pitch = Pitch(
                            route=route,
                            pitch_number=i + 1,
                            pitch_consensus_grade=pitch_data.get('grade'),
                            pitch_length=pitch_data.get('pitch_length'),
                            pitch_name=pitch_data.get('pitch_name'),
                            pitch_ernsthaftigkeit = pitch_data.get('pitch_ernsthaftigkeit')
                        )
                        self.session.add(pitch)
                        self.session.flush()

                    # Create user's PitchAscent
                    pitch_ascent = PitchAscent(
                        ascent=ascent,
                        pitch=pitch,
                        grade=pitch_data.get('grade', '7a'),
                        led=pitch_data.get('led', True),
                        style=pitch_data.get('style'),
                        stars=pitch_data.get('stars', 0),
                        shortnote=pitch_data.get('shortnote'),
                        notes=pitch_data.get('notes'),
                        gear=pitch_data.get('gear'),
                    )
                    self.session.add(pitch_ascent)

            self.session.commit()
            return ascent

        except Exception as e:
            self.session.rollback()
            raise

    def update_ascent(self, ascent_id: int, **kwargs):
        """Update user's ascent."""
        ascent = self._base_query().filter(Ascent.id == ascent_id).first()

        if not ascent:
            return None

        # Update Ascent fields (user's experience)
        for field in ['grade', 'style', 'stars', 'shortnote', 'notes', 'gear',
                      'is_project', 'is_milestone', 'ernsthaftigkeit', 'ascent_time']:
            if field in kwargs:
                setattr(ascent, field, kwargs[field])

        if 'date' in kwargs:
            date = kwargs['date']
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()
            ascent.date = date

        self.session.commit()
        return ascent

    def delete_ascent(self, ascent_id: int) -> bool:
        """Delete user's ascent (and cascade to pitch ascents)."""
        ascent = self._base_query().filter(Ascent.id == ascent_id).first()

        if not ascent:
            return False

        self.session.delete(ascent)
        self.session.commit()
        return True

    def get_ascent_by_id(self, ascent_id: int):
        """Get ascent by ID (user-filtered)."""
        return self._base_query().filter(Ascent.id == ascent_id).first()

    def get_route_by_id(self, route_id: int):
        """Get universal route by ID."""
        return self.session.query(Route).filter(Route.id == route_id).first()

    def get_statistics(self):
        """Get user statistics."""
        base_query = self._base_query()
        stats = {
            'total_routes': base_query.filter(Ascent.is_project == False).count(),
            'total_projects': base_query.filter(Ascent.is_project == True).count(),
            'sportclimbs': base_query.filter(
                and_(Route.discipline == "Sportclimb", Ascent.is_project == False)
            ).count(),
            'boulders': base_query.filter(
                and_(Route.discipline == "Boulder", Ascent.is_project == False)
            ).count(),
            'multipitches': base_query.filter(
                and_(Route.discipline == "Multipitch", Ascent.is_project == False)
            ).count(),
        }

        # Get hardest ascent
        hardest = base_query.filter(Ascent.is_project == False).order_by(Ascent.ole_grade.desc()).first()

        if hardest:
            stats['hardest_route'] = hardest.route.name
            stats['hardest_grade'] = hardest.grade

        return stats


if __name__ == "__main__":
    print("Testing ClimbingService")
    db = ClimbingService()

    print("\n=== Statistics ===")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\n=== Boulders ===")
    boulders = db.get_boulders()
    print(boulders[['name', 'grade', 'style', 'crag', 'date', 'stars']].head(10))

    print("\n=== Filtered (8a+ sport) ===")
    routes = db.get_filtered_routes(discipline="Sportclimb", grade="8a", operation=">=")
    print(routes[['name', 'grade', 'crag', 'area']].head(10))