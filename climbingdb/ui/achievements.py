"""
Achievement badges for climbing milestones.
"""

import streamlit as st

from climbingdb.services import ClimbingService
from climbingdb.grade import Grade
from climbingdb.ui.achievement_helpers import (
    get_max_daily_length,
    get_max_daily_v_points,
    get_max_boulders_in_area
)


def _create_badge_html(badge):
    """Create badge HTML using shields.io."""
    color = "red"
    url = (f"https://img.shields.io/badge/"
           f"{badge['label']}-{badge['message']}-{color}"
           f"?style=for-the-badge")

    return f"""
    <div title="{badge['description']}" style="margin: 2px 0;">
        <img src="{url}" alt="{badge['name']}">
    </div>
    """


BADGES = {
    "8a_redpoint": {
        "name": "8a Redpoint",
        "description": "Redpointed 8a",
        "label": "8a",
        "message": "Redpoint"
    },
    "8a_onsight": {
        "name": "8a Onsight",
        "description": "Onsighted 8a",
        "label": "8a",
        "message": "Onsight"
    },
    "8a_multipitch": {
        "name": "8a Multipitch",
        "description": "Climbed an 8a multipitch",
        "label": "8a",
        "message": "Multipitch"
    },
    "8A_boulder": {
        "name": "8A Boulder",
        "description": "Bouldered 8A",
        "label": "8A",
        "message": "Boulder"
    },
    "vertical_500": {
        "name": "500m Day",
        "description": "Climbed 500m+ in one day",
        "label": "500m",
        "message": "Day"
    },
    "boulder_parkour": {
        "name": "Boulder Parkour",
        "description": "Climbed 30 boulders in one area",
        "label": "30+ Boulders",
        "message": "Day"
    },
    "commentator": {
        "name": "Commentator",
        "description": "Added notes on 30%+ of all routes",
        "label": "Commentator",
        "message": "Verbose"
    },
    "century_club": {
        "name": "Century Club",
        "description": "Climbed 100+ routes graded 8a or harder",
        "label": "100x",
        "message": "8a"
    },
    "world_traveler": {
        "name": "World Traveler",
        "description": "Climbed in 10+ countries",
        "label": "World",
        "message": "Traveler"
    },
    "v_points_100": {
        "name": "V-Points 100",
        "description": "Climbed 100 V-points in one day",
        "label": "100 V Points",
        "message": "Day"
    },
}


@st.cache_data(ttl=3600)
def get_earned_badges_cached(_user_id):
    db = ClimbingService(user_id=_user_id)
    stats = db.get_statistics()

    ole_grade_8a = Grade("8a").conv_grade()
    ole_grade_8A = Grade("8A").conv_grade()

    max_daily_length = get_max_daily_length(db)
    max_boulders_in_area = get_max_boulders_in_area(db)
    max_daily_v_points = get_max_daily_v_points(db)

    checks = {
        "8a_redpoint": Grade(stats['hardest_redpoint_grade']).conv_grade() >= ole_grade_8a,
        "8a_onsight": Grade(stats['hardest_onsight_grade']).conv_grade() >= ole_grade_8a,
        "8a_multipitch": Grade(stats['hardest_multipitch_grade']).conv_grade() >= ole_grade_8a,
        "8A_boulder": Grade(stats['hardest_boulder_grade']).conv_grade() >= ole_grade_8A,
        "vertical_500": max_daily_length >= 500,
        "boulder_parkour": max_boulders_in_area >= 30,
        "commentator": stats['comment_ratio'] >= 0.3,
        "century_club": stats['routes_8a_plus_count'] >= 100,
        "world_traveler": stats['total_countries'] >= 10,
        "v_points_100": max_daily_v_points >= 100,
    }

    badges = []
    for badge_id, earned in checks.items():
        if earned and badge_id in BADGES:
            badges.append({'id': badge_id, **BADGES[badge_id]})

    return badges


def render_achievements():
    """Render earned achievement badges in sidebar."""
    if not st.session_state.get('authenticated'):
        return

    earned_badges = get_earned_badges_cached(st.session_state.user_id)
    if not earned_badges:
        return

    st.sidebar.markdown("**:material/award_star: Achievements**")

    # Render badges in a row
    badges_html = ""
    for badge in earned_badges:
        badges_html += _create_badge_html(badge)

    st.sidebar.markdown(badges_html, unsafe_allow_html=True)
    st.sidebar.markdown("---")
