import streamlit as st
import pandas as pd

from climbingdb.scripts.import_8anu import import_8a_csv, parse_8anu_dataframe
from climbingdb.config import EIGHTANU_EXPORT_URL


def render_8a_sync_form(show_toggle=True):
    if show_toggle:
        sync = st.radio(
            "Do you want to synchronize your 8a.nu data?",
            ["No", "Yes"],
            horizontal=True,
            key="sync_8a_toggle"
        )
        if sync == "No":
            return None

    uploaded_file = get_8anu_csv_file()
    return uploaded_file


def get_8anu_csv_file():
    """Render the step-by-step sync instructions."""
    st.markdown("#### :material/sync: Sync with 8a.nu")
    st.info(":material/info: Your 8a.nu credentials are never shared with Sandbagger's Choice.")

    st.markdown("##### Step 1: Log into your 8a.nu account")
    st.link_button(":material/open_in_new: Open https://www.8a.nu/login", "https://www.8a.nu/login")
    st.info(""":material/info: This is needed to authenticate yourself and enable the download of your data.
    """)

    st.markdown("##### Step 2: Download your 8a.nu data")
    st.markdown("Either go to your 8a.nu settings and download the data from there or click the link below.")
    st.link_button(f":material/open_in_new: Open {EIGHTANU_EXPORT_URL}", EIGHTANU_EXPORT_URL)
    st.info(f""" :material/info: Make sure you're logged into 8a.nu before clicking. You will be asked to save a CSV file to your computer.
    This file contains your route and bouldering data. You can open it in Excel if you'd like to inspect it.
    """)

    st.markdown("##### Step 3: Upload your 8a.nu data")
    uploaded_file = st.file_uploader(
        "Upload 8a.nu CSV file",
        type=['csv'],
        key="upload_8a_csv",
        help="The CSV file downloaded from 8a.nu"
    )

    return uploaded_file


def show_preview_of_8anu_import(uploaded_file):
    """
    Show preview of how 8a.nu data will be imported.
    Returns True if user confirms, False otherwise.
    """
    df = pd.read_csv(uploaded_file, sep=',', header=0, keep_default_na=False, dtype=str)
    uploaded_file.seek(0)

    # Parse using shared function
    parsed_rows, skipped_rows, errors = parse_8anu_dataframe(df)

    # Summary metrics
    n_routes = sum(1 for r in parsed_rows if r['discipline'] == 'Sportclimb')
    n_boulders = sum(1 for r in parsed_rows if r['discipline'] == 'Boulder')
    n_countries = len(set(r['country_name'] for r in parsed_rows if r['country_name']))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Ascents", len(parsed_rows))
    with col2:
        st.metric("Routes", n_routes)
    with col3:
        st.metric("Boulders", n_boulders)
    with col4:
        st.metric("Countries", n_countries)

    preview_df = pd.DataFrame([{
        'Name': r['name'],
        'Discipline': r['discipline'],
        'Grade': r['grade'],
        'Style': r['style'] or '',
        'Crag': r['crag_name'],
        'Area': r['area_name'],
        'Country': r['country_name'] or '',
        'Date': r['date'] or '',
        'Stars': r['stars'],
        'Short Note': r['shortnote'] or '',
        'Notes': r['notes'] or ''
    } for r in parsed_rows])

    st.markdown(f"### Preview ({len(preview_df)} ascents will be imported)")
    st.dataframe(
        preview_df,
        width="stretch",
        height=400,
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Discipline": st.column_config.TextColumn("Discipline", width="small"),
            "Grade": st.column_config.TextColumn("Grade", width="small"),
            "Style": st.column_config.TextColumn("Style", width="small"),
            "Crag": st.column_config.TextColumn("Crag", width="medium"),
            "Area": st.column_config.TextColumn("Area", width="medium"),
            "Country": st.column_config.TextColumn("Country", width="small"),
            "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "Stars": st.column_config.NumberColumn("Stars", width="small"),
            "Short Note": st.column_config.TextColumn("Short Note", width="small"),
            "Notes": st.column_config.TextColumn("Notes")
        }
    )

    # Show skipped rows
    if skipped_rows:
        with st.expander(f":material/warning: {len(skipped_rows)} ascents will be skipped"):
            st.dataframe(
                pd.DataFrame(skipped_rows),
                width="stretch",
                hide_index=True
            )


def submit_8anu_upload(uploaded_file, user_id):
    try:
        success, message = _run_import(uploaded_file, user_id)
        if success:
            st.success(message)
        else:
            st.warning(f"Import failed: {message}")

    except Exception as e:
        st.error(f":material/error: Could not read file: {e}")
        st.info("Make sure you uploaded the correct CSV file from 8a.nu")


def _run_import(uploaded_file, user_id, dry_run=False):
    spinner_message = "Importing..." if not dry_run else "Previewing..."
    with st.spinner(spinner_message):
        imported, skipped, errors = import_8a_csv(csv_file=uploaded_file, user_id=user_id, dry_run=dry_run)

        if dry_run:
            message = f":material/check: Preview: {imported} ascents would be imported"
        else:
            message = f":material/check: Successfully imported {imported} ascents!"
            #st.cache_resource.clear()

        if skipped > 0:
            st.warning(f":material/warning: {skipped} ascents skipped")

        if errors:
            with st.expander(f":material/error: {len(errors)} errors"):
                for error in errors:
                    st.write(f"- {error}")

        return True, message
