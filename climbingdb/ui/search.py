"""
Route search functionality with autocomplete.
"""

import streamlit as st
from sqlalchemy import or_
from climbingdb.models import Route, Crag, Area, Ascent
from climbingdb.ui.navigation import DISCIPLINE_ICONS


def _search_routes(db, search_term, limit=20):
    if not search_term or len(search_term) < 2:
        return [], 0

    base_query = db.session.query(Route) \
        .join(Route.crag) \
        .join(Crag.area) \
        .filter(
        or_(
            Route.name.ilike(f"%{search_term}%"),
            Crag.name.ilike(f"%{search_term}%"),
            Area.name.ilike(f"%{search_term}%")
        )
    ).order_by(
        Route.consensus_ole_grade.desc().nullslast()
    )

    # Get total count (no limit), data not yet transferred
    total_count = base_query.count()

    # Get limited results (lazy loading)
    results = base_query.limit(limit).all()

    return results, total_count


def _format_route_option(route):
    """Format route for display in selectbox."""
    crag = route.crag.name if route.crag else "Unknown"
    area = route.crag.area.name if route.crag and route.crag.area else "Unknown"
    grade = route.consensus_grade or "?"
    return f"{route.discipline.upper()}: {route.name} ({grade}) - {crag}, {area}"


def render_search(db):
    """Render search bar with autocomplete-style results."""
    col_spacer, col1, col2 = st.columns([3, 1.1, 2.5])
    with col1:
        st.markdown("#### :material/search: Search Routes")
    with col2:
        search_term = st.text_input(
            "Search by route name, crag, or area",
            placeholder="e.g., Action Directe or Frankenjura",
            key="route_search_input",
            label_visibility="collapsed"
        )

    if not search_term:
        return

    if len(search_term) < 2:
        st.caption("Type at least 2 characters to search")
        return

    limit = 20
    results, total_count = _search_routes(db, search_term, limit=limit)

    if not results:
        st.warning(f"No routes found matching '{search_term}'")
        return

    # Show count with limit warning if needed
    if total_count > limit:
        st.caption(f"Found {total_count} routes. Refine your search to narrow results.")
        return
    else:
        with col2:
            st.caption(f"Found {total_count} route(s)")

    # Display results as selectbox (autocomplete-style)
    options = {_format_route_option(r): r for r in results}
    with col2:
        selected_label = st.selectbox(
        "Select route",
        [""] + list(options.keys()),
        key="route_search_select",
        label_visibility="collapsed"
        )

    if selected_label and selected_label != "":
        selected_route = options[selected_label]
        st.query_params['route_id'] = str(selected_route.id)
        st.session_state.previous_view = st.session_state.get('view', 'Sportclimb')
        st.session_state.view = "RouteDetail"
        st.session_state.detail_route_id = selected_route.id
        st.rerun()
