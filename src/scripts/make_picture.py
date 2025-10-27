"""
make_picture.py
----------------

This script provides helper functions for acquiring images from the
user when running inside Streamlit.  Streamlit's built‑in
``st.camera_input`` widget returns an ``UploadedFile`` object.  To
perform inference we need to convert this object into a ``PIL.Image``.

Separating this logic into its own module keeps the Streamlit page
code clean and makes it easy to add additional preprocessing steps in
future (for example, rotating the image based on EXIF orientation or
validating the aspect ratio).
"""

from __future__ import annotations

from typing import Optional
import io
from PIL import Image


def uploaded_file_to_image(uploaded_file) -> Optional[Image.Image]:
    """
    Convert a Streamlit UploadedFile object into a PIL Image.

    The ``st.camera_input`` widget returns an UploadedFile with a
    ``getvalue()`` method that provides the image bytes.  This helper
    wraps the conversion in a try/except to gracefully handle invalid
    files.

    Parameters
    ----------
    uploaded_file : UploadedFile or None
        The object returned by ``st.camera_input``.  If ``None`` then
        ``None`` is returned.

    Returns
    -------
    PIL.Image or None
        The decoded image, or ``None`` if decoding fails.
    """
    if uploaded_file is None:
        return None
    try:
        bytes_data = uploaded_file.getvalue()
        if not bytes_data:
            return None
        return Image.open(io.BytesIO(bytes_data)).convert("RGB")
    except Exception:
        # In case of an unsupported file format or other errors return None.
        return None