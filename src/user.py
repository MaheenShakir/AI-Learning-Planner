import uuid

import streamlit as st


def get_user_id():
    """Give every visitor a private ID.

    The ID is kept in the session (so it follows the visitor across pages)
    and in the web address as ?u=... (so it survives a page refresh).
    """
    user_id = st.session_state.get("user_id")

    if not user_id:
        from_url = st.query_params.get("u", "")
        if from_url.isalnum() and 8 <= len(from_url) <= 64:
            user_id = from_url
        else:
            user_id = uuid.uuid4().hex
        st.session_state["user_id"] = user_id

    if st.query_params.get("u") != user_id:
        st.query_params["u"] = user_id

    return user_id
