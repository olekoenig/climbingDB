"""
Streamlit climbing logbook application.

Run as:
    streamlit run app.py
"""

import streamlit as st
from climbingdb.services import ClimbingService
from climbingdb.ui import (
    CUSTOM_CSS,
    render_navigation_buttons,
    render_sidebar_filters,
    render_filter_summary,
    render_dashboard,
    render_routes_table,
    convert_grades,
    render_add_route_form,
    render_edit_delete_form
)
from climbingdb.ui.auth import (
    require_authentication,
    render_user_menu,
    render_settings_page
)
from climbingdb.config import REQUIRE_AUTH


@st.cache_resource
def load_database(_user_id):
    """Load and cache the climbing database."""
    return ClimbingService(user_id=_user_id)


def fetch_routes(db, filters):
    """Fetch routes based on current view and filters."""
    if st.session_state.view == "Projects":
        return db.get_projects(area=filters['area'])
    return db.get_filtered_routes(
        discipline=st.session_state.view,
        area=filters['area'],
        grade=filters['grade'],
        stars=filters['stars'],
        operation=filters['grade_operation']
    )


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="My Climbing Routes",
        page_icon="🧗",
        layout="wide"
    )

    if REQUIRE_AUTH:
        if not require_authentication():
            return
        user_id = st.session_state.user_id
    else:
        user_id = 1
        st.info("📺 Demo Mode - Viewing Lauchinger's climbing logbook")

    db = load_database(user_id)

    # Check if showing settings page
    if st.session_state.get('show_settings', False):
        render_settings_page()
        return

    # Initialize session state
    if 'view' not in st.session_state:
        st.session_state.view = 'Sportclimb'

    # Render UI
    st.title("🧗 My Climbing Logbook")
    st.markdown("---")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    render_navigation_buttons()
    filters = render_sidebar_filters(db)
    with st.spinner("Loading your routes..."):
        routes = fetch_routes(db, filters)

    if len(routes) > 0:
        routes = convert_grades(routes, filters['grade_system'])
        render_dashboard(routes)
        if REQUIRE_AUTH:
            render_add_route_form(db, st.session_state.view)
            render_edit_delete_form(db, routes)
        render_routes_table(routes)
    else:
        st.warning("No routes match your filters. Try adjusting the filter criteria or add a route.")
        render_add_route_form(db, st.session_state.view)

    render_filter_summary(filters)

    if REQUIRE_AUTH:
        render_user_menu()


if __name__ == '__main__':
    main()