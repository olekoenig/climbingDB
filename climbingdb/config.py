import os

# For local development, use environment variable with SQLite
# For Streamlit Cloud, uses secrets.toml
DATADIR = "data/"
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DATADIR}climbing.db')
REQUIRE_AUTH = os.getenv('REQUIRE_AUTH', 'true').lower() == 'true'

# Old setup with CSV-based data
CRAGS_CSV_FILE = DATADIR + "crags.csv"
ROUTES_CSV_FILE = DATADIR + "routes.csv"
BOULDERS_CSV_FILE = DATADIR + "boulders.csv"
MULTIPITCHES_CSV_FILE = DATADIR + "multipitches.csv"
