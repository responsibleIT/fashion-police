"""
start_page.py
---------------

This module contains the UI for the initial landing page of the
Fashion Police app.  Users are greeted with a short description of
what the app does and can proceed to the next page by clicking a
button.  The ``render`` function returns the identifier of the next
page when navigation should occur.
"""

from __future__ import annotations

import streamlit as st


def render() -> str | None:
    """
    Render the start page and return the identifier of the next page
    when the user opts to continue.

    Returns
    -------
    str or None
        The identifier of the next page (``"make_picture_page"``) if
        navigation should occur; otherwise ``None``.
    """
    # Page header and description.
    st.title("👮‍♀️ Fashion Police")
    st.markdown(
        """
        Welcome to **Fashion Police**, your personal stylist powered by
        machine learning!  Snap a picture of your outfit and let our
        models do the rest.  We'll segment your clothing, mask out your
        face for fairness, classify your garments and even predict a
        high‑level fashion style (e.g. casual, formal or streetwear).

        To get started simply click the button below and grant
        permission for your webcam.  No photos are stored – all
        processing happens locally on your machine.
        """
    )
    # Primary action button.  When clicked we return the next page id.
    if st.button("📸 Take a picture", type="primary"):
        return "make_picture_page"
    # No navigation otherwise.
    return None