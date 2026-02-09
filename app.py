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
    render_add_route_form
)


@st.cache_resource
def load_database():
    """Load and cache the climbing database."""
    return ClimbingService()


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

    # Initialize session state
    if 'view' not in st.session_state:
        st.session_state.view = 'Sportclimb'

    db = load_database()

    # Render UI
    st.title("🧗 My Climbing Logbook")
    st.markdown("---")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    render_navigation_buttons()
    filters = render_sidebar_filters(db)
    routes = fetch_routes(db, filters)

    if len(routes) > 0:
        routes = convert_grades(routes, filters['grade_system'])
        render_add_route_form(db, st.session_state.view)
        render_dashboard(routes)
        render_routes_table(routes)
    else:
        st.warning("No routes match your filters. Try adjusting the filter criteria.")

    render_filter_summary(filters)


if __name__ == '__main__':
    main()