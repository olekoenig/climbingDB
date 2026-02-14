"""
Import climbing data from CSV files into SQLAlchemy database.

Run as:
    python3 -m climbingdb.scripts.csv_to_sqlalchemy
"""

import pandas as pd
from sqlalchemy import text
import getpass
from datetime import datetime
import bcrypt

from climbingdb.models import SessionLocal, init_db, drop_all
from climbingdb.models import Country, Area, Crag, Route, User, Pitch
from climbingdb.config import ROUTES_CSV_FILE, BOULDERS_CSV_FILE, MULTIPITCHES_CSV_FILE
from climbingdb.grade import Grade


def _create_performance_indexes():
    """Create database indexes for query performance."""
    session = SessionLocal()

    indexes = [
        "CREATE INDEX IF NOT EXISTS ix_crags_area_id ON crags(area_id);",
        "CREATE INDEX IF NOT EXISTS ix_areas_country_id ON areas(country_id);",
        "CREATE INDEX IF NOT EXISTS ix_routes_discipline ON routes(discipline);",
        "CREATE INDEX IF NOT EXISTS ix_routes_ole_grade ON routes(ole_grade);",
        "CREATE INDEX IF NOT EXISTS ix_routes_is_project ON routes(is_project);",
        "CREATE INDEX IF NOT EXISTS ix_routes_crag_id ON routes(crag_id);",
        "CREATE INDEX IF NOT EXISTS ix_routes_user_id ON routes(user_id);",
        "CREATE INDEX IF NOT EXISTS ix_pitches_route_id ON pitches(route_id);",
    ]

    for idx_sql in indexes:
        try:
            session.execute(text(idx_sql))
            print(f"  ✓ {idx_sql.split('INDEX')[1].split('ON')[0].strip()}")
        except Exception as e:
            print(f"  ⚠️ Error: {e}")

    session.commit()
    session.close()
    print("✓ Indexes created")


def parse_multipitch_pitches(pitches_str):
    """Parse comma-separated pitch grades. Parentheses indicate followed pitch."""
    if not pitches_str:
        return None

    result = []
    for pitch in pitches_str.split(","):
        pitch = pitch.strip()

        if pitch.startswith("(") and pitch.endswith(")"):
            result.append({"grade": pitch.strip("()"), "led": False})
        else:
            result.append({"grade": pitch, "led": True})

    return result


def get_or_create_country(session, country_name):
    """Get existing country or create new one."""
    if not country_name:
        raise ValueError("Country is required")

    country = session.query(Country).filter(Country.name == country_name).first()
    if not country:
        country = Country(name=country_name)
        session.add(country)
        session.flush()
        print(f"  Created country: {country_name}")

    return country


def get_or_create_area(session, area_name, country):
    """Get existing area or create new one."""
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
        print(f"  Created area: {area_name}, {country.name}")

    return area


def get_or_create_crag(session, crag_name, area):
    """Get existing crag or create new one."""
    if not crag_name:
        raise ValueError("Crag is required")

    query = session.query(Crag).filter(Crag.name == crag_name, Crag.area_id == area.id)

    crag = query.first()
    if not crag:
        crag = Crag(name=crag_name, area=area)
        session.add(crag)
        session.flush()
        print(f"  Created crag: {crag_name}")

    return crag


def create_pitches_from_data(session, route, pitch_data):
    """Create Pitch objects for a multipitch route."""
    if not pitch_data:
        return

    for i, pitch_info in enumerate(pitch_data):
        pitch = Pitch(
            route=route,
            pitch_number=i + 1,
            grade=pitch_info['grade'],
            led=pitch_info['led'],
            style=None,
            stars=0,
            shortnote=None,
            notes=None,
            gear=None,
            ernsthaftigkeit=None,
            pitch_length=None,
            pitch_name=None
        )
        session.add(pitch)


