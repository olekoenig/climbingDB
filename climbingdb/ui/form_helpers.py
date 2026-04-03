"""
Helper functions for form rendering.
"""

import streamlit as st
from datetime import date

from climbingdb.grade import ALL_GRADE_SYSTEMS


def get_grade_system_options(discipline):
    """Get available grading systems for discipline."""
    if discipline == "Boulder":
        return ["Vermin", "Font"]
    return ["French", "UIAA", "YDS", "Elbsandstein"]


def get_style_options(discipline):
    """Get available style options for discipline."""
    style_options = [""]
    if discipline == "Boulder":
        style_options += ["F"]
    elif discipline == "Sportclimb":
        style_options += ["o.s.", "F", "2. Go", "toprope"]
    else:  # Multipitch
        style_options += ["o.s.", "F", "AF", "followed"]
    return style_options


def get_grade_options(grade_system):
    """Get sorted grade options for a grading system."""
    if grade_system not in ALL_GRADE_SYSTEMS:
        raise ValueError(f"Unknown grade system: {grade_system}")
    grade_dict = ALL_GRADE_SYSTEMS[grade_system]  # French, UIAA, etc.
    return [""] + [k for k, v in sorted(grade_dict.items(), key=lambda x: x[1])]


def get_shortnote_options(discipline):
    """Get short note options for discipline."""
    shortnote = ["", "soft", "hard", "FA"]
    if discipline == "Boulder":
        shortnote.extend(["sit start", "trav"])
    else:
        shortnote.append("trad")

    if discipline == "Multipitch":
        shortnote.append("simul")

    return shortnote


def get_ernsthaftigkeit_options():
    return ["", "R", "X"]


def validate_route_data(name, grade, area, crag, country):
    """Validate required route fields."""
    errors = []
    if not name:
        errors.append("Route name is required!")
    if not grade:
        errors.append("Grade is required!")
    if not area or not crag or not country:
        errors.append("Country, area, and crag are required!")
    return errors


def render_gps_fields(route):
    col_lat, col_lon = st.columns(2)
    default_lat = float(route.latitude) if route and route.latitude else 0.0
    default_lon = float(route.longitude) if route and route.longitude else 0.0
    with col_lat:
        latitude = st.number_input("Latitude", format="%.6f", value=default_lat, help="GPS coordinate")
    with col_lon:
        longitude = st.number_input("Longitude", format="%.6f", value=default_lon, help="GPS coordinate")

    # Reset coordinates such that not all routes where this was unpopulated are actually at GPS=0/0
    latitude = latitude if latitude != 0.0 else None
    longitude = longitude if longitude != 0.0 else None

    return latitude, longitude


def render_multipitch_metadata(route):
    default_length = int(route.length) if route and route.length else 0
    length = st.number_input("Total Length (m)", min_value=0, step=10, value=default_length)

    col_ernst, col_time = st.columns(2)
    with col_ernst:
        ernsthaftigkeit = st.selectbox("Ernsthaftigkeit (overall)", ["", "R", "X"])
    with col_time:
        ascent_time = st.number_input("Ascent Time (hours)", min_value=0.0, step=0.5)

    return length if length > 0 else None, ernsthaftigkeit, ascent_time if ascent_time > 0 else None


def render_grade_field(grade_options, route=None, ascent=None):
    """
    Split this off from render_ascent_misc_fields because it can either be populated
    from an existing route in the database when a user wants to add a route, or it
    should be set to the already selected ascent grade when the user wants to edit
    the own ascent.
    """

    # Auto-populate grade from existing route (when adding) or ascent (when editing)
    default_grade_idx = 0
    if route and route.consensus_grade in grade_options:
        default_grade_idx = grade_options.index(route.consensus_grade)
    if ascent and ascent.grade in grade_options:
        default_grade_idx = grade_options.index(ascent.grade)

    return st.selectbox("Grade", grade_options, index=default_grade_idx)


