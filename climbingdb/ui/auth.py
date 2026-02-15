"""
Authentication UI components.
"""

import streamlit as st
from climbingdb.services.auth_service import AuthService


def render_login_page():
    """Render login and signup page."""

    st.title("Welcome to Sandbagger's Choice")
    st.markdown("---")

    st.info("📺 New here? Check out the [demo with sample data](https://olesclimbingdb.streamlit.app) first!")

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
                # Set session state
                st.session_state.authenticated = True
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.rerun()
            else:
                st.error("Invalid username or password")


def render_signup_form():
    """Render signup form."""
    st.subheader("Create New Account")

    with st.form("signup_form"):
        new_username = st.text_input("Username", help="At least 3 characters")
        new_email = st.text_input("Email (optional)")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        submitted = st.form_submit_button("Sign Up", type="primary", width='stretch')

        if submitted:
            # Validation
            if not new_username or not new_password:
                st.error("Please fill in user name and password")
                return

            if new_password != confirm_password:
                st.error("Passwords don't match")
                return

            # Create account
            auth = AuthService()
            success, message, user = auth.create_user(new_username, new_password, new_email)

            if success:
                st.success(message)
                st.info("Please login with your new account")
            else:
                st.error(message)


def render_user_menu():
    """Render user menu in sidebar."""

    if not st.session_state.get('authenticated', False):
        return

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 👤 {st.session_state.username}")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("⚙️ Settings", width='stretch'):
            st.session_state.show_settings = True

    with col2:
        if st.button("🚪 Logout", width='stretch'):
            logout()


def render_settings_page():
    """Render user settings page."""
    st.title("⚙️ Account Settings")
    st.markdown("---")

    # Account info
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

    # Change password
    st.subheader("Change Password")

    with st.form("change_password_form"):
        old_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")

        submitted = st.form_submit_button("Change Password", type="primary")

        if submitted:
            if not old_password or not new_password or not confirm_new_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_new_password:
                st.error("New passwords don't match")
            else:
                success, message = auth.change_password(
                    st.session_state.user_id,
                    old_password,
                    new_password
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)

    st.markdown("---")

    # Back button
    if st.button("← Back to Routes"):
        st.session_state.show_settings = False
        st.rerun()


def logout():
    """Log out the current user."""
    # Clear cache to prevent stale data
    st.cache_resource.clear()

    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def require_authentication():
    """
    Check if user is authenticated. If not, show login page.

    Returns:
        bool: True if authenticated, False otherwise
    """
    if not st.session_state.get('authenticated', False):
        render_login_page()
        st.stop()
        return False

    return True