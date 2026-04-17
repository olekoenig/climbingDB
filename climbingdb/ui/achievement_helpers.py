from sqlalchemy import func

from climbingdb.models import Ascent, Route, Area, Crag


def get_max_daily_length(db):
    ascents = db.session.query(
        Ascent.date,
        Route.length,
        Ascent.ascent_time
    ).join(Ascent.route).filter(
        Ascent.user_id == db.user_id,
        Route.discipline == "Multipitch",
        Ascent.is_project == False,
        Route.length != None,
        Ascent.date != None
    ).all()

    if not ascents:
        return 0

    # Group by date, summing normalized lengths
    daily_lengths = {}
    for ascent_date, length, ascent_time in ascents:
        if ascent_time and ascent_time > 24:
            # Normalize: how much was climbed in one day
            normalized_length = length / (ascent_time / 24)
        else:
            # Ascent <= 24h or no time recorded: use full length
            normalized_length = length

        # Sum length of potential other route that was climbed on that day.
        # This can happen if the user did a link-up, i.e., climbing multiple multipitches in one day.
        daily_lengths[ascent_date] = daily_lengths.get(ascent_date, 0) + normalized_length

    return max(daily_lengths.values()) if daily_lengths else 0


def get_max_boulders_in_area(db):
    """Get maximum number of boulders climbed in a single area."""
    result = db.session.query(
        Area.name,
        func.count(Ascent.id).label('boulder_count')
    ).join(Ascent.route).join(Route.crag).join(Crag.area).filter(
        Ascent.user_id == db.user_id,
        Route.discipline == "Boulder",
        Ascent.is_project == False
    ).group_by(
        Area.name
    ).order_by(
        func.count(Ascent.id).desc()
    ).first()

    return result.boulder_count if result else 0


def get_max_daily_v_points(db):
    # Get all boulder ascents with dates
    ascents = db.session.query(
        Ascent.date,
        Ascent.ole_grade
    ).join(Ascent.route).filter(
        Ascent.user_id == db.user_id,
        Route.discipline == "Boulder",
        Ascent.is_project == False,
        Ascent.date != None
    ).all()

    if not ascents:
        return 0

    # Group by date and sum V-points
    # ole_grade for boulders maps directly to V-grade number
    daily_points = {}
    for ascent_date, ole_grade in ascents:
        if ole_grade and ole_grade > 0:
            daily_points[ascent_date] = daily_points.get(ascent_date, 0) + int(ole_grade)

    return max(daily_points.values()) if daily_points else 0


def _test_ascent_badge(db, route_properties):
    for route_name, crag_name, area_name in route_properties:
        ascent = db.session.query(Ascent).join(Ascent.route).join(Route.crag).join(Crag.area).filter(
            Ascent.user_id == db.user_id,
            Ascent.is_project == False,
            Route.name == route_name,
            Crag.name == crag_name,
            Area.name == area_name

        ).first()
        if not ascent:
            return False
    return True


def has_font_big_5(db):
    font_big_5 = [
        ("Big Boss", "Cuvier Rempart", "Fontainebleau"),
        ("Fourmis Rouge", "Cuvier Rempart", "Fontainebleau"),
        ("Tristesse", "Cuvier Rempart", "Fontainebleau"),
        ("Big Golden", "Cuvier Rempart", "Fontainebleau"),
        ("Atrésie", "Cuvier Rempart", "Fontainebleau"),
    ]
    return _test_ascent_badge(db, font_big_5)


def has_alpine_triology(db):
    alpine_triology = [
        ("Des Kaisers neue Kleider", "Fleischbankpfeiler", "Wilder Kaiser"),
        ("Silbergeier", "Vierte Kirchlispitze", "Rätikon"),
        ("End of Silence", "Feuerhorn", "Berchtesgadener Alpen")
    ]
    return _test_ascent_badge(db, alpine_triology)


def is_local(db):
    """Check if user has climbed on 100+ distinct days in one area."""
    result = db.session.query(
        Area.name,
        func.count(func.distinct(Ascent.date)).label('days')
    ).join(Ascent.route)\
     .join(Route.crag)\
     .join(Crag.area)\
     .filter(
        Ascent.user_id == db.user_id,
        Ascent.is_project == False,
        Ascent.date != None
    ).group_by(Area.name)\
     .order_by(func.count(func.distinct(Ascent.date)).desc())\
     .first()
    return result.days >= 100 if result else False


def is_bleaussard(db):
    """Check if user has climbed 100+ boulders in Fontainebleau."""
    count = db.session.query(Ascent)\
        .join(Ascent.route)\
        .join(Route.crag)\
        .join(Crag.area)\
        .filter(
            Ascent.user_id == db.user_id,
            Ascent.is_project == False,
            Route.discipline == "Boulder",
            Area.name == "Fontainebleau"
        ).count()
    return count >= 100


def is_epicing(db):
    ascent = db.session.query(Ascent).join(Ascent.route).filter(
        Ascent.user_id == db.user_id,
        Ascent.is_project == False,
        Route.discipline == "Multipitch",
        Ascent.ascent_time > 15
    ).first()
    return ascent is not None


def is_sandbagger(db):
    count = db.session.query(Ascent).join(Ascent.route).filter(
        Ascent.user_id == db.user_id,
        Ascent.is_project == False,
        Ascent.ole_grade != None,
        Route.consensus_ole_grade != None,
        Ascent.ole_grade < Route.consensus_ole_grade
    ).count()
    return count >= 3


def is_grade_inflator(db):
    count = db.session.query(Ascent).join(Ascent.route).filter(
        Ascent.user_id == db.user_id,
        Ascent.is_project == False,
        Ascent.ole_grade != None,
        Route.consensus_ole_grade != None,
        Ascent.ole_grade > Route.consensus_ole_grade
    ).count()
    return count >= 3