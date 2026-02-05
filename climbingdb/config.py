import os

# Database URL - SQLite for local development
# (switch to PostgreSQL for deployment for many users later)
DATADIR = "data/"
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DATADIR}climbing.db')

# Old setup with CSV-based data
CRAGS_CSV_FILE = DATADIR + "crags.csv"
ROUTES_CSV_FILE = DATADIR + "routes.csv"
BOULDERS_CSV_FILE = DATADIR + "boulders.csv"
MULTIPITCHES_CSV_FILE = DATADIR + "multipitches.csv"
