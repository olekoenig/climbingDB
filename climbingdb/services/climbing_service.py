"""
Climbing database service layer with Route/Ascent separation.
"""

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import joinedload, contains_eager
import pandas as pd
from datetime import datetime

from climbingdb.models import SessionLocal, Route, Crag, Area, Country, Ascent, Pitch, PitchAscent
from climbingdb.grade import Grade
from climbingdb.services.crud import (
    get_or_create_location,
    get_or_create_route,
    create_ascent,
    create_pitches_and_ascents
)


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

    @staticmethod
    def _ascents_to_dataframe(ascents) -> pd.DataFrame:
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
                    pitches_data = {
                        'led': [pa.led for pa in ascent.pitch_ascents],
                        'grade': [pa.grade for pa in ascent.pitch_ascents],
                        'ole_grade': [pa.ole_grade for pa in ascent.pitch_ascents]
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


    @staticmethod
    def _filter_query_for_location(query, area, crag):
        query = query.join(Route.crag).join(Crag.area)
        query = query.options(
            contains_eager(Ascent.route).contains_eager(Route.crag).contains_eager(Crag.area)
        )
        if area:
            query = query.filter(Area.name == area)
        if crag:
            query = query.filter(Crag.name == crag)
        return query


    def get_filtered_routes(self, discipline="Sportclimb",
                            crag=None, area=None, grade=None, style=None,
                            stars=None, operation="=="):
        """Return filtered ascents as DataFrame."""
        query = self._base_query().filter(Ascent.is_project == False)

        # Eager load route and location
        if area or crag:
            query = self._filter_query_for_location(query, area=area, crag=crag)
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

        if area or crag:
            query = self._filter_query_for_location(query, area=area, crag=crag)

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
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()

            crag = get_or_create_location(self.session, country_name, area_name, crag_name)

            route = get_or_create_route(self.session, name, discipline, crag, grade,
                                        length=length, ernsthaftigkeit=ernsthaftigkeit,
                                        latitude=latitude, longitude=longitude)

            ascent = create_ascent(self.session, self.user_id, route, grade,
                                   style=style, date=date, stars=stars,
                                   shortnote=shortnote, notes=notes, gear=gear,
                                   is_project=is_project, is_milestone=is_milestone,
                                   ascent_time=ascent_time)

            if discipline == "Multipitch" and pitches:
                create_pitches_and_ascents(self.session, route, ascent, pitches)

            self.session.commit()  # Commit the ascent first

            # Update consensus fields (grade, stars)
            self.update_consensus_fields(route)
            if discipline == "Multipitch":
                for pitch in route.pitches:
                    self.update_consensus_fields(pitch)
            self.session.commit()  # Single commit for all consensus updates

            return ascent

        except Exception as e:
            self.session.rollback()
            raise


    def update_ascent(self, ascent_id: int, **kwargs):
        ascent = self._base_query().filter(Ascent.id == ascent_id).first()
        if not ascent:
            return None

        # Track ID for later update of the consensus fields
        route_id = ascent.route_id

        ascent_fields = Ascent.get_updatable_fields()
        route_fields = Route.get_updatable_fields()

        for field, value in kwargs.items():
            if field in ascent_fields:
                setattr(ascent, field, value)
            elif field in route_fields:
                setattr(ascent.route, field, value)

        self.session.commit()

        # Update consensus fields
        route = self.session.query(Route).filter(Route.id == route_id).first()
        self.update_consensus_fields(route)

        if 'grade' in kwargs and ascent.route.discipline == "Multipitch":
            for pitch in ascent.route.pitches:
                self.update_consensus_fields(pitch)

        self.session.commit()

        return ascent


    def delete_ascent(self, ascent_id: int) -> bool:
        """Delete user's ascent (and cascade to pitch ascents)."""
        ascent = self._base_query().filter(Ascent.id == ascent_id).first()
        if not ascent:
            return False

        # Save IDs before deletion for later consensus field update
        route_id = ascent.route_id
        pitch_ids = [pa.pitch_id for pa in ascent.pitch_ascents]

        self.session.delete(ascent)
        self.session.commit()

        # Update the consensus fields
        route = self.session.query(Route).filter(Route.id == route_id).first()
        self.update_consensus_fields(route)

        for pitch_id in pitch_ids:
            pitch = self.session.query(Pitch).filter(Pitch.id == pitch_id).first()
            self.update_consensus_fields(pitch)

        self.session.commit()

        return True


    def update_pitch_ascents(self, pitch_updates: list) -> None:
        pitch_fields = Pitch.get_updatable_fields()
        pitch_ascent_fields = PitchAscent.get_updatable_fields()

        updated_pitch_ids = set()

        for update in pitch_updates:
            pitch_ascent_id = update.pop('pitch_ascent_id')
            if not pitch_ascent_id:
                continue

            pa = self.session.query(PitchAscent).filter(
                PitchAscent.id == pitch_ascent_id
            ).first()

            if not pa:
                continue

            for field, value in update.items():
                if field in pitch_ascent_fields:
                    setattr(pa, field, value)
                elif field in pitch_fields and pa.pitch:
                    setattr(pa.pitch, field, value)

            updated_pitch_ids.add(pa.pitch_id)

        self.session.commit()

        # Update the consensus fields (grade, stars)
        for pitch_id in updated_pitch_ids:
            pitch = self.session.query(Pitch).filter(Pitch.id == pitch_id).first()
            self.update_consensus_fields(pitch)
        self.session.commit()

    def update_consensus_fields(self, obj) -> None:
        """
        Update consensus grade and stars for a Route or Pitch.
        Works for both because they share RouteMixin fields.

        Args:
            obj: Route or Pitch object (both have RouteMixin fields)
        """
        # Determine correct table for averaging
        if isinstance(obj, Route):
            avg_ole_grade = self.session.query(
                func.avg(Ascent.ole_grade)
            ).filter(
                Ascent.route_id == obj.id,
                Ascent.is_project == False
            ).scalar()

            avg_stars = self.session.query(
                func.avg(Ascent.stars)
            ).filter(
                Ascent.route_id == obj.id,
                Ascent.is_project == False,
                Ascent.stars > 0
            ).scalar()

        elif isinstance(obj, Pitch):
            avg_ole_grade = self.session.query(
                func.avg(PitchAscent.ole_grade)
            ).filter(
                PitchAscent.pitch_id == obj.id
            ).scalar()

            avg_stars = self.session.query(
                func.avg(PitchAscent.stars)
            ).filter(
                PitchAscent.pitch_id == obj.id,
                PitchAscent.stars > 0
            ).scalar()

        else:
            raise ValueError(f"Expected Route or Pitch, got {type(obj)}")

        # Update shared RouteMixin fields (same for both)
        if avg_ole_grade:
            obj.consensus_ole_grade = avg_ole_grade
            scale = Grade(obj.consensus_grade).get_scale() if obj.consensus_grade else 'French'
            obj.consensus_grade = Grade.from_ole_grade(avg_ole_grade, scale, nearest=True)

        if avg_stars:
            obj.consensus_stars = avg_stars


    def get_ascent_by_id(self, ascent_id: int):
        """Get ascent by ID (user-filtered)."""
        return self._base_query().filter(Ascent.id == ascent_id).first()


    def get_route_by_id(self, route_id: int):
        """Get universal route by ID."""
        return self.session.query(Route).filter(Route.id == route_id).first()


    def get_statistics(self):
        """Get overall statistics for the user."""
        base = self._base_query()
        ascents = base.filter(Ascent.is_project == False)
        ascents_with_routes = ascents.join(Ascent.route)
        sportclimbs = ascents_with_routes.filter(Route.discipline == "Sportclimb")
        multipitches = ascents_with_routes.filter(Route.discipline == "Multipitch")
        boulders = ascents_with_routes.filter(Route.discipline == "Boulder")

        total_ascents = ascents.count()
        total_countries = self.session.query(Country).join(Area).join(Crag).join(Route).join(Ascent).filter(
            Ascent.user_id == self.user_id,
            Ascent.is_project == False
        ).distinct().count()
        total_areas = self.session.query(Area).join(Crag).join(Route).join(Ascent).filter(
            Ascent.user_id == self.user_id,
            Ascent.is_project == False
        ).distinct().count()
        total_crags = self.session.query(Crag).join(Route).join(Ascent).filter(
            Ascent.user_id == self.user_id,
            Ascent.is_project == False
        ).distinct().count()

        hardest_rp = sportclimbs.order_by(Ascent.ole_grade.desc()).first()
        hardest_os = sportclimbs.filter(Ascent.style == "o.s.").order_by(Ascent.ole_grade.desc()).first()
        hardest_flash = sportclimbs.filter(Ascent.style == "F").order_by(Ascent.ole_grade.desc()).first()
        hardest_boulder = boulders.order_by(Ascent.ole_grade.desc()).first()
        hardest_boulder_flash = boulders.filter(Ascent.style == "F").order_by(Ascent.ole_grade.desc()).first()
        hardest_mp = multipitches.order_by(Ascent.ole_grade.desc()).first()
        hardest_mp_os = multipitches.filter(Ascent.style == "o.s.").order_by(Ascent.ole_grade.desc()).first()

        # Calculate some metrics for the achievement badges
        threshold_8a_sport = Grade("8a").conv_grade()
        threshold_8A_boulder = Grade("8A").conv_grade()

        routes_8a_plus = sportclimbs.filter(Ascent.ole_grade >= threshold_8a_sport).count()
        boulders_8A_plus = boulders.filter(Ascent.ole_grade >= threshold_8A_boulder).count()
        ascents_with_notes = ascents.filter(Ascent.notes != None, Ascent.notes != "").count()
        comment_ratio = ascents_with_notes / total_ascents if total_ascents > 0 else 0

        return {
            'total_routes': ascents.count(),
            'sportclimbs': sportclimbs.count(),
            'boulders': boulders.count(),
            'multipitches': multipitches.count(),
            'total_projects': base.filter(Ascent.is_project == True).count(),

            'total_crags': total_crags,
            'total_areas': total_areas,
            'total_countries': total_countries,

            'hardest_redpoint_grade': hardest_rp.grade if hardest_rp else 0,
            'hardest_redpoint_name': hardest_rp.route.name if hardest_rp else None,
            'hardest_onsight_grade': hardest_os.grade if hardest_os else 0,
            'hardest_onsight_name': hardest_os.route.name if hardest_os else None,
            'hardest_flash_grade': hardest_flash.grade if hardest_flash else 0,
            'hardest_flash_name': hardest_flash.route.name if hardest_flash else None,
            'hardest_boulder_grade': hardest_boulder.grade if hardest_boulder else 0,
            'hardest_boulder_name': hardest_boulder.route.name if hardest_boulder else None,
            'hardest_boulder_flash_grade': hardest_boulder_flash.grade if hardest_boulder_flash else 0,
            'hardest_boulder_flash_name': hardest_boulder_flash.route.name if hardest_boulder_flash else None,
            'hardest_multipitch_grade': hardest_mp.grade if hardest_mp else 0,
            'hardest_multipitch_name': hardest_mp.route.name if hardest_mp else None,
            'hardest_multipitch_onsight_grade': hardest_mp_os.grade if hardest_mp_os else 0,
            'hardest_multipitch_onsight_name': hardest_mp_os.route.name if hardest_mp_os else None,

            'routes_8a_plus_count': routes_8a_plus,
            'boulders_8A_plus_count': boulders_8A_plus,
            'comment_ratio': comment_ratio,
        }


if __name__ == "__main__":
    print("Testing ClimbingService")
    db = ClimbingService()

    #print("\n=== Statistics ===")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    #print("\n=== Boulders ===")
    #boulders = db.get_boulders()
    #print(boulders[['name', 'grade', 'style', 'crag', 'date', 'stars']].head(10))

    #print("\n=== Test area filter ===")
    #routes = db.get_filtered_routes(discipline="Multipitch", crag="El Capitan")
    #print(routes)

    #print("\n=== Filtered (8a+ sport) ===")
    #routes = db.get_filtered_routes(discipline="Sportclimb", grade="8a", operation=">=")
    #print(routes[['name', 'grade', 'crag', 'area']].head(10))