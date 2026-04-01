import pandas as pd
import argparse
import getpass
from datetime import datetime
import country_converter as coco

from climbingdb.models.base import get_session, init_db
from climbingdb.services.crud import (
    get_or_create_location,
    get_or_create_route,
    create_ascent
)
from climbingdb.services.auth_service import AuthService
from climbingdb.models import Crag, Area


COCO = coco.CountryConverter()

# Map of 8a.nu discipline to climbingdb discipline
DISCIPLINE_MAP = {
    'ROUTE': 'Sportclimb',
    'BOULDER': 'Boulder'
}

# Map of 8a.nu styles to climbingdb style
STYLE_MAP = {
    'os': 'o.s.',
    'f': 'F',
    'rp': ''
}

# 8a.nu perceived hardness to shortnote
PERCEIVED_HARDNESS_MAP = {
    'soft': 'soft',
    'hard': 'hard',
    '': None,
    'null': None
}


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _parse_discipline(row):
    discipline_raw = row['route_boulder'].strip('"').upper()
    return DISCIPLINE_MAP.get(discipline_raw)


def _parse_date(row):
    date_str = row['date']
    if not date_str or date_str in ('null', ''):
        return None
    try:
        return datetime.strptime(date_str[:10], '%Y-%m-%d').date()
    except ValueError:
        return None


def _parse_stars(row):
    rating_str = row['rating']
    try:
        return int(rating_str)
    except (ValueError, TypeError):
        return 0


def _parse_grade(row):
    grade_str = row['difficulty']
    if not grade_str or grade_str in ('null', ''):
        return None

    # 8a.nu boulders use Font scale (uppercase)
    # System should detect this via Grade.get_scale()
    return grade_str.strip()


def _parse_style(row):
    type_str = row['type']
    if not type_str or type_str in ('null', ''):
        return None
    return STYLE_MAP.get(type_str.lower())


def _parse_shortnote(row):
    perceived_hardness = row.get('perceived_hardness', ''),
    sits = row.get('sits', '')
    tries = row.get('tries', '')
    type_str = row.get('type', '')

    notes = []

    hardness = PERCEIVED_HARDNESS_MAP.get(str(perceived_hardness).lower())
    if hardness:
        notes.append(hardness)

    if tries != "null" and tries != '0' and type_str != "f" and type_str != "os":
        notes.append("{}. Go".format(tries.strip()))

    # is this column a sit start?
    if str(sits).lower() not in ('null', '', ''):
        notes.append('sit start')

    return ', '.join(notes) if notes else None


def _parse_notes(row):
    comment = row.get('comment', '')
    if not comment or comment in ('null', ''):
        return None
    return comment.strip('"').strip()


def _parse_country(row):
    country_code = row['country_code']
    if not country_code or country_code in ('null', ''):
        return None
    else:
        return COCO.convert(country_code, to="name_short")


def _parse_crag(location_name, sector_name):
    crag_name = location_name

    if not location_name or location_name in ('null', ''):
        return "Unknown"

    if sector_name != "Unknown Sector" and sector_name.lower() != location_name.lower():
        crag_name = f"{location_name} ({sector_name})"

    return crag_name


def _parse_area_and_crag(row, crag_to_area_map=None):
    area_name = row['area_name'].strip()
    if area_name not in ('null', ''):
        print("Area information is available but unused!")

    location_name = row['location_name'].strip()
    sector_name = row['sector_name'].strip()

    if crag_to_area_map:
        all_areas = [v for _, v in crag_to_area_map.items()]

        if location_name in all_areas:
            area_name = location_name
            crag_name = sector_name
        else:
            area_name = crag_to_area_map.get(location_name, 'Unknown')
            crag_name = _parse_crag(location_name, sector_name)
    else:
        area_name = "Unknown"
        crag_name = _parse_crag(location_name, sector_name)

    return area_name, crag_name


def _parse_is_project(row):
    return row['type'].strip().lower() == "go"


def _parse_row(row, crag_to_area_map=None):
    area_name, crag_name = _parse_area_and_crag(row, crag_to_area_map)
    return {
        'name': row['name'].strip('"'),
        'discipline': _parse_discipline(row),
        'grade': _parse_grade(row),
        'style': _parse_style(row),
        'date': _parse_date(row),
        'stars': _parse_stars(row),
        'is_project': _parse_is_project(row),
        'shortnote': _parse_shortnote(row),
        'notes': _parse_notes(row),
        'country_name': _parse_country(row),
        'area_name': area_name,
        'crag_name': crag_name
    }


