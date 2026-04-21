"""
Authentication UI components.
"""

import streamlit as st
from climbingdb.services.auth_service import AuthService
from climbingdb.ui.sync_8anu import (
    render_8a_sync_form,
    get_8anu_csv_file,
    submit_8anu_upload,
    show_preview_of_8anu_import
)
from climbingdb.ui.settings import (
    render_delete_account,
    render_password_settings,
    render_delete_all_ascents
)
from climbingdb.ui.achievements import render_achievements


def render_login_page():
    """Render login and signup page."""

    st.title("Welcome to Sandbagger's Choice")
    st.markdown("---")

    st.info(":material/co_present: New here? Check out the [demo with sample data](https://olesclimbingdb.streamlit.app) first!")

    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        render_login_form()

    with tab2:
        render_signup_form()


def render_login_form():
    """Render login form."""
    st.subheader("Login to Your Account")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login", type="primary", width='stretch')

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password")
                return

            auth = AuthService()
            user = auth.authenticate_user(username, password)

            if user:
                #st.cache_resource.clear()
                st.session_state.authenticated = True
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.rerun()
            else:
                st.error("Invalid username or password")


def render_signup_form():
    st.subheader("Create New Account")
    uploaded_file = render_8a_sync_form(show_toggle=True)

    if uploaded_file:
        show_preview_of_8anu_import(uploaded_file)

    with st.form("signup_form"):
        st.markdown("#### Your Sandbagger's Choice credentials")
        new_username = st.text_input("Username")
        new_email = st.text_input("Email (optional)")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Sign Up", type="primary", width='stretch')

    if submitted:
        if not new_username or not new_password:
            st.error("Please fill in username and password")
            return

        if new_password != confirm_password:
            st.error("Passwords don't match")
            return

        auth = AuthService()
        success, errors, user = auth.create_user(new_username, new_password, new_email)

        if not success:
            for error in errors:
                st.error(error)
            return

        st.success("Account created!")

        if uploaded_file:
            submit_8anu_upload(uploaded_file, user.id)

        st.info("Please login with your new account.")


def render_user_menu():
    """Render user menu in sidebar."""

    if not st.session_state.get('authenticated', False):
        return

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### :material/account_circle: {st.session_state.username}'s Profile")

    render_achievements()

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button(":material/settings: Settings", width='stretch'):
            st.session_state.show_settings = True
            st.rerun()

    with col2:
        if st.button(":material/logout: Logout", width='stretch'):
            logout()


def render_settings_page():
    st.title(":material/settings: Account Settings")
    st.markdown("---")

    st.subheader("Account Information")
    auth = AuthService()
    user = auth.get_user_by_id(st.session_state.user_id)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Username:** {user.username}")
        st.write(f"**Email:** {user.email}")
    with col2:
        st.write(f"**Member since:** {user.created_at.strftime('%B %d, %Y')}")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        ":material/sync: 8a.nu Sync",
        ":material/lock: Password",
        ":material/delete_sweep: Delete Ascents",
        ":material/person_remove: Delete Account"
    ])

    with tab1:
        uploaded_file = get_8anu_csv_file()
        if uploaded_file:
            show_preview_of_8anu_import(uploaded_file)

            # Confirm button
            st.markdown("---")
            confirmed = st.button(":material/check: Confirm Import",
                type="primary", width="stretch", key="confirm_8a_import")

            if confirmed:
                submit_8anu_upload(uploaded_file, st.session_state.user_id)
    with tab2:
        render_password_settings(auth)
    with tab3:
        render_delete_all_ascents(auth)
    with tab4:
        render_delete_account(auth)
    st.markdown("---")

    if st.button(":material/first_page: Back to Routes"):
        st.session_state.show_settings = False
        st.rerun()


def logout():
    #st.cache_resource.clear()

    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def require_authentication():
    if not st.session_state.get('authenticated', False):
        render_login_page()
        st.stop()
        return False

    return True