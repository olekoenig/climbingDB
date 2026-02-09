"""
Import climbing data from CSV files into SQLAlchemy database.

Run as:
    python3 -m climbingdb.scripts.import_csv
"""

import pandas as pd
from datetime import datetime
from climbingdb.models import SessionLocal, init_db, drop_all
from climbingdb.models import Country, Area, Crag, Route
from climbingdb.config import ROUTES_CSV_FILE, BOULDERS_CSV_FILE, MULTIPITCHES_CSV_FILE
from ..grade import Grade


def parse_multipitch_pitches(pitches_str):
    if not pitches_str or pitches_str == "":
        return None

    pitches = pitches_str.split(",")
    result = []

    for pitch in pitches:
        pitch = pitch.strip()

        # Check if in parentheses (followed)
        if pitch.startswith("(") and pitch.endswith(")"):
            grade = pitch.strip("()")
            led = False
        else:
            grade = pitch
            led = True

        result.append({
            "grade": grade,
            "led": led,
            "pitch_length": None,
            "pitch_name": None
        })

    return result


def get_or_create_country(session, country_name):
    """Get existing country or create new one."""
    if not country_name or country_name == "":
        return None

    country = session.query(Country).filter(Country.name == country_name).first()
    if not country:
        country = Country(name=country_name)
        session.add(country)
        session.flush()  # Get the ID without committing
        print(f"  Created country: {country_name}")
    return country


def get_or_create_area(session, area_name, country):
    """Get existing area or create new one."""
    if not area_name or area_name == "":
        return None

    # Query by name and country_id to allow same area name in different countries
    query = session.query(Area).filter(Area.name == area_name)
    if country:
        query = query.filter(Area.country_id == country.id)

    area = query.first()
    if not area:
        area = Area(name=area_name, country=country)
        session.add(area)
        session.flush()
        location = f"{area_name}, {country.name}" if country else area_name
        print(f"  Created area: {location}")
    return area


def get_or_create_crag(session, crag_name, area):
    """Get existing crag or create new one."""
    if not crag_name or crag_name == "":
        # Create a default crag if none specified
        crag_name = "Unknown"

    # Query by name and area_id
    query = session.query(Crag).filter(Crag.name == crag_name)
    if area:
        query = query.filter(Crag.area_id == area.id)

    crag = query.first()
    if not crag:
        if not area:
            # Need to create a default area
            area = get_or_create_area(session, "Unknown", None)
        crag = Crag(name=crag_name, area=area)
        session.add(crag)
        session.flush()
        print(f"  Created crag: {crag_name}")
    return crag


def import_routes_from_csv(csv_file, discipline, session):
    """
    Import routes from a single CSV file.

    Args:
        csv_file: Path to CSV file
        discipline: "Sportclimb", "Boulder", or "Multipitch"
        session: SQLAlchemy session

    Returns:
        Number of routes imported
    """
    print(f"\nImporting {discipline} routes from {csv_file}...")

    # Read CSV
    df = pd.read_csv(
        csv_file,
        sep=';',
        header=0,
        encoding='utf-8',
        parse_dates=["date"],
        keep_default_na=False
    )

    print(f"  Found {len(df)} routes in CSV")

    df['date'] = pd.to_datetime(df['date'], format='mixed').dt.strftime('%Y-%m-%d')

    imported_count = 0
    skipped_count = 0

    for idx, row in df.iterrows():
        try:
            # Get or create location hierarchy
            country = get_or_create_country(session, row.get('country', ''))
            area = get_or_create_area(session, row.get('area', ''), country)
            crag = get_or_create_crag(session, row.get('crag', ''), area)

            is_project = row.get('project', '') == 'X'
            is_milestone = row.get('milestone', '') == 'X'

            # Parse date
            route_date = None
            if pd.notna(row.get('date')):
                if isinstance(row['date'], str):
                    try:
                        route_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    except:
                        pass
                else:
                    route_date = row['date'].date() if hasattr(row['date'], 'date') else row['date']

            # Parse stars
            stars = 0
            if row.get('stars', '') != '':
                try:
                    stars = int(row['stars'])
                except:
                    stars = 0

            # Handle multipitch-specific fields
            pitches = None
            ernsthaftigkeit = None
            length = None
            if discipline == "Multipitch":
                pitches_str = row.get('pitches', '')
                pitches = parse_multipitch_pitches(pitches_str)
                ernsthaftigkeit = row.get('ernsthaftigkeit', '') or None
                length = row.get('length', '') or None

            route = Route(
                name=row['name'],
                grade=row['grade'],
                crag=crag,
                discipline=discipline,
                style=row.get('style', '') or None,
                date=route_date,
                stars=stars,
                shortnote=row.get('shortnote', '') or None,
                notes=row.get('notes', '') or None,
                is_project=is_project,
                is_milestone=is_milestone,
                ernsthaftigkeit=ernsthaftigkeit,
                pitches=pitches,
                length=length,
                gear=row.get('gear', None),  # If column exists in CSV
                ascent_time=row.get('ascent_time', None),
                pitch_number=len(pitches) if pitches else None  # Auto-calculate
            )

            # Override ole_grade for sport-graded boulders (keep original grade visible)
            if discipline == "Boulder" and Grade(row['grade']).get_scale() in ['YDS', 'UIAA', 'French', 'Elbsandstein']:
                route.ole_grade = 0  # Easy boulder (5.9 or so, set to 0 for proper sorting/filtering)

            session.add(route)
            imported_count += 1

            # Commit every 100 routes to avoid memory issues
            if imported_count % 100 == 0:
                session.commit()
                print(f"  Imported {imported_count} routes...")

        except Exception as e:
            print(f"\tError importing route '{row.get('name', 'unknown')}': {e}")
            skipped_count += 1
            continue

    # Final commit
    session.commit()
    print(f"\tImported {imported_count} routes")
    if skipped_count > 0:
        print(f"\tSkipped {skipped_count} routes due to errors")

    return imported_count