def _get_ascent_defaults(discipline, style_options, shortnote_options, ascent=None):
    style_idx = 0
    stars_idx = 0
    shortnote = []
    date_value = date.today()
    is_project_bool = False
    is_milestone_bool = False
    notes = ""
    gear = ""

    if ascent:
        if ascent.style in style_options:
            style_idx = style_options.index(ascent.style)

        if ascent.shortnote:
            candidates = [s.strip() for s in ascent.shortnote.split(',')]
            shortnote = [s for s in candidates if s in shortnote_options]

        stars_idx = ascent.stars
        date_value = ascent.date
        is_project_bool = ascent.is_project
        is_milestone_bool = ascent.is_milestone
        notes = ascent.notes if ascent.notes else ""
        gear = ascent.gear if ascent.gear else ""

    if discipline == "Projects":
        is_project_bool = True

    return style_idx, stars_idx, shortnote, date_value, is_project_bool, is_milestone_bool, notes, gear


def render_ascent_misc_fields(discipline, style_options, shortnote_options, ascent=None):
    (default_style_idx, default_stars_idx, default_shortnote,
     default_date_value, default_is_project, default_is_milestone, default_notes, default_gear) = (
        _get_ascent_defaults(discipline, style_options, shortnote_options, ascent=ascent))

    style = st.selectbox("Style", style_options, index=default_style_idx) if discipline != "Projects" else None
    stars = st.selectbox("Stars", [0, 1, 2, 3, 4, 5], index=default_stars_idx)

    shortnote = st.multiselect("Short Note", shortnote_options, default=default_shortnote)
    shortnote = ', '.join(shortnote) if shortnote else None

    climb_date = st.date_input("Date", value=default_date_value) if discipline != "Projects" else None
    is_project = st.checkbox("Project", value=default_is_project)
    is_milestone = st.checkbox("Milestone", value=default_is_milestone)

    notes = st.text_area("Notes", value=default_notes, placeholder="Detailed description...")
    gear = st.text_input("Gear", value=default_gear, placeholder="e.g., 10 quickdraws, cams #0.5-3") if discipline != "Boulder" else None

    return style, stars, shortnote, climb_date, is_project, is_milestone, notes, gear


def _get_multipitch_defaults(grade_options, style_options, shortnote_options,
                             pitch=None, pitch_ascent=None):
    # Auto-populate from existing pitch
    pitch_grade_idx = 0
    pitch_length = 0
    pitch_name = ""
    pitch_ernsthaftigkeit_idx = 0
    pitch_style_idx = 0
    pitch_led_bool = True
    pitch_stars_idx = 0
    pitch_notes = ""
    pitch_gear = ""

    if pitch:
        if pitch.pitch_consensus_grade in grade_options:
            pitch_grade_idx = grade_options.index(pitch.pitch_consensus_grade)

        pitch_length = pitch.pitch_length if pitch.pitch_length else 0
        pitch_name = pitch.pitch_name if pitch.pitch_name else ""

        ernsthaftigkeit_options = get_ernsthaftigkeit_options()
        if pitch.pitch_ernsthaftigkeit in ernsthaftigkeit_options:
            pitch_ernsthaftigkeit_idx = ernsthaftigkeit_options.index(pitch.pitch_ernsthaftigkeit)

    if pitch_ascent:
        if pitch_ascent.grade in grade_options:
            pitch_grade_idx = grade_options.index(pitch_ascent.grade)
        if pitch_ascent.style in style_options:
            pitch_style_idx = style_options.index(pitch_ascent.style)

        pitch_led_bool = pitch_ascent.led
        pitch_stars_idx = pitch_ascent.stars
        pitch_notes = pitch_ascent.notes if pitch_ascent.notes else ""
        pitch_gear = pitch_ascent.gear if pitch_ascent.gear else ""

    return (pitch_grade_idx, pitch_length, pitch_name, pitch_ernsthaftigkeit_idx,
            pitch_style_idx, pitch_led_bool, pitch_stars_idx, pitch_notes, pitch_gear)


