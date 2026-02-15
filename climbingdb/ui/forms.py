"""
Main form rendering for adding/editing routes.
"""

import streamlit as st
from datetime import date

from .location_selector import render_location_selector
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

        length = None
        num_pitches = 3
        if discipline == "Multipitch":
            col_len, col_pitches = st.columns(2)
            with col_len:
                length = st.number_input("Total Length (m)", min_value=0, step=10)
            with col_pitches:
                num_pitches = st.number_input("Number of Pitches", min_value=1, value=3, step=1)

        with st.form("add_route_form", clear_on_submit=True):
            route_data = _render_route_fields(
                discipline, grade_system, num_pitches if discipline == "Multipitch" else None
            )

            submitted = st.form_submit_button(f"Add {discipline}", type="primary", use_container_width=True)

            if submitted:
                _handle_form_submission(db, discipline, name, country, area, crag, length, route_data)


def _render_route_fields(discipline, grade_system, num_pitches=None):
    """Render form fields for route details."""
    grade_options = get_grade_options(grade_system)
    style_options = get_style_options(discipline)
    shortnote_options = get_shortnote_options(discipline)

    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("Grade", grade_options)
        style = st.selectbox("Style", [""] + style_options + ["FA"]) if discipline != "Projects" else None
        stars = st.selectbox("Stars", [0, 1, 2, 3], index=0)

    with col2:
        shortnote = st.multiselect("Short Note", shortnote_options)
        climb_date = st.date_input("Date", value=date.today()) if discipline != "Projects" else None
        col_proj, col_mile = st.columns(2)
        with col_proj:
            is_project = st.checkbox("Project")
        with col_mile:
            is_milestone = st.checkbox("Milestone")

    col_lat, col_lon = st.columns(2)
    with col_lat:
        latitude = st.number_input("Latitude", format="%.6f", value=0.0, help="GPS coordinate")
    with col_lon:
        longitude = st.number_input("Longitude", format="%.6f", value=0.0, help="GPS coordinate")

    latitude = latitude if latitude != 0.0 else None
    longitude = longitude if longitude != 0.0 else None

    notes = st.text_area("Notes", placeholder="Detailed description...")
    gear = st.text_input("Gear", placeholder="e.g., 10 quickdraws, cams #0.5-3") if discipline != "Boulder" else None

    ernsthaftigkeit = None
    pitches = None
    ascent_time = None
    if discipline == "Multipitch":
        ernsthaftigkeit, ascent_time, pitches = _render_multipitch_fields(num_pitches, grade_options, style_options, shortnote_options)

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
        'ascent_time': ascent_time,
        'pitch_number': num_pitches
    }


