"""
Find and remove duplicates from database.

Run as:
    python3 -m climbingdb.scripts.cleanup --dry-run
    python3 -m climbingdb.scripts.cleanup
"""

import argparse
from collections import defaultdict

from climbingdb.models import SessionLocal, Route, Country, Area, Crag, Ascent, User


# ---------------------------------------------------------------------------
# Generic duplicate finder
# ---------------------------------------------------------------------------

def _find_duplicates(session, model, key_fn):
    """
    Generic duplicate finder for any model.

    Args:
        session: SQLAlchemy session
        model: SQLAlchemy model class
        key_fn: Function that extracts the grouping key from an object

    Returns:
        dict: {key: [list of objects]} - only includes groups with duplicates
    """
    all_objects = session.query(model).all()

    grouped = defaultdict(list)
    for obj in all_objects:
        grouped[key_fn(obj)].append(obj)

    return {key: objs for key, objs in grouped.items() if len(objs) > 1}


def find_duplicate_countries(session):
    """Find countries with the same name."""
    return _find_duplicates(session, Country, key_fn=lambda c: c.name)


def find_duplicate_areas(session):
    """Find areas with the same name and country_id."""
    return _find_duplicates(session, Area, key_fn=lambda a: (a.name, a.country_id))


def find_duplicate_crags(session):
    """Find crags with the same name and area_id."""
    return _find_duplicates(session, Crag, key_fn=lambda c: (c.name, c.area_id))


def find_duplicate_routes(session):
    return _find_duplicates(session, Route, key_fn=lambda r: (r.name, r.crag_id, r.discipline))


def find_duplicate_ascents(session):
    return _find_duplicates(session, Ascent, key_fn=lambda a: (a.user_id, a.route_id))


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------

def _get_ascent_stats_for_routes(session, route_ids):
    if not route_ids:
        return 0, 0

    ascents = session.query(Ascent).filter(
        Ascent.route_id.in_(route_ids)
    ).all()

    ascent_count = len(ascents)

    usernames = [
        u.username for u in
        session.query(User).join(Ascent).filter(
            Ascent.route_id.in_(route_ids)
        ).distinct().all()
    ] if route_ids else []

    return ascent_count, usernames


def _get_route_ids_for_crags(session, crag_ids):
    """Get all route IDs for a list of crag IDs."""
    return [
        r.id for r in
        session.query(Route.id).filter(Route.crag_id.in_(crag_ids)).all()
    ]


def _get_crag_ids_for_areas(session, area_ids):
    """Get all crag IDs for a list of area IDs."""
    return [
        c.id for c in
        session.query(Crag.id).filter(Crag.area_id.in_(area_ids)).all()
    ]


def _get_area_ids_for_countries(session, country_ids):
    """Get all area IDs for a list of country IDs."""
    return [
        a.id for a in
        session.query(Area.id).filter(Area.country_id.in_(country_ids)).all()
    ]


# ---------------------------------------------------------------------------
# Generic print function
# ---------------------------------------------------------------------------

def _print_duplicates(duplicates, label, format_header_fn, format_item_fn):
    """
    Generic duplicate printer.

    Args:
        duplicates: dict from find_duplicate_X()
        label: String label e.g. "countries", "areas", "crags"
        format_header_fn: fn(key) → header string
        format_item_fn: fn(obj) → item string
    """
    if not duplicates:
        print(f"✅ No duplicate {label} found!")
        return

    print(f"\n{'=' * 70}")
    print(f"Found {len(duplicates)} duplicate {label} groups:")
    print(f"{'=' * 70}\n")

    total_duplicates = 0
    for key, objects in sorted(duplicates.items(), key=lambda x: str(x[0])):
        print(format_header_fn(key, objects))
        for obj in objects:
            print(f"  {format_item_fn(obj)}")
        total_duplicates += len(objects) - 1
        print()

    print(f"Total duplicate {label} to remove: {total_duplicates}")


