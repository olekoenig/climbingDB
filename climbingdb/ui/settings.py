import streamlit as st


def render_password_settings(auth):
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
                success, errors = auth.change_password(st.session_state.user_id, old_password, new_password)

                if not success:
                    for error in errors:
                        st.error(error)
                    return

                st.success("Password changed!")


def render_delete_all_ascents(auth):
    """Render delete all ascents confirmation."""
    st.subheader(":material/delete_sweep: Delete All Ascents")
    st.warning(""":material/warning: This will permanently delete **all your ascents**. 
    This action **cannot be undone**.""")

    confirm = st.text_input(
        "Type **DELETE ALL** to confirm:",
        key="delete_all_ascents_confirm"
    )

    if st.button(
            ":material/delete_sweep: Delete All My Ascents",
            type="primary",
            disabled=(confirm != "DELETE ALL"),
            key="delete_all_ascents_btn"
    ):
        try:
            deleted_count = auth.delete_all_ascents(st.session_state.user_id)
            st.success(f":material/check: Deleted {deleted_count} ascents.")
            #st.cache_resource.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")


def render_delete_account(auth):
    """Render delete account confirmation."""
    st.subheader(":material/person_remove: Delete Account")
    st.error(""":material/warning: This will permanently delete **your entire account**. 
    This action **cannot be undone**.""")

    user = auth.get_user_by_id(st.session_state.user_id)

    confirm_username = st.text_input(
        f"Type your username **{user.username}** to confirm:",
        key="delete_account_username_confirm"
    )

    password = st.text_input(
        "Enter your password to confirm:",
        type="password",
        key="delete_account_password_confirm"
    )

    if st.button(
            ":material/person_remove: Permanently Delete My Account",
            type="primary",
            disabled=(confirm_username != user.username or not password),
            key="delete_account_btn"
    ):
        # Verify password before deletion
        verified_user = auth.authenticate_user(user.username, password)
        if not verified_user:
            st.error("Incorrect password")
            return

        try:
            auth.delete_account(st.session_state.user_id)
            st.success(":material/check: Account deleted.")
            # st.cache_resource.clear()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")