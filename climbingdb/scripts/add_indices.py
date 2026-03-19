"""
Add missing indexes to existing database.

Run as:
    python3 -m climbingdb.scripts.add_indices
"""

from climbingdb.models import SessionLocal
from sqlalchemy import text


def add_missing_indexes():
    """Add performance indexes to existing database."""
    session = SessionLocal()

    indexes = [
        # Ascent indexes
        "CREATE INDEX IF NOT EXISTS ix_ascents_user_id ON ascents(user_id);",
        "CREATE INDEX IF NOT EXISTS ix_ascents_route_id ON ascents(route_id);",
        "CREATE INDEX IF NOT EXISTS ix_ascents_is_project ON ascents(is_project);",
        "CREATE INDEX IF NOT EXISTS ix_ascents_is_milestone ON ascents(is_milestone);",
        "CREATE INDEX IF NOT EXISTS ix_ascents_date ON ascents(date);",
        "CREATE INDEX IF NOT EXISTS ix_ascents_ole_grade ON ascents(ole_grade);",

        # Composite index - most common query pattern
        "CREATE INDEX IF NOT EXISTS ix_ascents_user_project ON ascents(user_id, is_project);",
        "CREATE INDEX IF NOT EXISTS ix_ascents_user_route ON ascents(user_id, route_id);",

        # PitchAscent indexes
        "CREATE INDEX IF NOT EXISTS ix_pitchascents_ascent_id ON pitchascents(ascent_id);",
        "CREATE INDEX IF NOT EXISTS ix_pitchascents_pitch_id ON pitchascents(pitch_id);",
        "CREATE INDEX IF NOT EXISTS ix_pitchascents_pitch_id ON pitchascents(pitch_id);",

        # Route indexes
        "CREATE INDEX IF NOT EXISTS ix_routes_discipline ON routes(discipline);",
        "CREATE INDEX IF NOT EXISTS ix_routes_consensus_ole_grade ON routes(consensus_ole_grade);",
        "CREATE INDEX IF NOT EXISTS ix_routes_crag_id ON routes(crag_id);",

        # Pitch indexes
        "CREATE INDEX IF NOT EXISTS ix_pitches_route_id ON pitches(route_id);",
    ]

    print("Adding indexes...")
    for idx_sql in indexes:
        try:
            session.execute(text(idx_sql))
            name = idx_sql.split('INDEX')[1].split('ON')[0].strip()
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  Error: {e}")

    session.commit()
    session.close()
    print("Done!")


if __name__ == "__main__":
    add_missing_indexes()