"""
Route detail page.
"""

import streamlit as st

from climbingdb.models import Route, Ascent
from climbingdb.config import APP_BASE_URL
from climbingdb.ui.navigation import DISCIPLINE_ICONS
import urllib.parse


def render_route_details_page(public_db, route_id, user_id=None):
    """Render route detail page."""
    route = public_db.session.query(Route).filter(Route.id == route_id).first()

    if not route:
        st.error("Route not found!")
        if st.button(":material/first_page: Back"):
            st.query_params.clear()
            st.rerun()
        return

    # Look up user's ascent if logged in
    ascent = None
    if user_id:
        ascent = public_db.session.query(Ascent).filter(
            Ascent.route_id == route.id,
            Ascent.user_id == user_id
        ).first()

    _render_navigation_header()
    _render_route_properties(route)

    st.markdown("---")
    if ascent:
        _render_ascent_properties(ascent, route.discipline)


def _render_navigation_header():
    """Render back button and share URL."""
    if st.button(":material/first_page: Back"):
        st.query_params.clear()
        st.session_state.view = st.session_state.get('previous_view', 'Sportclimb')
        st.rerun()


def _render_grade_stars(route):
    st.markdown("#### :material/target: Rating")
    st.markdown(f"**Consensus Grade:** {route.consensus_grade or 'N/A'}")
    stars = ":material/star: " * int(route.consensus_stars) if route.consensus_stars else "No ratings yet"
    st.markdown(f"**Rating:** {stars}")

def _render_location(route):
    st.markdown("#### :material/location_on: Location")
    st.write(f"**Country:** {route.country.name if route.country else 'N/A'}")
    st.write(f"**Area:** {route.area.name if route.area else 'N/A'}")
    st.write(f"**Crag:** {route.crag.name if route.crag else 'N/A'}")

    if route.latitude and route.longitude:
        st.write(f"**GPS:** {route.latitude:.6f}, {route.longitude:.6f}")
        st.link_button(
            ":material/map: View on Google Maps",
            f"https://www.google.com/maps?q={route.latitude},{route.longitude}"
        )


def _render_route_details(route):
    st.markdown("#### :material/info: Route Details")

    if route.discipline in ("Sportclimb", "Multipitch") and route.bolts:
        st.write(f"**Bolts:** {route.bolts}")
    if route.length:
        st.write(f"**Length:** {route.length:.0f}m")
    if route.first_ascensionist:
        st.write(f"**First Ascent:** {route.first_ascensionist}")
    if route.first_ascent:
        st.write(f"**FA Date:** {route.first_ascent.strftime('%Y')}")
    if route.discipline == "Multipitch" and route.pitches:
        st.write(f"**Pitches:** {len(route.pitches)}")
    if route.ernsthaftigkeit:
        st.write(f"**Ernsthaftigkeit:** {route.ernsthaftigkeit}")
    if route.description:
        st.markdown("---")
        st.markdown("#### :material/article: Description")
        st.write(route.description)


def _render_route_properties(route):
    """Render universal route properties."""
    discipline_icon = DISCIPLINE_ICONS.get(route.discipline, DISCIPLINE_ICONS['Sportclimb'])

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"{discipline_icon} {route.name}")
    with col2:
        _render_share_button(route)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        _render_grade_stars(route)
    with col2:
        _render_location(route)
    with col3:
        _render_route_details(route)


def _render_ascent_properties(ascent, discipline):
    """Render user's ascent properties."""
    st.markdown("#### :material/person: Your Ascent")

    if ascent.is_project:
        st.info(":material/strategy: Project")
    if ascent.is_milestone:
        st.success(":material/trophy: Milestone")

    st.markdown(f"**Personal Grade:** {ascent.grade}")
    if ascent.style:
        st.markdown(f"**Style:** {ascent.style}")
    st.markdown(f"**Stars:** {':material/star:' * int(ascent.stars) if ascent.stars else '0'}")
    st.markdown(f"**Date:** {str(ascent.date) or 'N/A'}")

    if discipline == "Multipitch" and ascent.ascent_time:
        st.write(f"**Ascent Time:** {round(ascent.ascent_time)} h")

    if ascent.shortnote:
        st.write(f"**Short Note:** {ascent.shortnote}")

    if ascent.gear:
        st.markdown(f"**Gear:** {ascent.gear}")

    if ascent.notes:
        _render_notes(ascent.notes)

    if discipline == "Multipitch" and ascent.pitch_ascents:
        st.markdown("---")
        _render_pitch_details(ascent)


def _render_notes(notes, label="Notes", max_preview_length=100):
    """Render notes with expandable view if too long."""
    if not notes:
        return

    st.markdown(f"**:material/notes: {label}**")

    if len(notes) <= max_preview_length:
        # Short note: display directly
        st.write(notes)
    else:
        # Long note: show preview + expander
        preview = notes[:max_preview_length].rsplit(' ', 1)[0] + "..."
        with st.expander(preview):
            st.write(notes)


def _render_pitch_details(ascent):
    """Render pitch-by-pitch breakdown for multipitch routes."""
    if not ascent.pitch_ascents:
        st.info("No pitch details logged.")
        return

    st.markdown(f"#### {DISCIPLINE_ICONS['Pitches']} Detailed Pitch Information")

    sorted_pitch_ascents = sorted(ascent.pitch_ascents, key=lambda pa: pa.pitch.pitch_number)

    for pa in sorted_pitch_ascents:
        pitch = pa.pitch

        # Expander title
        pitch_number = pitch.pitch_number
        pitch_name = pitch.pitch_name or f"Pitch {pitch_number}"
        ernst = f" ({pitch.pitch_ernsthaftigkeit})" if pitch.pitch_ernsthaftigkeit else ""

        expander_title = f"P{pitch_number}: {pitch_name}"

        with st.expander(expander_title, expanded=False):
            consensus = f" (consensus: {pitch.pitch_consensus_grade})" if pitch.pitch_consensus_grade else ""
            grade_str = f"**Grade:** {pa.grade or 'N/A'}{consensus}"
            if pitch.pitch_ernsthaftigkeit:
                grade_str += ernst
            st.write(grade_str)

            led_str = "Led" if pa.led else "Followed"
            shortnote = f", {pa.shortnote}" if pa.shortnote else ""
            st.write(f"**Style:** {led_str}{shortnote}")

            if pa.stars:
                stars_str = ":material/star:" * int(pa.stars)
                st.markdown(f"**Stars:** {stars_str}")

            if pitch.pitch_length:
                st.write(f"**Length:** {pitch.pitch_length:.0f}m")

            if pa.gear:
                st.write(f"**Gear:** {pa.gear}")

            # Notes (expandable if long)
            if pa.notes:
                _render_notes(pa.notes, label="Notes")


def _render_share_button(route):
    share_url = f"{APP_BASE_URL}/?route_id={route.id}"
    share_text = f"Check out {route.name} ({route.consensus_grade or '?'}) on Sandbagger's Choice!"
    full_encoded = urllib.parse.quote(f"{share_text} {share_url}")
    st.link_button(
            "Share on WhatsApp",
            f"https://wa.me/?text={full_encoded}",
            use_container_width=True
    )