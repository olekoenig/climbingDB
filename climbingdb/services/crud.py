"""
Shared CRUD operations for location and route/ascent creation.
Used by both climbing_service.py and csv_to_sqlalchemy.py.
"""

from climbingdb.models import Country, Area, Crag, Route, Pitch, Ascent, PitchAscent


def get_or_create_country(session, country_name, verbose=False):
    if not country_name:
        raise ValueError("Country is required")

    country = session.query(Country).filter(Country.name == country_name).first()
    if not country:
        country = Country(name=country_name)
        session.add(country)
        session.flush()
        if verbose:
            print(f"  Created country: {country_name}")

    return country


def get_or_create_area(session, area_name, country, verbose=False):
    if not area_name:
        raise ValueError("Area is required")

    query = session.query(Area).filter(Area.name == area_name)
    if country:
        query = query.filter(Area.country_id == country.id)

    area = query.first()
    if not area:
        area = Area(name=area_name, country=country)
        session.add(area)
        session.flush()
        if verbose:
            print(f"  Created area: {area_name}, {country.name if country else ''}")

    return area


def get_or_create_crag(session, crag_name, area, verbose=False):
    """Get existing crag or create new one."""
    if not crag_name:
        raise ValueError("Crag is required")

    crag = session.query(Crag).filter(
        Crag.name == crag_name,
        Crag.area_id == area.id
    ).first()

    if not crag:
        crag = Crag(name=crag_name, area=area)
        session.add(crag)
        session.flush()
        if verbose:
            print(f"  Created crag: {crag_name}")

    return crag


def get_or_create_location(session, country_name, area_name, crag_name, verbose=False):
    """Get or create full location hierarchy (country/area/crag)."""
    country = get_or_create_country(session, country_name, verbose=verbose)
    area = get_or_create_area(session, area_name, country, verbose=verbose)
    crag = get_or_create_crag(session, crag_name, area, verbose=verbose)
    return crag


def get_or_create_route(session, name, discipline, crag, grade,
                        length=None, ernsthaftigkeit=None,
                        latitude=None, longitude=None, verbose=False):
    """Get existing route or create new universal route."""
    route = session.query(Route).filter(
        Route.name == name,
        Route.crag_id == crag.id,
        Route.discipline == discipline
    ).first()

    if route and verbose:
        print(f"  Route {name} already exists")

    if not route:
        route = Route(
            name=name,
            crag=crag,
            discipline=discipline,
            consensus_grade=grade,
            length=length,
            ernsthaftigkeit=ernsthaftigkeit,
            latitude=latitude,
            longitude=longitude
        )
        session.add(route)
        session.flush()
        if verbose:
            print(f"  Created route: {name}")

    return route


def create_ascent(session, user_id, route, grade, style=None, date=None,
                  stars=0, shortnote=None, notes=None, gear=None,
                  is_project=False, is_milestone=False,
                  ascent_time=None):
    """Create user's ascent of a route."""
    # Check for duplicate: same user, route, and date
    existing = session.query(Ascent).filter(
        Ascent.user_id == user_id,
        Ascent.route_id == route.id,
        Ascent.date == date
    ).first()

    if existing:
        return existing

    ascent = Ascent(
        user_id=user_id,
        route=route,
        grade=grade,
        style=style,
        date=date,
        stars=int(stars),
        shortnote=shortnote,
        notes=notes,
        gear=gear,
        is_project=is_project,
        is_milestone=is_milestone,
        ascent_time=ascent_time
    )
    session.add(ascent)
    session.flush()
    return ascent


def get_or_create_pitch(session, route, pitch_number, pitch_data):
    """Get existing pitch or create new universal pitch."""
    pitch = session.query(Pitch).filter(
        Pitch.route_id == route.id,
        Pitch.pitch_number == pitch_number
    ).first()

    if not pitch:
        pitch = Pitch(
            route=route,
            pitch_number=pitch_number,
            consensus_grade=pitch_data.get('grade'),
            length=pitch_data.get('length'),
            pitch_name=pitch_data.get('pitch_name'),
            ernsthaftigkeit=pitch_data.get('ernsthaftigkeit')
        )
        session.add(pitch)
        session.flush()

    return pitch


def create_pitch_ascent(session, ascent, pitch, pitch_data):
    """Create user's ascent of a specific pitch."""
    pitch_ascent = PitchAscent(
        ascent=ascent,
        pitch=pitch,
        grade=pitch_data.get('grade'),
        led=pitch_data.get('led', True),
        style=pitch_data.get('style'),
        stars=pitch_data.get('stars', 0),
        shortnote=pitch_data.get('shortnote'),
        notes=pitch_data.get('notes'),
        gear=pitch_data.get('gear')
    )
    session.add(pitch_ascent)
    session.flush()
    return pitch_ascent


def create_pitches_and_ascents(session, route, ascent, pitches_data):
    """Create pitches and pitch ascents for a multipitch route."""
    if not pitches_data:
        return

    for i, pitch_data in enumerate(pitches_data):
        pitch = get_or_create_pitch(session, route, i + 1, pitch_data)
        create_pitch_ascent(session, ascent, pitch, pitch_data)


def load_existing_ascents(session, user_id):
    """Load existing ascents for a user into memory."""
    return {
        (a.route_id, a.date): a for a in
        session.query(Ascent).filter(Ascent.user_id == user_id).all()
    }

def load_existing_routes(session, route_names=None):
    """Load existing routes into memory, optionally filtered by name."""
    query = session.query(Route)
    if route_names:
        query = query.filter(Route.name.in_(route_names))
    return {(r.name, r.crag_id, r.discipline): r for r in query.all()}

def load_existing_countries(session, country_names=None):
    query = session.query(Country)
    if country_names:
        query = query.filter(Country.name.in_(country_names))
    return {c.name: c for c in query.all()}

def load_existing_areas(session, area_names=None):
    query = session.query(Area)
    if area_names:
        query = query.filter(Area.name.in_(area_names))
    return {a.name: a for a in query.all()}

def load_existing_crags(session, crag_names=None):
    query = session.query(Crag)
    if crag_names:
        query = query.filter(Crag.name.in_(crag_names))
    return {c.name: c for c in query.all()}

