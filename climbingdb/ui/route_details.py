import streamlit as st
import urllib.parse
import matplotlib.pyplot as plt

from climbingdb.models import Route, Ascent
from climbingdb.config import APP_BASE_URL
from climbingdb.ui.navigation import DISCIPLINE_ICONS
from climbingdb.visualizations import plot_multipitches
from climbingdb.services import ClimbingService


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
    _render_share_button(route)
    _render_route_properties(route)

    st.markdown("---")
    if ascent:
        st.markdown("#### :material/person: Your Ascent")
        _render_ascent_properties(ascent)


def _render_navigation_header():
    if st.button(":material/first_page: Back"):
        st.query_params.clear()
        st.session_state.view = st.session_state.get('previous_view', 'Sportclimb')
        st.rerun()

def _render_grade_stars(obj):
    st.markdown(f"**Consensus Grade:** {obj.consensus_grade or 'N/A'}")
    if obj.consensus_stars:
        st.markdown(f"**Average stars:** {obj.consensus_stars}")


def _render_location(route):
    st.write(f"**Country:** {route.country.name if route.country else 'N/A'}")
    st.write(f"**Area:** {route.area.name if route.area else 'N/A'}")
    st.write(f"**Crag:** {route.crag.name if route.crag else 'N/A'}")

    if route.latitude and route.longitude:
        st.write(f"**GPS:** {route.latitude:.6f}, {route.longitude:.6f}")
        st.link_button(
            ":material/map: View on Google Maps",
            f"https://www.google.com/maps?q={route.latitude},{route.longitude}"
        )


def _render_route_details(obj):
    if hasattr(obj, 'bolts') and obj.bolts:
        st.write(f"**Bolts:** {obj.bolts}")
    if hasattr(obj, 'length') and obj.length:
        st.write(f"**Length:** {obj.length:.0f}m")
    if hasattr(obj, 'first_ascensionist') and obj.first_ascensionist:
        st.write(f"**First Ascent:** {obj.first_ascensionist}")
    if hasattr(obj, 'first_ascent') and obj.first_ascent:
        st.write(f"**FA Date:** {obj.first_ascent.strftime('%Y')}")
    if hasattr(obj, 'pitches') and obj.pitches:
        st.write(f"**Pitches:** {len(obj.pitches)}")
    if hasattr(obj, 'ernsthaftigkeit') and obj.ernsthaftigkeit:
        st.write(f"**Ernsthaftigkeit:** {obj.ernsthaftigkeit}")
    if hasattr(obj, 'description') and obj.description:
        st.markdown("---")
        st.markdown("#### :material/article: Description")
        st.write(obj.description)


def _render_route_properties(route):
    """Render universal route properties."""
    discipline_icon = DISCIPLINE_ICONS.get(route.discipline, DISCIPLINE_ICONS['Sportclimb'])

    st.title(f"{discipline_icon} {route.name}")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown("#### :material/target: Rating")
        _render_grade_stars(route)
    with col2:
        st.markdown("#### :material/location_on: Location")
        _render_location(route)
    with col3:
        st.markdown("#### :material/info: Details")
        _render_route_details(route)


def _render_ascent_properties(ascent):
    """Render ascent properties - works for Ascent and PitchAscent."""
    if hasattr(ascent, 'is_project') and ascent.is_project:
        st.info(":material/strategy: Project")
    if hasattr(ascent, 'is_milestone') and ascent.is_milestone:
        st.success(":material/trophy: Milestone")

    grade_str = f"**Personal Grade:** {ascent.grade}"
    if hasattr(ascent, 'led') and ascent.led is not None:
        led_str = "Led" if ascent.led else "Followed"
        grade_str += f" ({led_str})"
    st.markdown(grade_str)

    if ascent.style:
        st.markdown(f"**Style:** {ascent.style}")

    if ascent.stars:
        st.markdown(f"**Stars:** {':material/star:' * int(ascent.stars)}")

    if hasattr(ascent, 'date') and ascent.date:
        st.markdown(f"**Date:** {str(ascent.date)}")

    if hasattr(ascent, 'ascent_time') and ascent.ascent_time:
        st.write(f"**Ascent Time:** {round(ascent.ascent_time)} h")

    if ascent.shortnote:
        st.write(f"**Short Note:** {ascent.shortnote}")
    if ascent.gear:
        st.markdown(f"**Gear:** {ascent.gear}")

    if ascent.notes:
        _render_notes(ascent.notes)

    # Pitch details only for full Ascent
    if hasattr(ascent, 'pitch_ascents') and ascent.pitch_ascents:
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            _render_pitch_details(ascent)
        with col2:
            with st.spinner("Generating visualization..."):
                df = ClimbingService._ascents_to_dataframe([ascent])
                fig = plot_multipitches(df, title=df["name"].item(), xwidth=6, ywidth=6)
                if fig:
                    st.pyplot(fig, dpi=250)
                    plt.close(fig)




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

    for pa in ascent.pitch_ascents:
        pitch = pa.pitch

        pitch_number = pitch.pitch_number
        name = pitch.pitch_name or f"Pitch {pitch_number}"
        expander_title = f"P{pitch_number}: {name}"

        with st.expander(expander_title, expanded=False):
            _render_grade_stars(pitch)
            _render_route_details(pitch)
            _render_ascent_properties(pa)


def _render_share_button(route):
    share_url = f"{APP_BASE_URL}/?route_id={route.id}"
    share_text = f"Check out {route.name} ({route.consensus_grade or '?'}) on Sandbagger's Choice!"
    full_encoded = urllib.parse.quote(f"{share_text} {share_url}")

    _, col = st.columns([7,1])
    with col:
        st.link_button(
            "Share on WhatsApp",
            f"https://wa.me/?text={full_encoded}",
            use_container_width=True
        )