"""
Navigation components.
"""

import streamlit as st


def render_navigation_buttons():
    """Render discipline navigation buttons."""
    disciplines = [
        ("🧗 Sportclimbing", "Sportclimb"),
        ("🪨 Bouldering", "Boulder"),
        ("⛰️ Multipitches", "Multipitch"),
        ("🎯 Projects", "Projects")
    ]

    cols = st.columns([2, 2, 2, 2, 2])

    for col, (label, discipline) in zip(cols, disciplines):
        button_type = "primary" if st.session_state.view == discipline else "secondary"
        if col.button(label, type=button_type):
            if st.session_state.view != discipline:
                st.session_state.selected_area = "All"
            st.session_state.view = discipline
            st.rerun()
