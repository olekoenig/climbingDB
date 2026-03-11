"""
Main form rendering for adding/editing routes.
"""

import streamlit as st
from datetime import date

from .location_selector import render_location_selector, get_existing_route_data
from .form_helpers import (
    get_grade_system_options,
    get_style_options,
    get_grade_options,
    validate_route_data,
    get_shortnote_options
)


def render_add_route_form(db, discipline):
    """Render form to add a new route."""

    with st.expander(f"➕ Add New {discipline}", expanded=False):
        grade_systems = get_grade_system_options(discipline)
        grade_system = st.selectbox("Grading System", grade_systems, key="add_grade_system")

        country, area, crag, name = render_location_selector(db, discipline)

        # Fetch existing route data for auto-population (could be None)
        existing_route = get_existing_route_data(db, name, crag, discipline)

        with st.form("add_route_form", clear_on_submit=True):
            route_data = _render_route_fields(discipline, grade_system, existing_route=existing_route)

            submitted = st.form_submit_button(f"Add {discipline}", type="primary", width='stretch')

            if submitted:
                _handle_form_submission(db, discipline, name, country, area, crag, route_data)


def _render_route_fields(discipline, grade_system, existing_route=None):
    """Render form fields for route details."""
    grade_options = get_grade_options(grade_system)

    # Auto-populate grade from existing route
    default_grade_idx = 0
    if existing_route and existing_route.consensus_grade in grade_options:
        default_grade_idx = grade_options.index(existing_route.consensus_grade)

    style_options = get_style_options(discipline)
    shortnote_options = get_shortnote_options(discipline)

    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("Grade", grade_options, index=default_grade_idx)
        style = st.selectbox("Style", [""] + style_options + ["FA"]) if discipline != "Projects" else None
        stars = st.selectbox("Stars", [0, 1, 2, 3, 4, 5], index=0)

    with col2:
        shortnote = st.multiselect("Short Note", shortnote_options)
        climb_date = st.date_input("Date", value=date.today()) if discipline != "Projects" else None
        col_proj, col_mile = st.columns(2)
        with col_proj:
            is_project = st.checkbox("Project")
        with col_mile:
            is_milestone = st.checkbox("Milestone")

    col_lat, col_lon = st.columns(2)
    default_lat = float(existing_route.latitude) if existing_route and existing_route.latitude else 0.0
    default_lon = float(existing_route.longitude) if existing_route and existing_route.longitude else 0.0
    with col_lat:
        latitude = st.number_input("Latitude", format="%.6f", value=default_lat, help="GPS coordinate")
    with col_lon:
        longitude = st.number_input("Longitude", format="%.6f", value=default_lon, help="GPS coordinate")

    # Reset coordinates such that not all routes where this was unpopulated are actually at GPS=0/0
    latitude = latitude if latitude != 0.0 else None
    longitude = longitude if longitude != 0.0 else None

    notes = st.text_area("Notes", placeholder="Detailed description...")
    gear = st.text_input("Gear", placeholder="e.g., 10 quickdraws, cams #0.5-3") if discipline != "Boulder" else None

    ernsthaftigkeit = pitches = length = ascent_time = None
    if discipline == "Multipitch":
        ernsthaftigkeit, ascent_time, length, pitches = _render_multipitch_fields(
            grade_options, style_options, shortnote_options, existing_route=existing_route
        )

    return {
        'grade': grade,
        'shortnote': ', '.join(shortnote) if shortnote else None,
        'style': style,
        'stars': stars,
        'climb_date': climb_date,
        'is_project': is_project,
        'is_milestone': is_milestone,
        'notes': notes,
        'gear': gear,
        'latitude': latitude,
        'longitude': longitude,
        'ernsthaftigkeit': ernsthaftigkeit,
        'pitches': pitches,
        'length': length,
        'ascent_time': ascent_time
    }


def render_edit_delete_form(db, routes_df):
    """Render edit/delete functionality."""

    if len(routes_df) == 0:
        st.info("No routes to edit. Adjust filters or add a new route.")
        return

    route_options = [
        f"{name} ({grade}) - {crag}"
        for name, grade, crag in zip(routes_df['name'], routes_df['grade'], routes_df['crag'])
    ]

    with st.expander("🔧 Edit or Delete Routes"):
        selected_idx = st.selectbox("Select Route to Edit/Delete", range(len(route_options)),
                                    format_func=lambda i: route_options[i])
        # Hack to typecast numpy.int64 (from the pandas dataframe) to python-integer
        ascent_id = int(routes_df.iloc[selected_idx]['id'])
        ascent = db.get_ascent_by_id(ascent_id)

        if not ascent:
            st.error("Ascent not found!")
            return

        tab1, tab2 = st.tabs(["✏️ Edit", "🗑️ Delete"])

        with tab1:
            _render_edit_form(db, ascent)

        with tab2:
            _render_delete_confirmation(db, ascent)


