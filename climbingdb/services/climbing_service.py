"""
Climbing database service layer.
Replaces the old CSV-based ClimbingQuery with SQLAlchemy database queries.
"""

from sqlalchemy import and_, or_
import pandas as pd

from ..models import SessionLocal, Route, Crag, Area, Country
from ..grade import Grade


class ClimbingService:
    """
    Service class to query the climbing database.
    Returns pandas DataFrames for compatibility with existing frontend.
    """

    def __init__(self):
        """Initialize database session."""
        self.session = SessionLocal()

    def __del__(self):
        """Close session when object is destroyed."""
        if hasattr(self, 'session'):
            self.session.close()

    def __str__(self):
        df = self.get_filtered_routes()[['name', 'grade', 'style', 'crag', 'shortnote', 'notes', 'date', 'stars']]
        return df.__str__()

    def _routes_to_dataframe(self, routes):
        """
        Convert list of Route objects to pandas DataFrame.

        Args:
            routes: List of Route SQLAlchemy objects

        Returns:
            pandas DataFrame with route data
        """
        if not routes:
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'id', 'name', 'grade', 'ole_grade', 'discipline', 'style',
                'date', 'stars', 'shortnote', 'notes',
                'crag', 'area', 'country', 'ernsthaftigkeit', 'pitches', 'length',
                'pitches_ole_grade', 'is_project', 'is_milestone'
            ])

        data = []
        for route in routes:
            # Compute pitches_ole_grade for multipitches
            pitches_ole_grade = None
            if route.discipline == "Multipitch" and route.pitches:
                pitches_ole_grade = [Grade(p['grade']).conv_grade() for p in route.pitches]
            elif route.discipline == "Multipitch":
                # No pitch info, use total grade
                pitches_ole_grade = [route.ole_grade]

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
                'crag': route.crag.name if route.crag else '',
                'area': route.area.name if route.area else '',
                'country': route.country.name if route.country else '',
                'ernsthaftigkeit': route.ernsthaftigkeit if route.ernsthaftigkeit else '',
                'pitches': route.pitches,
                'pitches_ole_grade': pitches_ole_grade,
                'length': route.length if route.length else '',
                'is_project': route.is_project,
                'is_milestone': route.is_milestone,
            }
            data.append(row)

        df = pd.DataFrame(data)
        return df

    def get_filtered_routes(self, discipline="Sportclimb",
                            crag=None, area=None, grade=None, style=None,
                            stars=None, operation="=="):
        """
        Return a route list under the applied filters.

        :param discipline: Sportclimb, Boulder, or Multipitch
        :param crag: Crag name, e.g. 'Schlaraffenland'
        :param area: Area name, e.g. 'Frankenjura'
        :param grade: Grade, e.g. '8a' or '9+/10-'
        :param style: Onsight 'o.s.' or Flash 'F'
        :param stars: Minimum number of stars [0,1,2,3]
        :param operation: logic operation applied to grade [default: ==], currently supported: ==,>=
        :returns: pandas DataFrame
        """
        # Start with base query (exclude projects)
        query = self.session.query(Route).filter(Route.is_project == False)

        # Join tables for filtering by area/country
        query = query.join(Route.crag).join(Crag.area).join(Area.country, isouter=True)

        # Apply filters
        if discipline:
            query = query.filter(Route.discipline == discipline)

        if crag:
            query = query.filter(Crag.name == crag)

        if area:
            query = query.filter(Area.name == area)

        if style:
            query = query.filter(Route.style == style)

        if stars is not None:
            query = query.filter(Route.stars >= stars)

        if grade:
            ole_grade = Grade(grade).conv_grade()
            if operation == ">=":
                query = query.filter(Route.ole_grade >= ole_grade)
            else:  # operation == "=="
                # HACK: Display also slash grades (e.g., 9/9+ when filtering for 9)
                query = query.filter(
                    or_(
                        Route.ole_grade == ole_grade,
                        Route.ole_grade == ole_grade + 0.5
                    )
                )

        # Execute query and sort by grade
        routes = query.order_by(Route.ole_grade.desc()).all()

        return self._routes_to_dataframe(routes)

    def get_multipitches(self):
        """Get all multipitch routes."""
        query = self.session.query(Route).filter(
            and_(
                Route.discipline == "Multipitch",
                Route.is_project == False
            )
        )
        query = query.join(Route.crag).join(Crag.area)
        routes = query.order_by(Route.ole_grade.asc()).all()
        return self._routes_to_dataframe(routes)

    def get_boulders(self):
        """Get all boulder problems."""
        query = self.session.query(Route).filter(
            and_(
                Route.discipline == "Boulder",
                Route.is_project == False
            )
        )
        query = query.join(Route.crag).join(Crag.area)
        routes = query.order_by(Route.ole_grade.asc()).all()
        return self._routes_to_dataframe(routes)

    def get_projects(self, crag=None, area=None):
        """
        Returns the project list in a crag or area.

        :param crag: Filter by crag name
        :param area: Filter by area name
        :returns: pandas DataFrame
        """
        query = self.session.query(Route).filter(Route.is_project == True)
        query = query.join(Route.crag).join(Crag.area)

        if area:
            query = query.filter(Area.name == area)

        if crag:
            query = query.filter(Crag.name == crag)

        routes = query.order_by(Route.ole_grade.asc()).all()
        return self._routes_to_dataframe(routes)

    def get_milestones(self):
        query = self.session.query(Route).filter(Route.is_milestone == True)
        query = query.join(Route.crag).join(Crag.area)
        routes = query.order_by(Route.ole_grade.asc()).all()
        return self._routes_to_dataframe(routes)

    def get_crag_info(self, cragname):
        """
        Get info about a crag.

        :param cragname: Name of the crag
        """
        crag = self.session.query(Crag).filter(Crag.name == cragname).first()

        if not crag or not crag.notes:
            print(f"No information about the crag {cragname} available")
        else:
            print(crag.notes)

    def get_route_info(self, routename):
        """
        Get the logged information about a route.

        :param routename: Name of the route
        """
        route = self.session.query(Route).filter(Route.name == routename).first()

        if not route or not route.notes:
            print(f"No information about the route {routename} available")
        else:
            print(route.notes)

    def get_all_areas(self):
        """Get list of all areas."""
        areas = self.session.query(Area).order_by(Area.name).all()
        return [area.name for area in areas]

    def get_all_crags(self, area=None):
        """Get list of all crags, optionally filtered by area."""
        query = self.session.query(Crag)
        if area:
            query = query.join(Crag.area).filter(Area.name == area)
        crags = query.order_by(Crag.name).all()
        return [crag.name for crag in crags]

    def get_statistics(self):
        """Get overall statistics."""
        stats = {
            'total_routes': self.session.query(Route).filter(Route.is_project == False).count(),
            'total_projects': self.session.query(Route).filter(Route.is_project == True).count(),
            'sportclimbs': self.session.query(Route).filter(
                and_(Route.discipline == "Sportclimb", Route.is_project == False)
            ).count(),
            'boulders': self.session.query(Route).filter(
                and_(Route.discipline == "Boulder", Route.is_project == False)
            ).count(),
            'multipitches': self.session.query(Route).filter(
                and_(Route.discipline == "Multipitch", Route.is_project == False)
            ).count(),
            'total_areas': self.session.query(Area).count(),
            'total_crags': self.session.query(Crag).count(),
            'total_countries': self.session.query(Country).count(),
        }

        # Get hardest route
        hardest = self.session.query(Route).filter(
            Route.is_project == False
        ).order_by(Route.ole_grade.desc()).first()

        if hardest:
            stats['hardest_route'] = hardest.name
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
    print(boulders[['name', 'grade', 'style', 'crag', 'shortnote', 'date', 'stars']].tail(10))

    print("\n=== Projects in Frankenjura ===")
    projects = db.get_projects(area="Frankenjura")
    print(projects[['name', 'grade', 'crag', 'area']])

    print("\n=== Milestones ===")
    milestones = db.get_milestones()
    print(milestones[['name', 'grade', 'crag', 'area', 'date']])

    print("\n=== Filtered routes (8a+ sportclimbs) ===")
    routes = db.get_filtered_routes(discipline="Sportclimb", grade="8a+", operation="==", stars=3)
    print(routes[['name', 'grade', 'crag', 'area']].head(10))