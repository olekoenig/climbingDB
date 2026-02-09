"""
Sidebar filter components.
"""

import streamlit as st
from .constants import (
    GRADE_OPTIONS_ROUTES,
    GRADE_OPTIONS_BOULDERS,
    SPORT_GRADE_SYSTEMS,
    BOULDER_GRADE_SYSTEMS
)


def get_grade_system_options(view):
    """Get available grade systems for current view."""
    if view in ['Sportclimb', 'Multipitch', 'Projects']:
        return SPORT_GRADE_SYSTEMS
    elif view == 'Boulder':
        return BOULDER_GRADE_SYSTEMS
    return ["Original"]


def get_discipline_areas(db, discipline):
    """Get areas that have routes in the specified discipline."""
    if discipline == "Projects":
        df = db.get_projects()
    else:
        df = db.get_filtered_routes(discipline=discipline)
    
    return sorted(df['area'].unique().tolist()) if len(df) > 0 else []


def render_sidebar_filters(db):
    """Render sidebar filters and return filter values."""
    _render_filter_header()
    
    selected_area = _render_area_filter(db)
    _handle_area_discipline_switch(db, selected_area)
    
    grade_operation, selected_grade = _render_grade_filters()
    selected_grade_system = _render_grade_system_filter()
    sandbaggers_choice = _render_sandbaggers_choice()
    selected_stars = _render_stars_filter()
    
    return {
        'area': None if selected_area == "All" else selected_area,
        'grade': None if selected_grade == "All" else selected_grade,
        'grade_operation': grade_operation,
        'grade_system': selected_grade_system,
        'sandbaggers_choice': sandbaggers_choice,
        'stars': None if selected_stars == 0 else selected_stars,
        'selected_area': selected_area,
        'selected_grade': selected_grade,
        'selected_stars': selected_stars
    }


def _render_filter_header():
    """Render filter header with reset button."""
    col_header, col_reset = st.sidebar.columns([3, 1])
    with col_header:
        st.markdown("### Filters")
    with col_reset:
        if st.button("🔄", help="Reset all filters", key="reset_filters"):
            st.session_state.selected_area = "All"
            st.session_state.grade_operation_select = ">="
            st.session_state.grade_select = "All"
            st.session_state.grade_system_select = "Original"
            st.session_state.sandbaggers_choice = "Round down"
            st.session_state.stars_select = 0
            st.rerun()


def _render_area_filter(db):
    """Render area filter dropdown."""
    all_areas = get_discipline_areas(db, st.session_state.view)
    area_options = ["All"] + all_areas
    
    if 'selected_area' not in st.session_state:
        st.session_state.selected_area = "All"
    
    return st.sidebar.selectbox("Area", area_options, key='selected_area')


def _handle_area_discipline_switch(db, selected_area):
    """Auto-switch discipline if area only has one discipline."""
    if selected_area == "All":
        return
    
    area_disciplines = []
    for disc in ['Sportclimb', 'Boulder', 'Multipitch']:
        df = db.get_filtered_routes(discipline=disc, area=selected_area)
        if len(df) > 0:
            area_disciplines.append(disc)
    
    if len(area_disciplines) == 1 and st.session_state.view != area_disciplines[0]:
        st.session_state.view = area_disciplines[0]
        st.rerun()


def _render_grade_filters():
    """Render grade operation and grade selection."""
    col_op, col_grade = st.sidebar.columns([2, 3])
    
    with col_op:
        grade_operation = st.selectbox(
            "Op",
            [">=", "=="],
            index=0,
            help="≥: at or above\n==: exact grade",
            key='grade_operation_select'
        )
    
    with col_grade:
        grade_options = (GRADE_OPTIONS_BOULDERS if st.session_state.view == "Boulder" 
                        else GRADE_OPTIONS_ROUTES)
        selected_grade = st.selectbox(
            "Grade",
            grade_options,
            index=0,
            key='grade_select'
        )
    
    return grade_operation, selected_grade


def _render_grade_system_filter():
    """Render grade system selector."""
    grade_system_options = get_grade_system_options(st.session_state.view)
    return st.sidebar.selectbox(
        "Display Grades As",
        grade_system_options,
        help="Convert grades to different grading systems",
        key='grade_system_select'
    )


def _render_sandbaggers_choice():
    """Render sandbagger's choice selector."""
    return st.sidebar.selectbox(
        "Sandbagger's Choice",
        ["Round down", "Round up"],
        index=0,
        help="Round slash grades up or down",
        key='sandbaggers_choice'
    )


def _render_stars_filter():
    """Render stars filter slider."""
    return st.sidebar.slider(
        "Minimum Stars",
        min_value=0,
        max_value=3,
        value=0,
        step=1,
        format="%d",
        key='stars_select'
    )


def render_filter_summary(filters):
    """Render active filters summary in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Active Filters")
    
    if filters['selected_area'] != "All":
        st.sidebar.write(f"📍 Area: {filters['selected_area']}")
    
    if filters['selected_grade'] != "All":
        st.sidebar.write(f"📈 Grade: {filters['grade_operation']} {filters['selected_grade']}")
    
    if filters['grade_system'] != "Original":
        st.sidebar.write(f"🎚️ Grade System: {filters['grade_system']}")
    
    if filters['selected_stars'] > 0:
        st.sidebar.write(f"⭐ Stars: ≥ {filters['selected_stars']}")