def print_duplicate_countries(duplicates, session):
    """Print duplicate countries with ascent and user stats."""

    def format_header(key, objects):
        country_ids = [o.id for o in objects]
        area_ids = _get_area_ids_for_countries(session, country_ids)
        crag_ids = _get_crag_ids_for_areas(session, area_ids)
        route_ids = _get_route_ids_for_crags(session, crag_ids)
        ascent_count, usernames = _get_ascent_stats_for_routes(session, route_ids)

        return (f"Country: '{key}' | "
                f"Areas: {len(area_ids)} | "
                f"Crags: {len(crag_ids)} | "
                f"Ascents: {ascent_count} | "
                f"Users: {', '.join(usernames) if usernames else 'none'}")

    def format_item(country):
        area_ids = _get_area_ids_for_countries(session, [country.id])
        crag_ids = _get_crag_ids_for_areas(session, area_ids)
        route_ids = _get_route_ids_for_crags(session, crag_ids)
        ascent_count, usernames = _get_ascent_stats_for_routes(session, route_ids)

        return (f"ID: {country.id:6} | "
                f"Areas: {len(area_ids):3} | "
                f"Crags: {len(crag_ids):3} | "
                f"Ascents: {ascent_count:4} | "
                f"Users: {', '.join(usernames) if usernames else 'none'}")

    _print_duplicates(duplicates, "countries", format_header, format_item)


def print_duplicate_areas(duplicates, session):
    """Print duplicate areas with ascent and user stats."""

    def format_header(key, objects):
        area_name, country_id = key
        country = session.query(Country).filter(Country.id == country_id).first()
        area_ids = [o.id for o in objects]
        crag_ids = _get_crag_ids_for_areas(session, area_ids)
        route_ids = _get_route_ids_for_crags(session, crag_ids)
        ascent_count, usernames = _get_ascent_stats_for_routes(session, route_ids)

        return (f"Area: '{area_name}' | "
                f"Country: {country.name if country else 'Unknown'} | "
                f"Crags: {len(crag_ids)} | "
                f"Ascents: {ascent_count} | "
                f"Users: {', '.join(usernames) if usernames else 'none'}")

    def format_item(area):
        crag_ids = _get_crag_ids_for_areas(session, [area.id])
        route_ids = _get_route_ids_for_crags(session, crag_ids)
        ascent_count, usernames = _get_ascent_stats_for_routes(session, route_ids)

        return (f"ID: {area.id:6} | "
                f"Crags: {len(crag_ids):3} | "
                f"Ascents: {ascent_count:4} | "
                f"Users: {', '.join(usernames) if usernames else 'none'}")

    _print_duplicates(duplicates, "areas", format_header, format_item)


def print_duplicate_crags(duplicates, session):
    """Print duplicate crags with ascent and user stats."""

    def format_header(key, objects):
        crag_name, area_id = key
        area = session.query(Area).filter(Area.id == area_id).first()
        crag_ids = [o.id for o in objects]
        route_ids = _get_route_ids_for_crags(session, crag_ids)
        ascent_count, usernames = _get_ascent_stats_for_routes(session, route_ids)

        return (f"Crag: '{crag_name}' | "
                f"Area: {area.name if area else 'Unknown'} | "
                f"Routes: {len(route_ids)} | "
                f"Ascents: {ascent_count} | "
                f"Users: {', '.join(usernames) if usernames else 'none'}")

    def format_item(crag):
        route_ids = _get_route_ids_for_crags(session, [crag.id])
        ascent_count, usernames = _get_ascent_stats_for_routes(session, route_ids)

        return (f"ID: {crag.id:6} | "
                f"Routes: {len(route_ids):4} | "
                f"Ascents: {ascent_count:4} | "
                f"Users: {', '.join(usernames) if usernames else 'none'}")

    _print_duplicates(duplicates, "crags", format_header, format_item)