def _render_multipitch_fields(num_pitches, grade_options, style_options, shortnote_options):
    """Render multipitch-specific fields including detailed pitch information."""
    col_ernst, col_time = st.columns(2)
    with col_ernst:
        ernsthaftigkeit = st.selectbox("Ernsthaftigkeit", ["", "R", "X"])
    with col_time:
        ascent_time = st.number_input("Ascent Time (hours)", min_value=0.0, step=0.5)

    with st.expander("⛰️ Pitch Details", expanded=False):
        st.markdown("Enter details for each pitch:")

        pitches_list = []
        for i in range(int(num_pitches)):
            st.markdown(f"**Pitch {i+1}**")

            col1, col2, col3 = st.columns(3)

            with col1:
                pitch_grade = st.selectbox(f"Grade", grade_options, key=f"pitch_grade_{i}", label_visibility="collapsed")
                pitch_style = st.selectbox(f"Style", [""] + style_options, key=f"pitch_style_{i}", label_visibility="collapsed")

            with col2:
                pitch_led = st.checkbox("Led", value=True, key=f"pitch_led_{i}")
                pitch_stars = st.selectbox("Stars", [0, 1, 2, 3], key=f"pitch_stars_{i}", label_visibility="collapsed")

            with col3:
                pitch_length = st.number_input("Length (m)", min_value=0, key=f"pitch_length_{i}", label_visibility="collapsed")
                pitch_ernst = st.selectbox("Ernst", ["", "R", "X"], key=f"pitch_ernst_{i}", label_visibility="collapsed")

            pitch_name = st.text_input("Pitch Name", key=f"pitch_name_{i}", placeholder="e.g., Crux pitch")
            pitch_shortnote = st.multiselect("Note", shortnote_options, key=f"pitch_shortnote_{i}")
            pitch_notes = st.text_area("Notes", key=f"pitch_notes_{i}", placeholder="Details about this pitch")
            pitch_gear = st.text_input("Gear", key=f"pitch_gear_{i}", placeholder="Gear for this pitch")

            pitches_list.append({
                "grade": pitch_grade if pitch_grade else None,
                "led": pitch_led,
                "style": pitch_style if pitch_style else None,
                "stars": pitch_stars,
                "pitch_length": pitch_length if pitch_length > 0 else None,
                "pitch_name": pitch_name if pitch_name else None,
                "ernsthaftigkeit": pitch_ernst if pitch_ernst else None,
                "shortnote": ', '.join(pitch_shortnote) if pitch_shortnote else None,
                "notes": pitch_notes if pitch_notes else None,
                "gear": pitch_gear if pitch_gear else None
            })

            if i < int(num_pitches) - 1:
                st.markdown("---")

    return ernsthaftigkeit, ascent_time, pitches_list


def _handle_form_submission(db, discipline, name, country, area, crag, length, route_data):
    """Handle form submission and route creation."""
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
            ascent_time=route_data['ascent_time'],
            pitch_number=route_data['pitch_number']
        )

        st.success(f"✅ Successfully added: {route.name} ({route.grade})")

    except Exception as e:
        st.error(f"Error adding route: {e}")


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
        route_id = int(routes_df.iloc[selected_idx]['id'])
        route = db.get_route_by_id(route_id)

        if not route:
            st.error("Route not found!")
            return

        tab1, tab2 = st.tabs(["✏️ Edit", "🗑️ Delete"])

        with tab1:
            _render_edit_form(db, route)

        with tab2:
            _render_delete_confirmation(db, route)


def _render_edit_form(db, route):
    """Render edit form for a route."""
    with st.form(f"edit_route_form_{route.id}"):
        col1, col2 = st.columns(2)

        with col1:
            new_name = st.text_input("Name", value=route.name)
            new_grade = st.text_input("Grade", value=route.grade)
            new_style = st.text_input("Style", value=route.style if route.style else "")
            new_stars = st.selectbox("Stars", [0, 1, 2, 3], index=int(route.stars))

        with col2:
            new_date = st.date_input("Date", value=route.date if route.date else date.today())
            new_shortnote = st.text_input("Short Note", value=route.shortnote if route.shortnote else "")
            col_proj, col_mile = st.columns(2)
            with col_proj:
                new_is_project = st.checkbox("Project", value=route.is_project)
            with col_mile:
                new_is_milestone = st.checkbox("Milestone", value=route.is_milestone)

        col_lat, col_lon = st.columns(2)
        with col_lat:
            new_latitude = st.number_input("Latitude", format="%.6f",
                                          value=float(route.latitude) if route.latitude else 0.0)
        with col_lon:
            new_longitude = st.number_input("Longitude", format="%.6f",
                                           value=float(route.longitude) if route.longitude else 0.0)

        new_notes = st.text_area("Notes", value=route.notes if route.notes else "")
        new_gear = st.text_input("Gear", value=route.gear if route.gear else "")

        new_ernsthaftigkeit = None
        if route.discipline == "Multipitch":
            new_ernsthaftigkeit = st.selectbox(
                "Ernsthaftigkeit",
                ["", "R", "X"],
                index=["", "R", "X"].index(route.ernsthaftigkeit) if route.ernsthaftigkeit else 0
            )
            new_length = st.number_input("Length (m)", min_value=0,
                                        value=int(route.length) if route.length else 0, step=10)
            new_ascent_time = st.number_input("Ascent Time (hours)", min_value=0.0,
                                             value=float(route.ascent_time) if route.ascent_time else 0.0, step=0.5)

            st.info("💡 To edit individual pitches, delete and recreate the route (pitch editing coming soon)")

        update_submitted = st.form_submit_button("Update Route", type="primary")

        if update_submitted:
            try:
                update_params = {
                    'name': new_name,
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
                    'longitude': new_longitude if new_longitude != 0.0 else None
                }

                if route.discipline == "Multipitch":
                    update_params['ernsthaftigkeit'] = new_ernsthaftigkeit if new_ernsthaftigkeit else None
                    update_params['length'] = new_length if new_length > 0 else None
                    update_params['ascent_time'] = new_ascent_time if new_ascent_time > 0 else None

                db.update_route(route_id=route.id, **update_params)
                st.success(f"✅ Updated: {new_name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating route: {e}")