def _render_edit_form(db, ascent):
    """Render edit form for an ascent."""
    route = ascent.route  # Get route from ascent

    with st.form(f"edit_route_form_{ascent.id}"):
        col1, col2 = st.columns(2)

        with col1:
            # Route name is read-only (universal property)
            st.text_input("Route Name", value=route.name, disabled=True, help="Route name cannot be changed")
            new_grade = st.text_input("Grade", value=ascent.grade)  # user's ascent.grade
            new_style = st.text_input("Style", value=ascent.style if ascent.style else "")
            new_stars = st.selectbox("Stars", [0, 1, 2, 3, 4, 5], index=int(ascent.stars))

        with col2:
            new_date = st.date_input("Date", value=ascent.date if ascent.date else date.today())
            new_shortnote = st.text_input("Short Note", value=ascent.shortnote if ascent.shortnote else "")
            col_proj, col_mile = st.columns(2)
            with col_proj:
                new_is_project = st.checkbox("Project", value=ascent.is_project)
            with col_mile:
                new_is_milestone = st.checkbox("Milestone", value=ascent.is_milestone)

        col_lat, col_lon = st.columns(2)
        with col_lat:
            new_latitude = st.number_input("Latitude", format="%.6f",
                                          value=float(route.latitude) if route.latitude else 0.0)
        with col_lon:
            new_longitude = st.number_input("Longitude", format="%.6f",
                                           value=float(route.longitude) if route.longitude else 0.0)

        new_notes = st.text_area("Notes", value=ascent.notes if ascent.notes else "")
        new_gear = st.text_input("Gear", value=ascent.gear if ascent.gear else "")

        new_ernsthaftigkeit = None
        new_length = None
        new_ascent_time = None
        if route.discipline == "Multipitch":
            new_ernsthaftigkeit = st.selectbox(
                "Ernsthaftigkeit",
                ["", "R", "X"]
            )
            new_length = st.number_input("Length (m)", min_value=0,
                                        value=int(route.length) if route.length else 0, step=10)
            new_ascent_time = st.number_input("Ascent Time (hours)", min_value=0.0,
                                             value=float(ascent.ascent_time) if ascent.ascent_time else 0.0, step=0.5)

            st.info("💡 To edit individual pitch ascents, delete and recreate the route (pitch editing coming soon)")

        update_submitted = st.form_submit_button("Update Ascent", type="primary")

        if update_submitted:
            try:
                update_params = {
                    'ascent_id': ascent.id,
                    'grade': new_grade,
                    'style': new_style if new_style else None,
                    'stars': new_stars,
                    'date': new_date,
                    'is_project': new_is_project,
                    'is_milestone': new_is_milestone,
                    'shortnote': new_shortnote if new_shortnote else None,
                    'notes': new_notes if new_notes else None,
                    'gear': new_gear if new_gear else None,
                    'latitude': new_latitude if new_latitude != 0.0 else None,
                    'longitude': new_longitude if new_longitude != 0.0 else None,
                    'ernsthaftigkeit': new_ernsthaftigkeit,
                    'length': new_length,
                    'ascent_time': new_ascent_time
                }

                db.update_ascent(route_id=route.id, **update_params)
                st.success(f"✅ Updated: {route.name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating route: {e}")


def _render_delete_confirmation(db, ascent):
    """Render delete confirmation."""
    route = ascent.route

    st.markdown(f"### Delete: {route.name}")
    st.warning(f"⚠️ This will permanently delete **{route.name}** ({ascent.grade})")

    if route.discipline == "Multipitch" and ascent.pitch_ascents:
        st.info(f"This will also delete your {len(ascent.pitch_ascents)} associated pitch ascents")

    confirm = st.text_input("Type the route name to confirm deletion:", key=f"delete_confirm_{ascent.id}")

    col1, col2 = st.columns(2)

    with col1:
        # Change to regular button (not form_submit_button)
        if st.button("🗑️ Delete Permanently", type="primary",
                     disabled=(confirm != route.name),
                     key=f"delete_btn_{route.id}"):
            try:
                db.delete_ascent(ascent.id)
                st.success(f"✅ Deleted your ascent of: {route.name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting route: {e}")

    with col2:
        st.markdown("")


