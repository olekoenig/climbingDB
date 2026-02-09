"""
Route display components.
"""

import streamlit as st
from .constants import DISPLAY_COLUMNS
from climbingdb.grade import Grade


def render_routes_table(routes):
    """Render routes as a data table."""
    routes = _adjust_grades_for_soft_hard(routes)
    routes = routes.sort_values(by="ole_grade", ascending=False)
    
    display_cols = _prepare_display_columns(routes)
    routes = _format_display_fields(routes)
    
    column_config = _get_column_config()
    
    st.dataframe(
        routes[display_cols],
        width='stretch',
        height=600,
        hide_index=True,
        column_config=column_config
    )


def _adjust_grades_for_soft_hard(routes):
    """Adjust ole_grade slightly for soft/hard routes to affect sort order."""
    routes['ole_grade'] = routes.apply(
        lambda row: row['ole_grade'] - 1e-6 if 'soft' in str(row['shortnote']).lower()
        else row['ole_grade'] + 1e-6 if 'hard' in str(row['shortnote']).lower()
        else row['ole_grade'],
        axis=1
    )
    return routes


def _prepare_display_columns(routes):
    """Prepare list of columns to display based on discipline."""
    display_cols = DISPLAY_COLUMNS.copy()
    
    if st.session_state.view == "Multipitch":
        display_cols.insert(2, 'length')
        routes['length'] = routes.apply(
            lambda row: f"{row.get('length', 0):.0f}m" if row.get('length') else "",
            axis=1
        )
        display_cols.insert(3, 'pitch_number')
    
    return display_cols


def _format_display_fields(routes):
    """Format grade and other display fields."""
    routes['grade'] = routes.apply(
        lambda row: _format_grade_display(row, st.session_state.view),
        axis=1
    )
    return routes


def _format_grade_display(row, discipline):
    """Format grade with optional ernsthaftigkeit and shortnote."""
    result = str(row.get('grade', ''))
    
    if not result:
        return "No grade"
    
    if discipline == 'Multipitch' and row.get('ernsthaftigkeit'):
        result += f" {row['ernsthaftigkeit']}"
    
    if row.get('shortnote'):
        result += f" ({row['shortnote']})"
    
    return result


def _get_column_config():
    """Get column configuration for dataframe display."""
    config = {
        "name": st.column_config.TextColumn("Name"),
        "grade": st.column_config.TextColumn("Grade"),
        "style": st.column_config.TextColumn("Style"),
        "area": st.column_config.TextColumn("Area"),
        "crag": st.column_config.TextColumn("Crag"),
        "notes": st.column_config.TextColumn("Notes"),
        "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
        "stars": st.column_config.NumberColumn("Stars")
    }
    
    if st.session_state.view == "Multipitch":
        config["length"] = st.column_config.TextColumn("Length")
        config["pitch_number"] = st.column_config.TextColumn("Pitches", width='stretch')
    
    return config


def convert_grades(routes, selected_grade_system):
    """Convert grades to selected grading system."""
    if selected_grade_system != "Original":
        routes['grade'] = routes['ole_grade'].apply(
            lambda x: Grade.from_ole_grade(x, selected_grade_system) if x > 0 else ""
        )
    return routes
