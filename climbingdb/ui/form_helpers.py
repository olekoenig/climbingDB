"""
Helper functions for form rendering.
"""

import streamlit as st
from datetime import date

from climbingdb.grade import ALL_GRADE_SYSTEMS
from climbingdb.ui.navigation import DISCIPLINE_ICONS


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
        shortnote.extend(["simul", "big wall"])

    return shortnote


def get_ernsthaftigkeit_options():
    return ["", "R", "X", "V", "VI"]


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


def render_multipitch_metadata(route, ascent):
    default_length = int(route.length) if route and route.length else 0
    ernst_options = get_ernsthaftigkeit_options()
    default_ernst_index = ernst_options.index(route.ernsthaftigkeit) if route and route.ernsthaftigkeit else 0
    default_ascent_time = float(ascent.ascent_time) if ascent and ascent.ascent_time else 0.0

    length = st.number_input("Total Length (m)", min_value=0, step=10, value=default_length)

    col_ernst, col_time = st.columns(2)
    with col_ernst:
        ernsthaftigkeit = st.selectbox("Ernsthaftigkeit (overall)", ernst_options,
                                       index=default_ernst_index)
    with col_time:
        ascent_time = st.number_input("Ascent Time (hours)", min_value=0.0, step=0.5,
                                      value = default_ascent_time)

    return (
        length if length > 0 else None,
        ernsthaftigkeit,
        ascent_time if ascent_time > 0 else None
    )


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
    grade_idx = 0
    length = 0.0
    pitch_name = ""
    ernsthaftigkeit_idx = 0
    style_idx = 0
    led_bool = True
    stars_idx = 0
    notes = ""
    gear = ""

    if pitch:
        if pitch.consensus_grade in grade_options:
            grade_idx = grade_options.index(pitch.consensus_grade)

        length = pitch.length if pitch.length else 0.0
        pitch_name = pitch.pitch_name if pitch.pitch_name else ""

        ernsthaftigkeit_options = get_ernsthaftigkeit_options()
        if pitch.ernsthaftigkeit in ernsthaftigkeit_options:
            ernsthaftigkeit_idx = ernsthaftigkeit_options.index(pitch.ernsthaftigkeit)

    if pitch_ascent:
        if pitch_ascent.grade in grade_options:
            grade_idx = grade_options.index(pitch_ascent.grade)
        if pitch_ascent.style in style_options:
            style_idx = style_options.index(pitch_ascent.style)

        led_bool = pitch_ascent.led
        stars_idx = pitch_ascent.stars
        notes = pitch_ascent.notes if pitch_ascent.notes else ""
        gear = pitch_ascent.gear if pitch_ascent.gear else ""

    return (grade_idx, length, pitch_name, ernsthaftigkeit_idx,
            style_idx, led_bool, stars_idx, notes, gear)


def render_multipitch_fields(grade_options, style_options, shortnote_options, num_pitches,
                             route=None, ascent=None):
    """Render multipitch fields with full pitch details."""
    length, ernsthaftigkeit, ascent_time = render_multipitch_metadata(route=route, ascent=ascent)

    key_prefix = "edit" if ascent else "add"

    with (st.expander(f"{DISCIPLINE_ICONS['Pitches']} Detailed Pitch Information", expanded=False)):
        st.markdown("Enter complete details for each pitch:")

        pitches_list = []
        for i in range(num_pitches):
            st.markdown(f"### Pitch {i+1}")

            pitch = route.pitches[i] if route else None  # contains info of the pitch's grade, name, style, etc.
            pitch_ascent = ascent.pitch_ascents[i] if ascent else None  # contains info of overall grade, style, etc.

            # Get the correct indices and values for auto-population (both if one wants
            # to add a route that is already in the database, and if one wants to edit a route).
            (default_grade_idx, default_length, default_pitch_name, default_ernsthaftigkeit_idx,
             default_style_idx, default_led, default_stars_idx, default_notes, default_gear) = (
                _get_multipitch_defaults(grade_options, style_options, shortnote_options,
                                         pitch=pitch, pitch_ascent=pitch_ascent))

            col1, col2, col3 = st.columns(3)
            with col1:
                grade = st.selectbox("Grade", grade_options,
                                           key=f"{key_prefix}_pitch_grade_{i}", index=default_grade_idx)
                pitch_name = st.text_input("Pitch Name", key=f"{key_prefix}_pitch_name_{i}", placeholder="e.g., Crux pitch",
                                           value=default_pitch_name)

            with col2:
                style = st.selectbox("Style", style_options, key=f"{key_prefix}_pitch_style_{i}", index=default_style_idx)
                led = st.checkbox("Led (uncheck if followed)", value=default_led, key=f"{key_prefix}_pitch_led_{i}")

            with col3:
                stars = st.selectbox("Stars", [0, 1, 2, 3, 4, 5], key=f"{key_prefix}_pitch_stars_{i}",
                                           index=default_stars_idx)
                length = st.number_input("Length (m)", min_value=0.0, key=f"{key_prefix}_pitch_length_{i}",
                                               value=default_length)

            col4, col5 = st.columns(2)
            with col4:
                ernsthaftigkeit_options = get_ernsthaftigkeit_options()
                ernst = st.selectbox("Ernsthaftigkeit", ernsthaftigkeit_options,
                                           key=f"{key_prefix}_pitch_ernst_{i}", index=default_ernsthaftigkeit_idx)
            with col5:
                shortnote = st.multiselect("Short note", shortnote_options, key=f"{key_prefix}_pitch_shortnote_{i}")

            notes = st.text_area("Pitch Notes", value=default_notes,
                                       key=f"{key_prefix}_pitch_notes_{i}", placeholder="Detailed notes for this pitch")
            gear = st.text_input("Pitch Gear", value=default_gear,
                                       key=f"{key_prefix}_pitch_gear_{i}", placeholder="Specific gear for this pitch")

            pitches_list.append({
                "pitch_ascent_id": pitch_ascent.id if pitch_ascent else None,
                "grade": grade,
                "led": led,
                "style": style,
                "stars": stars,
                "shortnote": ', '.join(shortnote),
                "notes": notes,
                "gear": gear,
                "length": length,
                "pitch_name": pitch_name,
                "ernsthaftigkeit": ernst
            })

            if i < int(num_pitches) - 1:
                st.markdown("---")

    return length, ernsthaftigkeit, ascent_time, pitches_list


