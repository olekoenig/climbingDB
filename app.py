"""
streamlit run app.py
"""

import streamlit as st
import matplotlib.pyplot as plt

from climbingdb import ClimbingQuery, Grade
from climbingdb.display_multipitches import create_multipitch_visualization

GRADE_OPTIONS_ROUTES = ["All", "4a", "5a", "6a", "6b", "6c", "7a", "7a+", "7b", "7b+",
                        "7c", "7c+", "8a", "8a+", "8b", "8b+", "8c", "8c+", "9a"]
GRADE_OPTIONS_BOULDERS = ['All', 'V0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8',
                          'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15']

SPORT_GRADE_SYSTEMS = ["Original", "French", "UIAA", "YDS", "Elbsandstein"]
BOULDER_GRADE_SYSTEMS = ["Original", "Vermin", "Font"]

DISPLAY_COLUMNS = ['name', 'grade', 'style', 'area', 'crag', 'notes', 'date', 'stars']


@st.cache_resource
def load_database():
    """Load and cache the climbing database."""
    return ClimbingQuery()


def apply_custom_css():
    """Apply custom CSS styling for buttons."""
    st.markdown("""
        <style>
        div.stButton > button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            font-size: 16px;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)


def render_navigation_buttons():
    disciplines = [
        ("🧗 Sportclimbing", "Sportclimb"),
        ("🪨 Bouldering", "Boulder"),
        ("⛰️ Multipitches", "Multipitch"),
        ("🎯 Projects", "Projects")
    ]

    cols = st.columns([2, 2, 2, 2, 4])

    for col, (label, view_name) in zip(cols, disciplines):
        with col:
            button_type = "primary" if st.session_state.view == view_name else "secondary"
            st.button(
                label,
                type=button_type,
                on_click=lambda v=view_name: st.session_state.update({'view': v})
            )


def get_grade_system_options(view):
    if view in ['Sportclimb', 'Multipitch', 'Projects']:
        return SPORT_GRADE_SYSTEMS
    elif view == 'Boulder':
        return BOULDER_GRADE_SYSTEMS
    else:
        return None


def render_sidebar_filters(db):
    st.sidebar.header("Filters")

    all_areas = sorted(db.data['area'].unique().tolist())
    area_options = ["All"] + all_areas
    selected_area = st.sidebar.selectbox("Area", area_options)

    grade_operation = st.sidebar.selectbox(
        "Grade Operation",
        [">=", "=="],
        help="≥: Show routes at or above grade\n==: Show routes at exact grade (includes slash grades)"
    )

    grade_options = GRADE_OPTIONS_BOULDERS if st.session_state.view == "Boulder" else GRADE_OPTIONS_ROUTES

    selected_grade = st.sidebar.selectbox(
        "Grade",
        grade_options,
        help="Select grade to filter by"
    )

    grade_system_options = get_grade_system_options(st.session_state.view)
    selected_grade_system = st.sidebar.selectbox(
        "Display Grades As",
        grade_system_options,
        help="Convert grades to different grading systems"
    )

    selected_stars = st.sidebar.slider(
        "Minimum Stars",
        min_value=0.0,
        max_value=3.0,
        value=0.0,
        step=1.0
    )

    return {
        'area': None if selected_area == "All" else selected_area,
        'grade': None if selected_grade == "All" else selected_grade,
        'grade_operation': grade_operation,
        'grade_system': selected_grade_system,
        'stars': None if selected_stars == 0.0 else selected_stars,
        'selected_area': selected_area,
        'selected_grade': selected_grade,
        'selected_stars': selected_stars
    }


def fetch_routes(db, filters):
    if st.session_state.view == "Projects":
        return db.get_projects()
    else:
        return db.get_filtered_routes(
            discipline=st.session_state.view,
            area=filters['area'],
            grade=filters['grade'],
            stars=filters['stars'],
            operation=filters['grade_operation']
        )


def format_grade_display(row, discipline):
    result = row['grade'] if row['grade'] else ""

    # If grade is None/empty, return empty string
    if not result:
        return ""

    # Add ernsthaftigkeit for multipitches
    if discipline == 'Multipitch' and row.get('ernsthaftigkeit'):
        result += f" {row['ernsthaftigkeit']}"

    if row.get('shortnote'):
        result += f" ({row['shortnote']})"

    return result


def process_routes_display(routes, selected_grade_system):
    # Subtract/add small number such that soft routes are displayed below hard routes
    routes['ole_grade'] = routes.apply(
        lambda row: row['ole_grade'] - 1e-6 if 'soft' in str(row['shortnote']).lower()
        else row['ole_grade'] + 1e-6 if 'hard' in str(row['shortnote']).lower()
        else row['ole_grade'],
        axis=1
    )

    routes = routes.sort_values(by="ole_grade", ascending=False)

    if st.session_state.view == "Multipitch":
        DISPLAY_COLUMNS.insert(2, 'length')

    # Convert grades if a different system is selected
    if selected_grade_system != "Original":
        routes['grade'] = routes['ole_grade'].apply(
            lambda x: Grade.from_ole_grade(x, selected_grade_system)
        )

    return routes


def render_statistics(routes, selected_grade_system):
    col1, col2, col3, col4, col5 = st.columns(5)

    hardest_grade = routes.iloc[0]['grade']
    if selected_grade_system != "Original":
        hardest_grade = Grade.from_ole_grade(Grade(hardest_grade).conv_grade(), selected_grade_system)

    metrics = [
        ("Total Routes", len(routes)),
        ("Hardest Grade", hardest_grade),
        ("Crags", routes['crag'].nunique()),
        ("Areas", routes['area'].nunique()),
        ("Countries", routes['country'].nunique())
    ]

    for col, (label, value) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            st.metric(label, value)


def render_multipitch_visualization(routes):
    with st.spinner("Generating visualization..."):
        fig = create_multipitch_visualization(routes)
        st.pyplot(fig)
        plt.close(fig)
    st.markdown("---")


def render_routes_table(routes):
    # Merge grade, ernsthaftigkeit, and shortnote
    routes['grade'] = routes.apply(
        lambda row: format_grade_display(row, st.session_state.view), axis=1)

    if st.session_state.view == "Multipitch":
        routes['length'] = routes.apply(
            lambda row: f"{row['length']:.0f}m" if row['length'] else "", axis=1)

    st.dataframe(
        routes[DISPLAY_COLUMNS],
        use_container_width=True,
        height=600,
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn("Name"),
            "grade": st.column_config.TextColumn("Grade"),
            "length": st.column_config.TextColumn("Length"),
            "style": st.column_config.TextColumn("Style"),
            "area": st.column_config.TextColumn("Area"),
            "crag": st.column_config.TextColumn("Crag"),
            "notes": st.column_config.TextColumn("Notes"),
            "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "stars": st.column_config.NumberColumn("Stars")
        }
    )


def render_filter_summary(filters):
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Active Filters")

    if filters['selected_area'] != "All":
        st.sidebar.write(f"📍 Area: {filters['selected_area']}")

    if filters['selected_grade'] != "All":
        st.sidebar.write(f"📈 Grade: {filters['grade_operation']} {filters['selected_grade']}")

    if filters['grade_system'] != "Original":
        st.sidebar.write(f"🎚️ Grade System: {filters['grade_system']}")

    if filters['selected_stars'] > 0:
        st.sidebar.write(f"⭐ Stars: ≥ {filters['selected_stars']}")


def main():
    st.set_page_config(
        page_title="My Climbing Routes",
        page_icon="🧗",
        layout="wide"
    )

    if 'view' not in st.session_state:
        st.session_state.view = 'Sportclimb'

    db = load_database()

    st.title("🧗 My Climbing Logbook")
    st.markdown("---")

    apply_custom_css()
    render_navigation_buttons()

    filters = render_sidebar_filters(db)

    routes = fetch_routes(db, filters)

    if len(routes) > 0:
        routes = process_routes_display(routes, filters['grade_system'])

        render_statistics(routes, filters['grade_system'])
        st.markdown("---")

        if st.session_state.view == 'Multipitch':
            render_multipitch_visualization(routes)

        render_routes_table(routes)
    else:
        st.warning("No routes match your filters. Try adjusting the filter criteria.")

    render_filter_summary(filters)


if __name__ == '__main__':
    main()