def parse_8anu_dataframe(df, populate_areas_from_database=True, verbose=False):
    """
    Parse 8a.nu DataFrame into list of dicts and list of skipped rows.
    Used by both preview (show_preview_of_8anu_import) and import (import_8a_csv).

    Returns:
        (parsed_rows, skipped_rows, errors)
        - parsed_rows: list of dicts with parsed fields
        - skipped_rows: list of dicts with name and reason
        - errors: list of error strings
    """
    crag_to_area_map = None
    if populate_areas_from_database:
        if verbose:
            print("  Building area map from database...")
        crag_to_area_map = _build_crag_to_area_map(verbose=verbose)

    parsed_rows = []
    skipped_rows = []
    errors = []

    for idx, row in df.iterrows():
        try:
            all_fields = _parse_row(row, crag_to_area_map)
            parsed_rows.append(all_fields)

        except Exception as e:
            error_msg = f"Row {idx} '{row.get('name', 'unknown')}': {e}"
            errors.append(error_msg)
            skipped_rows.append({'name': row.get('name', 'unknown'), 'reason': str(e)})

    return parsed_rows, skipped_rows, errors


def _build_crag_to_area_map(verbose=False):
    with get_session() as session:
        results = session.query(Crag.name, Area.name).join(Crag.area).all()

    crag_to_area_map = {crag_name: area_name for crag_name, area_name in results}
    if verbose:
        print("Loaded {len(crag_to_area_map)} crags from database for area lookup")
    return crag_to_area_map


# ---------------------------------------------------------------------------
# Main import function
# ---------------------------------------------------------------------------

def import_8a_csv(csv_file, user_id,
                  populate_areas_from_database=True, dry_run=False, verbose=False):
    """Import 8a.nu CSV export into database."""
    if verbose and type(csv_file) is str:
        print(f"\nImporting 8a.nu data from {csv_file}...")

    df = pd.read_csv(csv_file, sep=',', header=0, keep_default_na=False, dtype=str)

    parsed_rows, skipped_rows, errors = parse_8anu_dataframe(df,
        populate_areas_from_database=populate_areas_from_database, verbose=verbose)

    imported_count = 0

    with get_session() as session:
        for parsed in parsed_rows:
            try:
                if dry_run:
                    if verbose:
                        print(f"  [DRY RUN] {parsed['discipline']}: {parsed['name']} "
                              f"({parsed['grade']}) - {parsed['crag_name']}, "
                              f"{parsed['area_name']}, {parsed['country_name']}")
                    imported_count += 1
                    continue

                crag = get_or_create_location(
                    session,
                    country_name=parsed['country_name'],
                    area_name=parsed['area_name'],
                    crag_name=parsed['crag_name']
                )

                route = get_or_create_route(
                    session,
                    name=parsed['name'],
                    discipline=parsed['discipline'],
                    crag=crag,
                    grade=parsed['grade']
                )

                create_ascent(
                    session,
                    user_id=user_id,
                    route=route,
                    grade=parsed['grade'],
                    style=parsed['style'],
                    date=parsed['date'],
                    stars=parsed['stars'],
                    shortnote=parsed['shortnote'],
                    notes=parsed['notes'],
                    is_project=parsed['is_project']
                )

                imported_count += 1

            except Exception as e:
                error_msg = f"'{parsed['name']}': {e}"
                errors.append(error_msg)
                session.rollback()

        session.commit()

    return imported_count, len(skipped_rows), errors


def _get_or_create_user(username, email=None):
    """Get existing user or create new one via AuthService."""
    auth = AuthService()

    # Check if user exists
    user = auth.get_user_by_username(username)
    if user:
        print(f"  Found existing user: {username} (ID: {user.id})")
        return user

    # Create new user
    print(f"\nUser '{username}' not found. Creating new user...")
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm: ")

    if password != confirm:
        raise ValueError("Passwords don't match!")

    success, message, user = auth.create_user(
        username=username,
        password=password,
        email=email
    )

    if not success:
        raise ValueError(f"Failed to create user: {message}")

    print(f"  SUCCESS: {message} (ID: {user.id})")
    return user


def _print_summary(imported, skipped, errors):
    """Print import summary."""
    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)
    print(f"Imported:  {imported}")
    print(f"Skipped:   {skipped}")
    print(f"Errors:    {len(errors)}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")


def main():
    parser = argparse.ArgumentParser(description='Import 8a.nu CSV export')
    parser.add_argument('--file', required=True, help='Path to 8a.nu CSV file')
    parser.add_argument('--username', required=True, help='Username to import data for')
    parser.add_argument('--email', help='Email for new user (optional)')
    parser.add_argument('--dry-run', action='store_true', help='Parse without writing to database')
    args = parser.parse_args()

    print("=" * 60)
    print("8a.nu Import Script")
    print("=" * 60)

    if args.dry_run:
        print("WARNING: DRY RUN MODE - no data will be written")

    with get_session() as session:
        try:
            init_db()

            user = _get_or_create_user(args.username, args.email)

            imported, skipped, errors = import_8a_csv(
                csv_file=args.file,
                user_id=user.id,
                dry_run=args.dry_run
            )

            _print_summary(imported, skipped, errors)

        except Exception as e:
            print(f"\nERROR: Fatal error: {e}")
            session.rollback()
            raise


if __name__ == "__main__":
    main()