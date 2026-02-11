"""
Test that database indexes are properly created.

Run as:
    python3 -m unittest climbingdb.tests.test_indexes
"""

import unittest
from sqlalchemy import text
from climbingdb.models import SessionLocal, engine


class TestIndexes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up database session."""
        cls.session = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        cls.session.close()

    def _get_indexes(self):
        """Get all indexes from database (works for PostgreSQL and SQLite)."""
        dialect = engine.dialect.name

        if dialect == 'postgresql':
            result = self.session.execute(text("""
                SELECT 
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname;
            """))
            return [(row[0], row[1]) for row in result]

        elif dialect == 'sqlite':
            result = self.session.execute(text("""
                SELECT 
                    tbl_name,
                    name
                FROM sqlite_master
                WHERE type = 'index' AND tbl_name NOT LIKE 'sqlite_%'
                ORDER BY tbl_name, name;
            """))
            return [(row[0], row[1]) for row in result]

        else:
            self.fail(f"Unsupported database dialect: {dialect}")

    def test_routes_discipline_index(self):
        """Test that routes.discipline has an index."""
        indexes = self._get_indexes()
        route_indexes = [idx_name for table, idx_name in indexes if table == 'routes']

        discipline_indexed = any('discipline' in idx.lower() for idx in route_indexes)
        self.assertTrue(
            discipline_indexed,
            f"Missing index on routes.discipline. Found indexes: {route_indexes}"
        )

    def test_routes_ole_grade_index(self):
        """Test that routes.ole_grade has an index."""
        indexes = self._get_indexes()
        route_indexes = [idx_name for table, idx_name in indexes if table == 'routes']

        ole_grade_indexed = any('ole_grade' in idx.lower() for idx in route_indexes)
        self.assertTrue(
            ole_grade_indexed,
            f"Missing index on routes.ole_grade. Found indexes: {route_indexes}"
        )

    def test_routes_is_project_index(self):
        """Test that routes.is_project has an index."""
        indexes = self._get_indexes()
        route_indexes = [idx_name for table, idx_name in indexes if table == 'routes']

        is_project_indexed = any('is_project' in idx.lower() or 'project' in idx.lower() for idx in route_indexes)
        self.assertTrue(
            is_project_indexed,
            f"Missing index on routes.is_project. Found indexes: {route_indexes}"
        )

    def test_routes_crag_id_foreign_key_index(self):
        """Test that routes.crag_id has an index (from foreign key)."""
        indexes = self._get_indexes()
        route_indexes = [idx_name for table, idx_name in indexes if table == 'routes']

        crag_id_indexed = any('crag_id' in idx.lower() or 'crag' in idx.lower() for idx in route_indexes)
        self.assertTrue(
            crag_id_indexed,
            f"Missing index on routes.crag_id. Found indexes: {route_indexes}"
        )

    def test_crags_area_id_foreign_key_index(self):
        """Test that crags.area_id has an index (from foreign key)."""
        indexes = self._get_indexes()
        crag_indexes = [idx_name for table, idx_name in indexes if table == 'crags']

        area_id_indexed = any('area_id' in idx.lower() or 'area' in idx.lower() for idx in crag_indexes)
        self.assertTrue(
            area_id_indexed,
            f"Missing index on crags.area_id. Found indexes: {crag_indexes}"
        )

    def test_primary_key_indexes_exist(self):
        """Test that all tables have primary key indexes."""
        indexes = self._get_indexes()
        tables = ['routes', 'crags', 'areas', 'countries']

        for table in tables:
            table_indexes = [idx_name for tbl, idx_name in indexes if tbl == table]
            self.assertTrue(
                len(table_indexes) > 0,
                f"No indexes found on {table}. This likely means the table doesn't exist."
            )

    def test_print_all_indexes(self):
        """Print all indexes for debugging (always passes)."""
        indexes = self._get_indexes()

        print("\n" + "=" * 60)
        print("All Database Indexes")
        print("=" * 60)

        current_table = None
        for table, index_name in sorted(indexes):
            if table != current_table:
                print(f"\n{table}:")
                current_table = table
            print(f"  - {index_name}")

        print("=" * 60)

        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()