def print_duplicate_routes(duplicates, session):
    """Print duplicate routes with crag, area and user info."""
    def format_header(key, objects):
        name, crag_id, discipline = key
        crag = session.query(Crag).filter(Crag.id == crag_id).first()
        area = crag.area.name if crag and crag.area else "Unknown"
        crag_name = crag.name if crag else "Unknown"
        route_ids = [o.id for o in objects]
        ascent_count, usernames = _get_ascent_stats_for_routes(session, route_ids)

        return (f"Route: '{name}' [{discipline}] | "
                f"Crag: {crag_name} ({area}) | "
                f"Ascents: {ascent_count} | "
                f"Users: {', '.join(usernames) if usernames else 'none'}")

    def format_item(route):
        ascent_count, usernames = _get_ascent_stats_for_routes(session, [route.id])

        return (f"ID: {route.id:6} | "
                f"Grade: {route.consensus_grade or 'N/A':8} | "
                f"Ascents: {ascent_count:3} | "
                f"Users: {', '.join(usernames) if usernames else 'none'}")

    _print_duplicates(duplicates, "routes", format_header, format_item)


def print_duplicate_ascents(duplicates, session):
    """Print duplicate ascents with route, crag and user info."""
    def format_header(key, objects):
        user_id, route_id = key
        user = session.query(User).filter(User.id == user_id).first()
        route = session.query(Route).filter(Route.id == route_id).first()
        crag = route.crag if route else None
        area = crag.area.name if crag and crag.area else "Unknown"

        return (f"User: {user.username if user else 'Unknown'} | "
                f"Route: '{route.name if route else 'Unknown'}' "
                f"[{route.discipline if route else 'Unknown'}] | "
                f"Crag: {crag.name if crag else 'Unknown'} ({area})")

    def format_item(ascent):
        return (f"ID: {ascent.id:6} | "
                f"Grade: {ascent.grade or 'N/A':8} | "
                f"Date: {ascent.date} | "
                f"Style: {ascent.style or 'N/A':6} | "
                f"Stars: {ascent.stars}")

    _print_duplicates(duplicates, "ascents", format_header, format_item)


def cleanup_empty_crags(session, dry_run=True):
    all_crags = session.query(Crag).order_by(Crag.name).all()

    empty_crags = []
    for crag in all_crags:
        print("Getting info of crag: ", crag.name)
        route_ids = _get_route_ids_for_crags(session, [crag.id])
        ascent_count, _ = _get_ascent_stats_for_routes(session, route_ids)
        if ascent_count == 0:
            empty_crags.append((crag, len(route_ids)))

    print(f"\n{'=' * 70}")
    print(f"Found {len(empty_crags)} crags with zero ascents:")
    print(f"{'=' * 70}\n")

    if not empty_crags:
        print(" No empty crags found!")
        return 0

    total_routes = sum(route_count for _, route_count in empty_crags)

    for crag, route_count in sorted(empty_crags, key=lambda x: x[0].id):
        area = crag.area.name if crag.area else "Unknown"
        print(f"  ID: {crag.id:6} | "
              f"Crag: {crag.name:30} | "
              f"Area: {area:20} | "
              f"Routes: {route_count}")

    print(f"\nTotal crags to remove: {len(empty_crags)}")
    print(f"Total routes to remove: {total_routes}")

    if dry_run:
        print("\n[DRY RUN] No changes made.")
        return 0

    response = input("\nProceed with cleanup? (yes/no): ")
    if response.lower() != 'yes':
        print("Cleanup cancelled.")
        return 0

    removed_crags = 0
    removed_routes = 0

    for crag, route_count in empty_crags:
        print("Removing crag: ", crag.name)
        # Delete routes first (cascade handles ascents/pitches)
        route_ids = _get_route_ids_for_crags(session, [crag.id])
        session.query(Route).filter(Route.id.in_(route_ids)).delete(
            synchronize_session=False
        )
        session.delete(crag)
        removed_crags += 1
        removed_routes += route_count

    session.commit()
    print(f"\n Removed {removed_crags} crags and {removed_routes} routes")
    return removed_crags


def main():
    parser = argparse.ArgumentParser(description='Find and remove duplicates')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    session = SessionLocal()

    try:
        #print_duplicate_countries(find_duplicate_countries(session), session)
        #print_duplicate_areas(find_duplicate_areas(session), session)
        print_duplicate_crags(find_duplicate_crags(session), session)
        print_duplicate_routes(find_duplicate_routes(session), session)
        #print_duplicate_ascents(find_duplicate_ascents(session), session)
        #cleanup_empty_crags(session, dry_run=args.dry_run)

    except Exception as e:
        print(f"\n Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()