def import_all_csv_files(recreate_db=True):
    """
    Import all CSV files into the database.

    Args:
        recreate_db: If True, drops and recreates all tables (loses existing data!)
    """
    print("=" * 60)
    print("CSV Import Script")
    print("=" * 60)

    # Set up database
    if recreate_db:
        print("\nWARNING: Dropping all existing tables and data!")
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Import cancelled.")
            return
        drop_all()
        init_db()
    else:
        init_db()  # Just ensure tables exist

    session = SessionLocal()

    try:
        # Import each discipline
        total = 0
        total += import_routes_from_csv(ROUTES_CSV_FILE, "Sportclimb", session)
        total += import_routes_from_csv(BOULDERS_CSV_FILE, "Boulder", session)
        total += import_routes_from_csv(MULTIPITCHES_CSV_FILE, "Multipitch", session)

        # Print summary
        print("\n" + "=" * 60)
        print("Import Summary")
        print("=" * 60)

        countries = session.query(Country).count()
        areas = session.query(Area).count()
        crags = session.query(Crag).count()
        routes = session.query(Route).count()
        projects = session.query(Route).filter(Route.is_project == True).count()
        milestones = session.query(Route).filter(Route.is_milestone == True).count()

        print(f"Countries:  {countries}")
        print(f"Areas:      {areas}")
        print(f"Crags:      {crags}")
        print(f"Routes:     {routes}")
        print(f"  - Sport:  {session.query(Route).filter(Route.discipline == 'Sportclimb').count()}")
        print(f"  - Boulder: {session.query(Route).filter(Route.discipline == 'Boulder').count()}")
        print(f"  - Multi:   {session.query(Route).filter(Route.discipline == 'Multipitch').count()}")
        print(f"Projects:   {projects}")
        print(f"Milestones:   {milestones}")

        print("\nImport completed successfully!")
        print(f"Database file: climbing.db")

    except Exception as e:
        print(f"\nError during import: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def verify_import():
    """Quick verification of imported data."""
    print("\n" + "=" * 60)
    print("Verification")
    print("=" * 60)

    session = SessionLocal()

    try:
        # Show some sample data
        print("\nSample routes:")
        routes = session.query(Route).order_by(Route.ole_grade.desc()).limit(5).all()
        for route in routes:
            print(f"  {route.grade:6} - {route.name:30} ({route.discipline}) - {route.full_location}")

        print("\nSample areas:")
        areas = session.query(Area).limit(5).all()
        for area in areas:
            route_count = len(area.crags[0].routes) if area.crags else 0
            print(f"  {area.full_location:40} - {len(area.crags)} crags")

    finally:
        session.close()


if __name__ == "__main__":
    import_all_csv_files(recreate_db=True)
    verify_import()