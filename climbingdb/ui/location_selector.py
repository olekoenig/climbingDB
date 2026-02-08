"""
Location selection widgets with autocomplete and filtering.
"""

import streamlit as st
from sqlalchemy import and_
from climbingdb.models import Country, Area, Crag, Route


def render_location_selector(db, discipline):
    """
    Render cascading location selector (Country → Area → Crag → Route).
    
    Returns:
        tuple: (country, area, crag, name)
    """
    country = _render_country_selector(db, discipline)
    area = _render_area_selector(db, discipline, country)
    crag = _render_crag_selector(db, discipline, country, area)
    name = _render_route_selector(db, discipline, country, area, crag)
    
    return country, area, crag, name


def _render_country_selector(db, discipline):
    """Render country selection with add new option."""
    col1, col2 = st.columns(2)

    with col1:
        existing_countries = [c.name for c in db.session.query(Country)
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
        query = db.session.query(Area).join(Crag.area).join(Crag.routes)
        filters = [Route.discipline == discipline]
        
        if country_filter:
            query = query.join(Area.country)
            filters.append(Country.name == country_filter)
        
        existing_areas = [a.name for a in query.filter(and_(*filters)).distinct().order_by(Area.name).all()]
        area_select = st.selectbox("Area", [""] + existing_areas, key="area_select_existing")
    
    with col2:
        area_new = st.text_input("Add new area", key="area_new_input")
    
    return area_new if area_new else area_select


def _render_crag_selector(db, discipline, country_filter, area_filter):
    """Render crag selection filtered by country and area."""
    col1, col2 = st.columns(2)
    
    with col1:
        query = db.session.query(Crag).join(Crag.area).join(Crag.routes)
        filters = [Route.discipline == discipline]
        
        if area_filter:
            filters.append(Area.name == area_filter)
        if country_filter:
            query = query.join(Area.country)
            filters.append(Country.name == country_filter)
        
        existing_crags = [c.name for c in query.filter(and_(*filters)).distinct().order_by(Crag.name).all()]
        crag_select = st.selectbox("Crag", [""] + existing_crags, key="crag_select_existing")
    
    with col2:
        crag_new = st.text_input("Add new crag", key="crag_new_input")
    
    return crag_new if crag_new else crag_select


def _render_route_selector(db, discipline, country_filter, area_filter, crag_filter):
    """Render route selection filtered by location."""
    col1, col2 = st.columns(2)
    
    with col1:
        query = db.session.query(Route)
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
        
        existing_routes = [r.name for r in query.filter(and_(*filters)).distinct().order_by(Route.name).all()]
        route_select = st.selectbox("Route", [""] + existing_routes, key="route_select_existing")
    
    with col2:
        route_new = st.text_input("Add new route", key="route_new_input")
    
    return route_new if route_new else route_select
