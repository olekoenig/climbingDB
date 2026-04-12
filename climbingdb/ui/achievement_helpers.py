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