"""
Navigation components.
"""

import streamlit as st

DISCIPLINE_ICONS = {
    "Sportclimb": ":material/mountain_flag:",
    "Boulder": ":material/landslide:",
    "Multipitch": ":material/altitude:",
    "Projects": ":material/strategy:",
    "Pitches": ":material/altitude:"
}

def render_navigation_buttons():
    """Render discipline navigation buttons."""
    disciplines = [
        (f"{DISCIPLINE_ICONS['Sportclimb']} Sportclimbing", "Sportclimb"),
        (f"{DISCIPLINE_ICONS['Boulder']} Bouldering", "Boulder"),
        (f"{DISCIPLINE_ICONS['Multipitch']} Multipitches", "Multipitch"),
        (f"{DISCIPLINE_ICONS['Projects']} Projects", "Projects")
    ]

    cols = st.columns([2, 2, 2, 2, 2])

    for col, (label, discipline) in zip(cols, disciplines):
        button_type = "primary" if st.session_state.view == discipline else "secondary"
        if col.button(label, type=button_type):
            if st.session_state.view != discipline:
                st.session_state.selected_area = "All"
            st.session_state.view = discipline
            st.rerun()