def _render_delete_confirmation(db, route):
    """Render delete confirmation."""
    st.markdown(f"### Delete: {route.name}")
    st.warning(f"⚠️ This will permanently delete **{route.name}** ({route.grade})")

    if route.discipline == "Multipitch" and route.pitches:
        st.info(f"This will also delete {len(route.pitches)} associated pitches")

    confirm = st.text_input("Type the route name to confirm deletion:", key=f"delete_confirm_{route.id}")

    col1, col2 = st.columns(2)

    with col1:
        # Change to regular button (not form_submit_button)
        if st.button("🗑️ Delete Permanently", type="primary",
                     disabled=(confirm != route.name),
                     key=f"delete_btn_{route.id}"):
            try:
                db.delete_route(route.id)
                st.success(f"✅ Deleted: {route.name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting route: {e}")

    with col2:
        st.markdown("")  # Spacing


def _render_multipitch_fields(num_pitches, grade_options, style_options, shortnote_options):
    """Render multipitch fields with full pitch details."""
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

            col1, col2, col3 = st.columns(3)

            with col1:
                pitch_grade = st.selectbox("Grade", grade_options, key=f"pitch_grade_{i}")
                pitch_name = st.text_input("Name", key=f"pitch_name_{i}", placeholder="e.g., Crux pitch")

            with col2:
                pitch_style = st.selectbox("Style", [""] + style_options, key=f"pitch_style_{i}")
                pitch_led = st.checkbox("Led (uncheck if followed)", value=True, key=f"pitch_led_{i}")

            with col3:
                pitch_stars = st.selectbox("Stars", [0, 1, 2, 3], key=f"pitch_stars_{i}")
                pitch_length = st.number_input("Length (m)", min_value=0, key=f"pitch_length_{i}")

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
                "grade": pitch_grade if pitch_grade else None,
                "led": pitch_led,
                "style": pitch_style if pitch_style else None,
                "stars": pitch_stars,
                "pitch_length": pitch_length if pitch_length > 0 else None,
                "pitch_name": pitch_name if pitch_name else None,
                "ernsthaftigkeit": pitch_ernst if pitch_ernst else None,
                "shortnote": ', '.join(pitch_shortnote) if pitch_shortnote else None,
                "notes": pitch_notes if pitch_notes else None,
                "gear": pitch_gear if pitch_gear else None
            })

            if i < int(num_pitches) - 1:
                st.markdown("---")

    return ernsthaftigkeit, ascent_time, pitches_list


def _handle_form_submission(db, discipline, name, country, area, crag, length, route_data):
    """Handle form submission and route creation."""
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
            ascent_time=route_data['ascent_time'],
            pitch_number=route_data['pitch_number']
        )

        st.success(f"✅ Successfully added: {route.name} ({route.grade})")

    except Exception as e:
        st.error(f"Error adding route: {e}")