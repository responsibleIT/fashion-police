"""
load_model.py
----------------

This module defines classes responsible for loading and caching the
underlying machine learning models used by the Fashion Police app.

There are two primary models used in this project:

1. A **clothing segmentation model** based on the SegFormer architecture.
   It accepts an image and returns a segmentation map where each pixel is
   assigned a class label.  We use this map to isolate the regions
   containing clothing items.  Without segmentation the classifier might
   accidentally focus on background features (e.g. the colour of the wall) and
   produce poor predictions.

2. A **clothing classification model** fine‑tuned from a Vision Transformer.
   Given an image (ideally of the cropped clothing region) it returns a
   predicted clothing category.  We use the class names defined by the
   model's config to map prediction indices into human readable labels.

Both classes defined below lazily load their underlying models the first
time they're used.  Subsequent calls reuse the cached instances stored
in class variables.  This pattern avoids repeatedly downloading models
from Hugging Face and improves latency during runtime.

Usage example:

    from PIL import Image
    from fashion_police.src.scripts.load_model import SegmentationModel, ClassificationModel

    seg_model = SegmentationModel()
    seg_map, overlay = seg_model.segment(Image.open("person.jpg"))

    cls_model = ClassificationModel()
    label, score = cls_model.classify(Image.open("shirt_crop.jpg"))
"""

from __future__ import annotations

import functools
from typing import Tuple, List

import numpy as np
from PIL import Image

from transformers import (
    SegformerImageProcessor,
    AutoModelForSemanticSegmentation,
    AutoImageProcessor,
    AutoModelForImageClassification,
)
import torch


