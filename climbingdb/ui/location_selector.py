"""
Location selection widgets with autocomplete and filtering.
"""

import streamlit as st
from sqlalchemy import and_
from climbingdb.models import Country, Area, Crag, Route
from climbingdb.grade import Grade


def render_location_selector(db, discipline):
    country = _render_country_selector(db, discipline)
    area = _render_area_selector(db, discipline, country)
    crag = _render_crag_selector(db, discipline, country, area)
    name = _render_route_selector(db, discipline, country, area, crag)
    
    return country, area, crag, name


def _render_country_selector(db, discipline):
    """Render country selection with add new option."""
    col1, col2 = st.columns(2)

    with col1:
        existing_countries = [name for (name,) in db.session.query(Country.name)
            .join(Country.areas)
            .join(Area.crags)
            .join(Crag.routes)
            .filter(Route.discipline == discipline)
            .distinct()
            .order_by(Country.name).all()]
        country_select = st.selectbox("Country", [""] + existing_countries, key="country_select_existing")

    with col2:
        country_new = st.text_input("Add new country", key="country_new_input")
    
    return country_new if country_new else country_select


def _render_area_selector(db, discipline, country_filter):
    """Render area selection filtered by country."""
    col1, col2 = st.columns(2)
    
    with col1:
        query = db.session.query(Area.name).join(Crag.area).join(Crag.routes)
        filters = [Route.discipline == discipline]
        
        if country_filter:
            query = query.join(Area.country)
            filters.append(Country.name == country_filter)
        
        existing_areas = [name for (name,) in query.filter(and_(*filters)).distinct().order_by(Area.name).all()]
        area_select = st.selectbox("Area", [""] + existing_areas, key="area_select_existing")
    
    with col2:
        area_new = st.text_input("Add new area", key="area_new_input")
    
    return area_new if area_new else area_select


def _render_crag_selector(db, discipline, country_filter, area_filter):
    """Render crag selection filtered by country and area."""
    col1, col2 = st.columns(2)
    
    with col1:
        query = db.session.query(Crag.name).join(Crag.area).join(Crag.routes)
        filters = [Route.discipline == discipline]
        
        if area_filter:
            filters.append(Area.name == area_filter)
        if country_filter:
            query = query.join(Area.country)
            filters.append(Country.name == country_filter)
        
        existing_crags = [name for (name,) in query.filter(and_(*filters)).distinct().order_by(Crag.name).all()]
        crag_select = st.selectbox("Crag", [""] + existing_crags, key="crag_select_existing")
    
    with col2:
        crag_new = st.text_input("Add new crag", key="crag_new_input")
    
    return crag_new if crag_new else crag_select


def _render_route_selector(db, discipline, country_filter, area_filter, crag_filter):
    """Render route selection filtered by location."""
    col1, col2 = st.columns(2)
    
    with col1:
        query = db.session.query(Route.name).distinct()
        filters = [Route.discipline == discipline]
        
        if crag_filter:
            query = query.join(Route.crag)
            filters.append(Crag.name == crag_filter)
        if area_filter:
            query = query.join(Route.crag).join(Crag.area)
            filters.append(Area.name == area_filter)
        if country_filter:
            query = query.join(Route.crag).join(Crag.area).join(Area.country)
            filters.append(Country.name == country_filter)

        existing_routes = [name for (name,) in query.filter(and_(*filters)).distinct().order_by(Route.name).all()]
        route_select = st.selectbox("Route", [""] + existing_routes, key="route_select_existing")
    
    with col2:
        route_new = st.text_input("Add new route", key="route_new_input")
    
    return route_new if route_new else route_select


def get_existing_route_data(db, route_name, crag_name, discipline):
    """Fetch existing route data for auto-population."""
    if not route_name or not crag_name:
        return None

    route = db.session.query(Route).join(Route.crag).filter(
        Route.name == route_name,
        Crag.name == crag_name,
        Route.discipline == discipline
    ).first()

    if not route:
        return None

    # Need to set these parameters into the session state such that the form
    # can access it later for auto-population.
    default_grade_system = Grade(route.consensus_grade).get_scale()
    if st.session_state.get('last_selected_route') != route.name:
        st.session_state['add_grade_system'] = default_grade_system
        st.session_state['last_selected_route'] = route.name
        if discipline == "Multipitch" and route.pitches:
            st.session_state['add_num_pitches'] = len(route.pitches)

    return route