def import_routes_from_csv(csv_file, discipline, session, user_id):
    """Import routes from CSV file."""
    print(f"\nImporting {discipline} routes from {csv_file}...")

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
            country = get_or_create_country(session, row['country'])
            area = get_or_create_area(session, row['area'], country)
            crag = get_or_create_crag(session, row['crag'], area)

            is_project = row['project'] == 'X' if row['project'] else False
            is_milestone = row['milestone'] == 'X' if 'milestone' in row and row['milestone'] else False

            route_date = None
            if pd.notna(row['date']):
                if isinstance(row['date'], str):
                    try:
                        route_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    except:
                        pass
                else:
                    route_date = row['date'].date() if hasattr(row['date'], 'date') else row['date']

            stars = int(row['stars']) if row['stars'] != '' else 0

            style = row['style'] if row['style'] else None
            shortnote = row['shortnote'] if row['shortnote'] else None
            notes = row['notes'] if row['notes'] else None
            gear = row['gear'] if 'gear' in row and row['gear'] else None

            grade_str = row['grade']
            if discipline == "Boulder":
                grade_scale = Grade(grade_str).get_scale()
                if grade_scale in ['YDS', 'UIAA', 'French', 'Elbsandstein']:
                    grade_str = "VB"

            pitch_data = None
            ernsthaftigkeit = None
            length = None
            pitch_number = 1

            if discipline == "Multipitch":
                pitches_str = row['pitches'] if row['pitches'] else None
                pitch_data = parse_multipitch_pitches(pitches_str)
                pitch_number = len(pitch_data)
                ernsthaftigkeit = row['ernsthaftigkeit'] if row['ernsthaftigkeit'] else None
                length = float(row['length']) if row['length'] else None

            route = Route(
                user_id=user_id,
                name=row['name'],
                grade=grade_str,
                crag=crag,
                discipline=discipline,
                style=style,
                date=route_date,
                stars=stars,
                shortnote=shortnote,
                notes=notes,
                gear=gear,
                is_project=is_project,
                is_milestone=is_milestone,
                ernsthaftigkeit=ernsthaftigkeit,
                ascent_time=None,
                pitch_number=pitch_number,
                length=length,
                latitude=None,
                longitude=None
            )

            session.add(route)
            session.flush()

            if discipline == "Multipitch" and pitch_data:
                create_pitches_from_data(session, route, pitch_data)

            imported_count += 1

            if imported_count % 100 == 0:
                session.commit()
                print(f"  Imported {imported_count} routes...")

        except Exception as e:
            print(f"  ⚠️ Error importing '{row.get('name', 'unknown')}': {e}")
            skipped_count += 1
            session.rollback()
            continue

    session.commit()
    print(f"  ✓ Imported {imported_count} routes")
    if skipped_count > 0:
        print(f"  ⚠️ Skipped {skipped_count} routes")

    return imported_count


def _create_default_user(session, username, email, password):
    """Create default user for imported routes."""
    existing_user = session.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"  ⚠️ User '{username}' already exists")
        use_existing = input(f"  Use existing user? (yes/no): ")
        if use_existing.lower() == 'yes':
            return existing_user
        raise ValueError("User already exists")

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )

    session.add(user)
    session.commit()

    return user


def import_all_csv_files(recreate_db=True):
    """Import all CSV files into database."""
    print("=" * 60)
    print("CSV Import Script")
    print("=" * 60)

    if recreate_db:
        print("\n⚠️ WARNING: Dropping all existing tables and data!")
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Import cancelled.")
            return
        drop_all()
        init_db()
        print("\n✓ Tables created")

        print("\nCreating indexes...")
        _create_performance_indexes()
    else:
        init_db()

    session = SessionLocal()

    try:
        print("\n" + "=" * 60)
        print("Create Default User")
        print("=" * 60)
        print("This user will own all imported routes.\n")

        default_username = input("Username: ").strip()
        default_email = input("Email: ").strip()

        default_password = getpass.getpass("Password: ")
        confirm_password = getpass.getpass("Confirm password: ")

        if default_password != confirm_password:
            print("❌ Passwords don't match!")
            return

        if len(default_password) < 8:
            print("❌ Password must be at least 8 characters!")
            return

        print(f"\nCreating user: {default_username}")
        default_user = _create_default_user(session, default_username, default_email, default_password)
        print(f"✓ User created with ID: {default_user.id}")

        total = 0
        total += import_routes_from_csv(ROUTES_CSV_FILE, "Sportclimb", session, default_user.id)
        total += import_routes_from_csv(BOULDERS_CSV_FILE, "Boulder", session, default_user.id)
        total += import_routes_from_csv(MULTIPITCHES_CSV_FILE, "Multipitch", session, default_user.id)

        print("\n" + "=" * 60)
        print("Import Summary")
        print("=" * 60)

        print(f"Countries:  {session.query(Country).count()}")
        print(f"Areas:      {session.query(Area).count()}")
        print(f"Crags:      {session.query(Crag).count()}")
        print(f"Routes:     {session.query(Route).count()}")
        print(f"  - Sport:  {session.query(Route).filter(Route.discipline == 'Sportclimb').count()}")
        print(f"  - Boulder: {session.query(Route).filter(Route.discipline == 'Boulder').count()}")
        print(f"  - Multi:   {session.query(Route).filter(Route.discipline == 'Multipitch').count()}")
        print(f"Pitches:    {session.query(Pitch).count()}")
        print(f"Projects:   {session.query(Route).filter(Route.is_project == True).count()}")
        print(f"Milestones: {session.query(Route).filter(Route.is_milestone == True).count()}")

        print(f"\n✓ All routes assigned to user: {default_user.username}")
        print("✅ Import completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import_all_csv_files(recreate_db=True)