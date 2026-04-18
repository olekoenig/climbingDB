"""
Main form rendering for adding/editing routes.
"""

import streamlit as st

from .location_selector import render_location_selector, get_existing_route_data
from .form_helpers import (
    get_grade_system_options,
    validate_route_data,
    render_gps_fields,
    render_multipitch_fields,
    render_ascent_misc_fields,
    render_grade_field,
    get_grade_options,
    get_style_options,
    get_shortnote_options
)
from climbingdb.grade import Grade


def render_add_route_form(db, discipline):
    with st.expander(f":material/add: Add New {discipline}", expanded=False):
        country, area, crag, name = render_location_selector(db, discipline)

        # Fetch existing route data for auto-population (could be None)
        existing_route = get_existing_route_data(db, name, crag, discipline)

        grade_systems = get_grade_system_options(discipline)
        grade_system = st.selectbox("Grading System", grade_systems, key="add_grade_system")

        # Multipitch num_pitches needs to be outside form for interactivity
        num_pitches = None
        if discipline == "Multipitch":
            num_pitches = st.number_input("Number of Pitches", min_value=1, step=1, key="add_num_pitches")

        with st.form("add_route_form", clear_on_submit=True):
            # Get route-specific data; num_pitches needs to be passed because it's non-interactive
            # once in the form, and we want the number of pitches to be set correctly
            route_data = _render_add_route_fields(discipline, grade_system, existing_route=existing_route,
                                              num_pitches=num_pitches)

            submitted = st.form_submit_button(f"Add {discipline}", type="primary", width='stretch')

            if submitted:
                _handle_add_route_form_submission(db, discipline, name, country, area, crag, route_data)


def _render_add_route_fields(discipline, grade_system, existing_route=None, num_pitches=None):
    """Render form fields for route details."""
    grade_options = get_grade_options(grade_system)
    grade = render_grade_field(grade_options, route=existing_route)

    style_options = get_style_options(discipline)
    shortnote_options = get_shortnote_options(discipline)

    style, stars, shortnote, climb_date, is_project, is_milestone, notes, gear = (
        render_ascent_misc_fields(discipline, style_options, shortnote_options))

    latitude, longitude = render_gps_fields(route=existing_route)

    length = ernsthaftigkeit = ascent_time = pitches = None
    if discipline == "Multipitch":
        length, ernsthaftigkeit, ascent_time, pitches = render_multipitch_fields(
            grade_options, style_options, shortnote_options, route=existing_route, num_pitches=num_pitches
        )

    return {
        'grade': grade,
        'shortnote': shortnote,
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


def _handle_add_route_form_submission(db, discipline, name, country, area, crag, route_data):
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
            length=route_data['length'],
            pitches=route_data['pitches'],
            ascent_time=route_data['ascent_time']
        )

        st.success(f":material/check: Successfully added: {ascent.route.name} ({ascent.grade})")
        #st.cache_resource.clear()
        st.rerun()

    except ValueError as e:
        st.error(f"Validation error: {e}")
    except Exception as e:
        st.error("Failed to add route.")
        st.error(f"Details: {str(e)}")


def render_edit_delete_form(db, routes_df):
    if len(routes_df) == 0:
        st.info("No routes to edit. Adjust filters or add a new route.")
        return

    route_options = [
        f"{name} ({grade}) - {crag}"
        for name, grade, crag in zip(routes_df['name'], routes_df['grade'], routes_df['crag'])
    ]

    with st.expander(":material/edit: Edit or Delete Routes"):
        selected_idx = st.selectbox("Select Route to Edit/Delete", range(len(route_options)),
                                    format_func=lambda i: route_options[i])
        # Hack to typecast numpy.int64 (from the pandas dataframe) to python-integer
        ascent_id = int(routes_df.iloc[selected_idx]['id'])
        ascent = db.get_ascent_by_id(ascent_id)

        if not ascent:
            st.error("Ascent not found!")
            return

        tab1, tab2 = st.tabs([":material/edit: Edit", ":material/delete: Delete"])

        with tab1:
            _render_edit_fields(db, ascent)

        with tab2:
            _render_delete_confirmation(db, ascent)


def _render_edit_fields(db, ascent):
    """Render edit form for an ascent."""
    route = ascent.route
    discipline = st.session_state.view

    with (st.form(f"edit_route_form_{ascent.id}")):
        st.text_input("Route Name", value=route.name, disabled=True)

        grade_system = Grade(route.consensus_grade).get_scale()
        grade_options = get_grade_options(grade_system)
        new_grade = render_grade_field(grade_options, route=route)

        style_options = get_style_options(discipline)
        shortnote_options = get_shortnote_options(discipline)

        new_style, new_stars, new_shortnote, new_date, new_is_project, new_is_milestone, new_notes, new_gear = (
            render_ascent_misc_fields(discipline, style_options, shortnote_options, ascent=ascent))

        new_latitude, new_longitude = render_gps_fields(route=route)

        new_ernsthaftigkeit = new_length = new_ascent_time = pitch_updates = None
        if route.discipline == "Multipitch":
            num_pitches = len(route.pitches)
            new_length, new_ernsthaftigkeit, new_ascent_time, pitch_updates = (
            render_multipitch_fields(grade_options, style_options, shortnote_options, num_pitches,
                             route=route, ascent=ascent))

        update_submitted = st.form_submit_button("Update Ascent", type="primary")

        if update_submitted:
            try:
                db.update_ascent(
                    ascent_id=ascent.id,
                    grade=new_grade,
                    style=new_style if new_style else None,
                    stars=new_stars,
                    date=new_date,
                    is_project=new_is_project,
                    is_milestone=new_is_milestone,
                    shortnote=new_shortnote if new_shortnote else None,
                    notes=new_notes if new_notes else None,
                    gear=new_gear if new_gear else None,
                    latitude=new_latitude,
                    longitude=new_longitude,
                    ernsthaftigkeit=new_ernsthaftigkeit,
                    length=new_length,
                    ascent_time=new_ascent_time
                )

                if pitch_updates:
                    db.update_pitch_ascents(pitch_updates)

                st.success(f":material/check: Updated: {route.name}")
                st.session_state.show_edit_form = False
                st.rerun()

            except Exception as e:
                st.error(f"Error updating: {e}")


def _render_delete_confirmation(db, ascent):
    """Render delete confirmation."""
    route = ascent.route

    st.markdown(f"### Delete: {route.name}")
    st.warning(f":material/release_alert: This will permanently delete **{route.name}** ({ascent.grade})")

    if route.discipline == "Multipitch" and ascent.pitch_ascents:
        st.info(f"This will also delete your {len(ascent.pitch_ascents)} associated pitch ascents")

    confirm = st.text_input("Type the route name to confirm deletion:", key=f"delete_confirm_{ascent.id}")

    col1, col2 = st.columns(2)

    with col1:
        # Change to regular button (not form_submit_button)
        if st.button(":material/delete: Delete Permanently", type="primary",
                     disabled=(confirm != route.name),
                     key=f"delete_btn_{route.id}"):
            try:
                db.delete_ascent(ascent.id)
                st.success(f":material/check: Deleted your ascent of: {route.name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting route: {e}")

    with col2:
        st.markdown("")

