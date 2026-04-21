import os

# For local development, use environment variable with SQLite
# For Streamlit Cloud, uses secrets.toml
DATADIR = "data/"
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DATADIR}climbing.db')
APP_BASE_URL = os.getenv('APP_BASE_URL', "http://localhost:8501/")
REQUIRE_AUTH = os.getenv('REQUIRE_AUTH', 'true').lower() == 'true'
SHOW_DEMO = os.getenv('SHOW_DEMO', 'false').lower() == 'true'

EIGHTANU_EXPORT_URL = "https://www.8a.nu/api/unification/ascent/v1/web/ascents/export-csv"

# Old setup with CSV-based data
CRAGS_CSV_FILE = DATADIR + "crags.csv"
ROUTES_CSV_FILE = DATADIR + "routes.csv"
BOULDERS_CSV_FILE = DATADIR + "boulders.csv"
MULTIPITCHES_CSV_FILE = DATADIR + "multipitches.csv"
