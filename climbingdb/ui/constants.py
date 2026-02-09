"""
Constants and configuration for the UI.
"""

GRADE_OPTIONS_ROUTES = [
    "All", "4a", "5a", "6a", "6b", "6c", "7a", "7a+", "7b", "7b+",
    "7c", "7c+", "8a", "8a+", "8b", "8b+", "8c", "8c+", "9a"
]

GRADE_OPTIONS_BOULDERS = [
    'All', 'V0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8',
    'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15'
]

SPORT_GRADE_SYSTEMS = ["Original", "French", "UIAA", "YDS", "Elbsandstein"]
BOULDER_GRADE_SYSTEMS = ["Original", "Vermin", "Font"]

DISPLAY_COLUMNS = ['name', 'grade', 'style', 'area', 'crag', 'notes', 'date', 'stars']

CUSTOM_CSS = """
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-size: 16px;
        font-weight: bold;
    }
    </style>
"""
