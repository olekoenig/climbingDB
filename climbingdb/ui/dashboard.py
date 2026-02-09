"""
Dashboard components - metrics and visualizations.
"""

import streamlit as st
import matplotlib.pyplot as plt
from climbingdb.visualizations import plot_grade_pyramid, plot_multipitches
from .constants import GRADE_OPTIONS_ROUTES, GRADE_OPTIONS_BOULDERS


def render_dashboard(routes):
    """Render complete dashboard with metrics and visualizations."""
    render_area_metrics(routes)
    st.markdown("---")
    render_visualizations(routes)
    render_grade_metrics(routes)
    st.markdown("---")


def render_area_metrics(routes):
    """Render area/location metrics."""
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("Total Routes", len(routes)),
        ("Crags", routes['crag'].nunique()),
        ("Areas", routes['area'].nunique()),
        ("Countries", routes['country'].nunique())
    ]
    
    for col, (label, value) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.metric(label, value)


def render_grade_metrics(routes):
    """Render grade-based metrics (hardest, onsight, flash)."""
    if len(routes) == 0:
        return
    
    routes_sorted = routes.sort_values(by="ole_grade", ascending=False)
    
    col1, col2, col3 = st.columns(3)
    
    hardest_grade = routes_sorted.iloc[0]['grade']
    
    flash_routes = routes_sorted[routes_sorted['style'] == "F"]
    hardest_flash = flash_routes.iloc[0]['grade'] if len(flash_routes) > 0 else None
    
    onsight_routes = routes_sorted[routes_sorted['style'] == "o.s."]
    hardest_onsight = onsight_routes.iloc[0]['grade'] if len(onsight_routes) > 0 else None
    
    with col1:
        st.metric("Hardest Grade", hardest_grade)
    
    if hardest_onsight:
        with col2:
            st.metric("Hardest Onsight", hardest_onsight)
    
    if hardest_flash:
        with col3:
            st.metric("Hardest Flash", hardest_flash)


def render_visualizations(routes):
    """Render grade pyramid or multipitch visualization."""
    with st.spinner("Generating visualization..."):
        fig = _create_visualization(routes)
        if fig:
            st.pyplot(fig, dpi=250)
            plt.close(fig)
    st.markdown("---")


def _create_visualization(routes):
    """Create appropriate visualization based on current view."""
    view = st.session_state.view
    sandbaggers = st.session_state.get('sandbaggers_choice', 'Round down')
    
    if view == 'Multipitch':
        return plot_multipitches(routes)
    elif view == 'Sportclimb':
        return plot_grade_pyramid(
            routes, 
            grades=GRADE_OPTIONS_ROUTES[1:],
            sandbaggers_choice=sandbaggers,
            title="My Sport Climbing Grade Pyramid"
        )
    elif view == 'Boulder':
        return plot_grade_pyramid(
            routes,
            grades=GRADE_OPTIONS_BOULDERS[1:],
            sandbaggers_choice=sandbaggers,
            title="My Boulder Grade Pyramid"
        )
    return None
