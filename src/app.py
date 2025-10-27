"""
app.py
------

Entry point for the Fashion Police Streamlit application.  This module
implements a simple state machine to navigate between pages without
requiring users to switch pages manually via the sidebar.  Each page is
implemented in its own module under ``pages/``.  Navigation is
controlled via ``st.session_state['page']`` which is updated when the
user clicks buttons on the different pages.

To run the app locally execute:

    streamlit run fashion_police/src/app.py

The first time the app runs it may need to download pre‑trained
models from Hugging Face.  Subsequent runs reuse the cached copies
stored under ``~/.cache/huggingface``.
"""

from __future__ import annotations

import streamlit as st

from pages import start_page, make_picture_page, loader_page, result_page


def main() -> None:
    # Set the basic page configuration.  We hide the default Streamlit
    # navigation sidebar since our app manages navigation internally.
    st.set_page_config(
        page_title="Fashion Police",
        page_icon="👗",
        # Use a wide layout so that the capture and segmentation
        # previews can sit side‑by‑side without excessive scrolling.
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    # Initialise the current page in the session state on first run.
    if "page" not in st.session_state:
        st.session_state.page = "start_page"

    # Create a dictionary mapping page identifiers to callables.  Each
    # page module exposes a ``render`` function that accepts no
    # arguments and returns the name of the next page when the user
    # chooses to proceed.  If the user stays on the current page the
    # function returns ``None``.
    pages = {
        "start_page": start_page.render,
        "make_picture_page": make_picture_page.render,
        "loader_page": loader_page.render,
        "result_page": result_page.render,
    }

    # Determine which page function to call based on session state.
    current_page = st.session_state.get("page", "start_page")
    page_func = pages.get(current_page, start_page.render)
    # Call the page; if it returns a new page identifier update the
    # session state and rerun.  We wrap in a try/except to guard
    # against unexpected errors that would otherwise leave the app in
    # an inconsistent state.
    try:
        next_page = page_func()
        if next_page and next_page in pages and next_page != current_page:
            st.session_state.page = next_page
            st.rerun()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()