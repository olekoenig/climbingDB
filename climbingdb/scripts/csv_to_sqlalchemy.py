"""
Import climbing data from CSV files into SQLAlchemy database.

Run as:
    python3 -m climbingdb.scripts.csv_to_sqlalchemy
"""

import pandas as pd
import getpass
from datetime import datetime

from climbingdb.services.auth_service import AuthService
from climbingdb.models import SessionLocal, init_db, drop_all
from climbingdb.models import Country, Area, Crag, Route, User, Pitch, Ascent, PitchAscent
from climbingdb.config import ROUTES_CSV_FILE, BOULDERS_CSV_FILE, MULTIPITCHES_CSV_FILE
from climbingdb.grade import Grade
from climbingdb.services.crud import (
    get_or_create_location,
    get_or_create_route,
    create_ascent,
    create_pitches_and_ascents
)


def _parse_multipitch_pitches(pitches_str):
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


def _get_route_fields(row, discipline):
    routename = row['name']
    crag = row['crag']
    area = row['area']
    country = row['country']
    grade = row['grade']

    # Catch cases where boulders have a route grade (e.g., 5.9 for a tall boulder), set grade to "VB"
    if discipline == "Boulder":
        grade_scale = Grade(grade).get_scale()
        if grade_scale in ['YDS', 'UIAA', 'French', 'Elbsandstein']:
            grade = "VB"

    # Fields that are only in multipitch table
    length = float(getattr(row, 'length', 0))
    ernsthaftigkeit = getattr(row, 'ernsthaftigkeit', None)

    return routename, crag, area, country, grade, length, ernsthaftigkeit


def _get_ascent_fields(row):
    # Re-scale stars from 1-3 to 1-5
    stars = round(float(row['stars'])*5/2.85) if row['stars'] != '' else 0
    style = row['style'] if row['style'] else None
    shortnote = row['shortnote'] if row['shortnote'] else None
    notes = row['notes'] if row['notes'] else None
    is_project = row['project'] == 'X' if row['project'] else False
    is_milestone = row['milestone'] == 'X' if 'milestone' in row and row['milestone'] else False

    ascent_date = None
    if pd.notna(row['date']):
        if isinstance(row['date'], str):
            try:
                ascent_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
            except:
                pass
        else:
            ascent_date = row['date'].date() if hasattr(row['date'], 'date') else row['date']

    return stars, style, shortnote, notes, is_project, is_milestone, ascent_date


def _create_default_user(session, username, email, password):
    """Create default user via AuthService."""
    auth = AuthService()

    success, message, user = auth.create_user(
        username=username,
        password=password,
        email=email
    )

    if not success:
        raise ValueError(message)

    print(f"  SUCCESS: {message} (ID: {user.id})")
    return user


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

    # Hack to parse date formats properly, not sure if this is needed
    df['date'] = pd.to_datetime(df['date'], format='mixed').dt.strftime('%Y-%m-%d')

    imported_count = 0
    skipped_count = 0

    for idx, row in df.iterrows():
        try:
            route_name, crag_name, area_name, country_name, grade, length, ernsthaftigkeit = _get_route_fields(row, discipline)

            crag = get_or_create_location(session, country_name, area_name, crag_name, verbose=True)
            route = get_or_create_route(session, route_name, discipline, crag, grade,
                                        length=length, ernsthaftigkeit=ernsthaftigkeit,
                                        verbose=True)

            stars, style, shortnote, notes, is_project, is_milestone, ascent_date = _get_ascent_fields(row)

            ascent = create_ascent(
                session,
                user_id=user_id,
                route=route,
                grade=grade,
                style=style,
                date=ascent_date,
                stars=stars,
                shortnote=shortnote,
                notes=notes,
                gear=None,  # not in CSV
                is_project=is_project,
                is_milestone=is_milestone
            )

            if discipline == "Multipitch" and row['pitches'] is not None:
                pitch_data = _parse_multipitch_pitches(row['pitches'])
                create_pitches_and_ascents(session, route, ascent, pitch_data)

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
        print(f"Routes:     {session.query(Route).count()}")  # Universal routes
        print(f"Ascents:    {session.query(Ascent).count()}")  # User ascents
        print(f"  - Sport:  {session.query(Ascent).join(Ascent.route).filter(Route.discipline == 'Sportclimb').count()}")
        print(f"  - Boulder: {session.query(Ascent).join(Ascent.route).filter(Route.discipline == 'Boulder').count()}")
        print(f"  - Multi:   {session.query(Ascent).join(Ascent.route).filter(Route.discipline == 'Multipitch').count()}")
        print(f"Pitches:    {session.query(Pitch).count()}")
        print(f"PitchAscents: {session.query(PitchAscent).count()}")
        print(f"Projects:   {session.query(Ascent).filter(Ascent.is_project == True).count()}")
        print(f"Milestones: {session.query(Ascent).filter(Ascent.is_milestone == True).count()}")

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