def render_multipitch_fields(grade_options, style_options, shortnote_options, num_pitches,
                             route=None, ascent=None):
    """Render multipitch fields with full pitch details."""
    length, ernsthaftigkeit, ascent_time = render_multipitch_metadata(route=route)

    key_prefix = "edit" if ascent else "add"

    with (st.expander(":material/altitude: Detailed Pitch Information", expanded=False)):
        st.markdown("Enter complete details for each pitch:")

        pitches_list = []
        for i in range(num_pitches):
            st.markdown(f"### Pitch {i+1}")

            pitch = route.pitches[i] if route else None  # contains info of pitch_grade, pitch_name, pitch_style, etc.
            pitch_ascent = ascent.pitch_ascents[i] if ascent else None  # contains info of overall grade, style, etc.

            # Get the correct indices and values for auto-population (both if one wants
            # to add a route that is already in the database, and if one wants to edit a route).
            (default_pitch_grade_idx, default_pitch_length, default_pitch_name, default_pitch_ernsthaftigkeit_idx,
             default_pitch_style_idx, default_pitch_led, default_pitch_stars_idx, default_pitch_notes, default_pitch_gear) = (
                _get_multipitch_defaults(grade_options, style_options, shortnote_options,
                                         pitch=pitch, pitch_ascent=pitch_ascent))

            col1, col2, col3 = st.columns(3)
            with col1:
                pitch_grade = st.selectbox("Grade", grade_options,
                                           key=f"{key_prefix}_pitch_grade_{i}", index=default_pitch_grade_idx)
                pitch_name = st.text_input("Name", key=f"{key_prefix}_pitch_name_{i}", placeholder="e.g., Crux pitch",
                                           value=default_pitch_name)

            with col2:
                pitch_style = st.selectbox("Style", style_options, key=f"{key_prefix}_pitch_style_{i}", index=default_pitch_style_idx)
                pitch_led = st.checkbox("Led (uncheck if followed)", value=default_pitch_led, key=f"{key_prefix}_pitch_led_{i}")

            with col3:
                pitch_stars = st.selectbox("Stars", [0, 1, 2, 3, 4, 5], key=f"{key_prefix}_pitch_stars_{i}",
                                           index=default_pitch_stars_idx)
                pitch_length = st.number_input("Length (m)", min_value=0, key=f"{key_prefix}_pitch_length_{i}",
                                               value=default_pitch_length)

            col4, col5 = st.columns(2)
            with col4:
                ernsthaftigkeit_options = get_ernsthaftigkeit_options()
                pitch_ernst = st.selectbox("Ernsthaftigkeit", ernsthaftigkeit_options,
                                           key=f"{key_prefix}_pitch_ernst_{i}", index=default_pitch_ernsthaftigkeit_idx)
            with col5:
                pitch_shortnote = st.multiselect("Short note", shortnote_options, key=f"{key_prefix}_pitch_shortnote_{i}")

            pitch_notes = st.text_area("Pitch Notes", value=default_pitch_notes,
                                       key=f"{key_prefix}_pitch_notes_{i}", placeholder="Detailed notes for this pitch")
            pitch_gear = st.text_input("Pitch Gear", value=default_pitch_gear,
                                       key=f"{key_prefix}_pitch_gear_{i}", placeholder="Specific gear for this pitch")

            pitches_list.append({
                "pitch_ascent_id": pitch_ascent.id if pitch_ascent else None,
                "grade": pitch_grade,
                "led": pitch_led,
                "style": pitch_style,
                "stars": pitch_stars,
                "pitch_length": pitch_length,
                "pitch_name": pitch_name,
                "ernsthaftigkeit": pitch_ernst,
                "shortnote": ', '.join(pitch_shortnote),
                "notes": pitch_notes,
                "gear": pitch_gear
            })

            if i < int(num_pitches) - 1:
                st.markdown("---")

    return length, ernsthaftigkeit, ascent_time, pitches_list


