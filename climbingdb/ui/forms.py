"""
Main form rendering for adding routes.
"""

import streamlit as st
from datetime import date

from .location_selector import render_location_selector
from .form_helpers import (
    get_grade_system_options,
    get_style_options,
    get_grade_options,
    validate_route_data
)


def render_add_route_form(db, discipline):
    """Render form to add a new route for the given discipline."""
    
    with st.expander(f"➕ Add New {discipline}", expanded=False):
        # Grade system selection
        grade_systems = get_grade_system_options(discipline)
        grade_system = st.selectbox("Grading System", grade_systems, key="add_grade_system")
        
        # Location selection (outside form for interactivity)
        country, area, crag, name = render_location_selector(db, discipline)
        
        # Multipitch pre-form fields
        length = None
        num_pitches = 3
        if discipline == "Multipitch":
            length = st.number_input("Length (meters)", min_value=0, step=10)
            num_pitches = st.number_input("Number of Pitches", min_value=1, value=3, step=1)
        
        # Main form
        with st.form("add_route_form", clear_on_submit=True):
            route_data = _render_route_fields(
                discipline, grade_system, num_pitches if discipline == "Multipitch" else None
            )
            
            submitted = st.form_submit_button(f"Add {discipline}", type="primary", width='stretch')
            
            if submitted:
                _handle_form_submission(
                    db, discipline, name, grade_system, country, area, crag, 
                    length, route_data
                )


def _render_route_fields(discipline, grade_system, num_pitches=None):
    """Render form fields for route details."""
    grade_options = get_grade_options(grade_system)
    style_options = get_style_options(discipline)
    
    # Grade and shortnote
    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("Grade", grade_options)
    with col2:
        shortnote = st.selectbox("Short Note", ["", "soft", "hard"])
    
    # Style (not for projects)
    style = None
    if discipline != "Projects":
        style = st.selectbox("Style", [""] + style_options + ["FA"])
    
    # Stars and date
    stars = st.selectbox("Stars", [0, 1, 2, 3], index=0)
    
    climb_date = None
    if discipline != "Projects":
        climb_date = st.date_input("Date", value=date.today())
    
    # Checkboxes
    is_project = st.checkbox("Project")
    is_milestone = st.checkbox("Milestone")
    
    # Notes
    notes = st.text_area("Notes", placeholder="Detailed description...")
    
    # Multipitch-specific
    ernsthaftigkeit = None
    pitches = None
    if discipline == "Multipitch":
        ernsthaftigkeit, pitches = _render_multipitch_fields(num_pitches, grade_options)
    
    return {
        'grade': grade,
        'shortnote': shortnote,
        'style': style,
        'stars': stars,
        'climb_date': climb_date,
        'is_project': is_project,
        'is_milestone': is_milestone,
        'notes': notes,
        'ernsthaftigkeit': ernsthaftigkeit,
        'pitches': pitches
    }


def _render_multipitch_fields(num_pitches, grade_options):
    """Render multipitch-specific fields."""
    ernsthaftigkeit = st.selectbox("Ernsthaftigkeit", ["", "R", "X"])
    
    with st.expander("⛰️ Pitch Details", expanded=False):
        st.markdown("Enter grade and whether pitch was led for each pitch:")
        
        # Initialize pitch data
        if 'pitch_data' not in st.session_state or len(st.session_state.pitch_data) != num_pitches:
            st.session_state.pitch_data = [{"grade": "", "led": True} for _ in range(num_pitches)]
        
        # Render pitch inputs
        pitches_list = []
        for i in range(num_pitches):
            col_pitch, col_led = st.columns([3, 1])
            
            with col_pitch:
                pitch_grade = st.selectbox(
                    f"Pitch {i + 1} Grade",
                    grade_options,
                    key=f"pitch_grade_{i}",
                    label_visibility="collapsed"
                )
            
            with col_led:
                pitch_led = st.checkbox(
                    "Led",
                    value=st.session_state.pitch_data[i]["led"],
                    key=f"pitch_led_{i}",
                    help="Check if led, uncheck if followed"
                )
            
            pitches_list.append({"grade": pitch_grade, "led": pitch_led})
    
    return ernsthaftigkeit, pitches_list


def _handle_form_submission(db, discipline, name, grade_system, country, area, crag, length, route_data):
    """Handle form submission and route creation."""
    # Validation
    errors = validate_route_data(name, route_data['grade'], area, crag, country)
    if errors:
        for error in errors:
            st.error(error)
        return
    
    try:
        route = db.add_route(
            name=name,
            grade=route_data['grade'],
            discipline=discipline,
            crag_name=crag,
            area_name=area,
            country_name=country,
            style=route_data['style'],
            date=route_data['climb_date'],
            stars=route_data['stars'],
            shortnote=route_data['shortnote'] if route_data['shortnote'] else None,
            notes=route_data['notes'] if route_data['notes'] else None,
            is_project=route_data['is_project'],
            is_milestone=route_data['is_milestone'],
            ernsthaftigkeit=route_data['ernsthaftigkeit'],
            pitches=route_data['pitches'],
            length=length
        )
        
        st.success(f"✅ Successfully added: {route.name} ({route.grade})")
        
    except Exception as e:
        st.error(f"Error adding route: {e}")