def _render_multipitch_fields(grade_options, style_options, shortnote_options, existing_route=None):
    """Render multipitch fields with full pitch details."""
    col_len, col_pitches = st.columns(2)
    with col_len:
        default_length = int(existing_route.length) if existing_route and existing_route.length else 0
        length = st.number_input("Total Length (m)", min_value=0, step=10, value=default_length)
    with col_pitches:
        default_pitches = len(existing_route.pitches) if existing_route and existing_route.pitches else 3
        num_pitches = st.number_input("Number of Pitches", min_value=1, step=1, value=default_pitches)

    col_ernst, col_time = st.columns(2)
    with col_ernst:
        ernsthaftigkeit = st.selectbox("Ernsthaftigkeit (overall)", ["", "R", "X"])
    with col_time:
        ascent_time = st.number_input("Ascent Time (hours)", min_value=0.0, step=0.5)

    with st.expander("⛰️ Detailed Pitch Information", expanded=False):
        st.markdown("Enter complete details for each pitch:")

        pitches_list = []
        for i in range(int(num_pitches)):
            st.markdown(f"### Pitch {i+1}")

            # Auto-populate from existing pitch
            default_pitch_grade_idx = 0
            default_pitch_length = 0
            default_pitch_name = ""
            if existing_route and existing_route.pitches:
                pitch = existing_route.pitches[i]
                if pitch.pitch_consensus_grade in grade_options:
                    default_pitch_grade_idx = grade_options.index(pitch.pitch_consensus_grade)
                default_pitch_length = pitch.pitch_length
                default_pitch_name = pitch.pitch_name

            col1, col2, col3 = st.columns(3)
            with col1:
                pitch_grade = st.selectbox("Grade", grade_options,
                                           key=f"pitch_grade_{i}", index=default_pitch_grade_idx)
                pitch_name = st.text_input("Name", key=f"pitch_name_{i}", placeholder="e.g., Crux pitch",
                                           value=default_pitch_name)

            with col2:
                pitch_style = st.selectbox("Style", [""] + style_options, key=f"pitch_style_{i}")
                pitch_led = st.checkbox("Led (uncheck if followed)", value=True, key=f"pitch_led_{i}")

            with col3:
                pitch_stars = st.selectbox("Stars", [0, 1, 2, 3, 4, 5], key=f"pitch_stars_{i}")
                pitch_length = st.number_input("Length (m)", min_value=0, key=f"pitch_length_{i}",
                                               value=default_pitch_length)

            col4, col5 = st.columns(2)
            with col4:
                pitch_ernst = st.selectbox("Ernsthaftigkeit", ["", "R", "X"], key=f"pitch_ernst_{i}")
            with col5:
                pitch_shortnote = st.multiselect("Note", shortnote_options, key=f"pitch_shortnote_{i}")

            pitch_notes = st.text_area("Pitch Notes", key=f"pitch_notes_{i}",
                                      placeholder="Detailed notes for this pitch")
            pitch_gear = st.text_input("Pitch Gear", key=f"pitch_gear_{i}",
                                      placeholder="Specific gear for this pitch")

            pitches_list.append({
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

    return ernsthaftigkeit, ascent_time, length, pitches_list


def _handle_form_submission(db, discipline, name, country, area, crag, length, route_data):
    """Handle form submission and route creation."""
    errors = validate_route_data(name, route_data['grade'], area, crag, country)
    if errors:
        for error in errors:
            st.error(error)
        return

    try:
        ascent = db.add_ascent(
            name=name,
            grade=route_data['grade'],
            discipline=discipline,
            crag_name=crag,
            area_name=area,
            country_name=country,
            style=route_data['style'],
            date=route_data['climb_date'],
            stars=route_data['stars'],
            shortnote=route_data['shortnote'],
            notes=route_data['notes'],
            gear=route_data['gear'],
            latitude=route_data['latitude'],
            longitude=route_data['longitude'],
            is_project=route_data['is_project'],
            is_milestone=route_data['is_milestone'],
            ernsthaftigkeit=route_data['ernsthaftigkeit'],
            length=length,
            pitches=route_data['pitches'],
            ascent_time=route_data['ascent_time']
        )

        st.success(f"✅ Successfully added: {ascent.route.name} ({ascent.grade})")
        st.cache_resource.clear()
        st.rerun()

    except ValueError as e:
        st.error(f"Validation error: {e}")
    except Exception as e:
        st.error("Failed to add route.")
        st.error(f"Details: {str(e)}")