class SegmentationModel:
    """Wrapper around a Hugging Face segmentation model for clothing."""

    # Class‑wide caches so that loading happens only once per session.
    _processor: SegformerImageProcessor | None = None
    _model: AutoModelForSemanticSegmentation | None = None

    # The mapping from class IDs to human readable labels defined by the
    # underlying segmentation model.  These come from the ATR dataset used
    # during fine‑tuning.  Not all labels correspond to garments; we'll
    # extract only the garment indices when cropping.
    id2label: dict[int, str] = {
        0: "Background",
        1: "Hat",
        2: "Hair",
        3: "Sunglasses",
        4: "Upper-clothes",
        5: "Skirt",
        6: "Pants",
        7: "Dress",
        8: "Belt",
        9: "Left-shoe",
        10: "Right-shoe",
        11: "Face",
        12: "Left-leg",
        13: "Right-leg",
        14: "Left-arm",
        15: "Right-arm",
        16: "Bag",
        17: "Scarf",
    }

    # A simple colour palette for visualising each class.  Colours are
    # arbitrary but distinct; the index in the list corresponds to the
    # class ID.  When adding new classes ensure there are at least as many
    # colours as there are labels.
    palette: List[Tuple[int, int, int]] = [
        (0, 0, 0),        # Background – black
        (128, 0, 0),      # Hat – maroon
        (255, 0, 0),      # Hair – red
        (255, 165, 0),    # Sunglasses – orange
        (255, 192, 203),  # Upper‑clothes – pink
        (255, 105, 180),  # Skirt – hot pink
        (255, 0, 255),    # Pants – magenta
        (219, 112, 147),  # Dress – pale violet red
        (255, 255, 0),    # Belt – yellow
        (0, 128, 0),      # Left shoe – green
        (34, 139, 34),    # Right shoe – forest green
        (255, 228, 196),  # Face – bisque
        (75, 0, 130),     # Left leg – indigo
        (138, 43, 226),   # Right leg – blue violet
        (0, 191, 255),    # Left arm – deep sky blue
        (135, 206, 235),  # Right arm – sky blue
        (0, 255, 255),    # Bag – cyan
        (255, 20, 147),   # Scarf – deep pink
    ]

    def __init__(self, model_name: str = "mattmdjaga/segformer_b2_clothes") -> None:
        """
        Initialise the segmentation model.  If the underlying models haven't
        been loaded yet they will be downloaded from Hugging Face and cached
        locally.  The model name can be overridden when instantiating
        additional models for experimentation.
        """
        # Store the name so that future calls reuse the same model.
        self.model_name = model_name
        self._ensure_loaded()

    @classmethod
    def _ensure_loaded(cls) -> None:
        """Load the processor and model if they haven't already been loaded."""
        if cls._processor is None or cls._model is None:
            # Download the processor and model.  They will be cached under
            # ~/.cache/huggingface so subsequent sessions avoid network calls.
            cls._processor = SegformerImageProcessor.from_pretrained(
                "mattmdjaga/segformer_b2_clothes"
            )
            cls._model = AutoModelForSemanticSegmentation.from_pretrained(
                "mattmdjaga/segformer_b2_clothes"
            )
            # Put the model into evaluation mode for inference.  We don't
            # enable gradients which saves memory and computation.
            cls._model.eval()

    def segment(self, image: Image.Image) -> Tuple[np.ndarray, Image.Image]:
        """
        Run semantic segmentation on the provided image.

        Parameters
        ----------
        image : PIL.Image
            The input image containing a person wearing clothing.  Any
            resolution is accepted; the model processor will handle
            resizing internally.

        Returns
        -------
        mask : numpy.ndarray
            A 2‑D array of shape `(H, W)` where each element is the class
            index assigned to the corresponding pixel.
        overlay : PIL.Image
            A visualisation of the segmentation mask overlaid on top of the
            original image.  Useful for inspecting segmentation quality.
        """
        # Preprocess the image into a batch of tensors.  The processor
        # normalises and resizes the image to the model's expected input
        # dimensions.  We request PyTorch tensors for compatibility with
        # AutoModelForSemanticSegmentation.
        inputs = self._processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = self._model(**inputs)

        # The model outputs logits in a shape (batch, num_labels, h, w).
        # We take the argmax along the channel dimension to obtain the
        # predicted label for each pixel.  The result is downsampled; we
        # upsample it back to the original image size using bilinear
        # interpolation so that the overlay aligns correctly.
        logits = outputs.logits
        upsampled_logits = torch.nn.functional.interpolate(
            logits,
            size=image.size[::-1],  # (H, W) order expected by interpolate
            mode="bilinear",
            align_corners=False,
        )
        pred_seg = upsampled_logits.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)

        # Build a coloured overlay.  We map each class index to an RGB colour.
        palette_arr = np.array(self.palette, dtype=np.uint8)
        # Ensure we have enough colours in case the palette is shorter than
        # the number of classes.  We cycle through the palette if needed.
        colours = palette_arr[pred_seg % len(palette_arr)]
        colour_image = Image.fromarray(colours, mode="RGB")
        # Blend the original image and the colour mask.  Alpha controls
        # transparency; a value of 0.4 makes the segmentation semi‑transparent.
        overlay = Image.blend(image.convert("RGB"), colour_image, alpha=0.4)
        return pred_seg, overlay

    def extract_clothing_crop(self, image: Image.Image, mask: np.ndarray) -> Image.Image:
        """
        Crop the input image to the bounding box that contains clothing items.

        We identify all pixels in the segmentation mask that correspond to
        garment classes (e.g. upper clothes, skirt, pants, dress).  A tight
        bounding box is computed around these pixels and a slightly larger
        crop is extracted from the original image.  If no garment pixels are
        detected the original image is returned.

        Parameters
        ----------
        image : PIL.Image
            The original input image.
        mask : numpy.ndarray
            A 2‑D array of class indices, such as returned by
            ``segment()``.

        Returns
        -------
        PIL.Image
            A cropped view of the clothing region, or the original image
            when no clothing was found.
        """
        # Define which class indices correspond to clothing items.  You can
        # modify this list to include additional garment types (e.g. bag or
        # scarf) if you wish to account for accessories.
        clothing_classes = {4, 5, 6, 7, 8, 16, 17}
        # Create a binary mask where garment pixels are True.
        clothing_mask = np.isin(mask, list(clothing_classes))
        # Find the coordinates of garment pixels.
        coords = np.column_stack(np.where(clothing_mask))  # (row, col)
        if coords.size == 0:
            # No garment pixels – return the original image unchanged.
            return image
        # Determine the bounding box.  Note that mask shape is (H, W).
        top, left = coords.min(axis=0)
        bottom, right = coords.max(axis=0)
        # Apply a small padding around the bounding box (10% of box size).
        h, w = mask.shape
        pad_y = int(0.1 * (bottom - top + 1))
        pad_x = int(0.1 * (right - left + 1))
        top = max(top - pad_y, 0)
        left = max(left - pad_x, 0)
        bottom = min(bottom + pad_y, h - 1)
        right = min(right + pad_x, w - 1)
        # Crop and return.
        return image.crop((left, top, right + 1, bottom + 1))
