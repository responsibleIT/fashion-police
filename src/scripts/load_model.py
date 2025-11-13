""""""

load_model.pyload_model.py

--------------------------------



This module defines the segmentation model used by the Fashion Police app.This module defines classes responsible for loading and caching the

underlying machine learning models used by the Fashion Police app.

The **clothing segmentation model** is based on the SegFormer architecture.

It accepts an image and returns a segmentation map where each pixel isThere are two primary models used in this project:

assigned a class label. We use this map to create a visual overlay.

"""1. A **clothing segmentation model** based on the SegFormer architecture.

   It accepts an image and returns a segmentation map where each pixel is

from __future__ import annotations   assigned a class label.  We use this map to isolate the regions

   containing clothing items.  Without segmentation the classifier might

from typing import Tuple, List   accidentally focus on background features (e.g. the colour of the wall) and

   produce poor predictions.

import numpy as np

from PIL import Image2. A **clothing classification model** fine‑tuned from a Vision Transformer.

   Given an image (ideally of the cropped clothing region) it returns a

from transformers import (   predicted clothing category.  We use the class names defined by the

    SegformerImageProcessor,   model's config to map prediction indices into human readable labels.

    AutoModelForSemanticSegmentation,

)Both classes defined below lazily load their underlying models the first

import torchtime they're used.  Subsequent calls reuse the cached instances stored

in class variables.  This pattern avoids repeatedly downloading models

from Hugging Face and improves latency during runtime.

class SegmentationModel:

    """Wrapper around a Hugging Face segmentation model for clothing."""Usage example:



    # Class-wide caches so that loading happens only once per session.    from PIL import Image

    _processor: SegformerImageProcessor | None = None    from fashion_police.src.scripts.load_model import SegmentationModel, ClassificationModel

    _model: AutoModelForSemanticSegmentation | None = None

    seg_model = SegmentationModel()

    # The mapping from class IDs to human readable labels    seg_map, overlay = seg_model.segment(Image.open("person.jpg"))

    id2label: dict[int, str] = {

        0: "Background",    cls_model = ClassificationModel()

        1: "Hat",    label, score = cls_model.classify(Image.open("shirt_crop.jpg"))

        2: "Hair","""

        3: "Sunglasses",

        4: "Upper-clothes",from __future__ import annotations

        5: "Skirt",

        6: "Pants",import functools

        7: "Dress",from typing import Tuple, List

        8: "Belt",

        9: "Left-shoe",import numpy as np

        10: "Right-shoe",from PIL import Image

        11: "Face",

        12: "Left-leg",from transformers import (

        13: "Right-leg",    SegformerImageProcessor,

        14: "Left-arm",    AutoModelForSemanticSegmentation,

        15: "Right-arm",    AutoImageProcessor,

        16: "Bag",    AutoModelForImageClassification,

        17: "Scarf",)

    }import torch



    # Color palette for visualising each class

    palette: List[Tuple[int, int, int]] = [class SegmentationModel:

        (0, 0, 0),        # Background – black    """Wrapper around a Hugging Face segmentation model for clothing."""

        (128, 0, 0),      # Hat – maroon

        (255, 0, 0),      # Hair – red    # Class‑wide caches so that loading happens only once per session.

        (255, 165, 0),    # Sunglasses – orange    _processor: SegformerImageProcessor | None = None

        (255, 192, 203),  # Upper-clothes – pink    _model: AutoModelForSemanticSegmentation | None = None

        (255, 105, 180),  # Skirt – hot pink

        (255, 0, 255),    # Pants – magenta    # The mapping from class IDs to human readable labels defined by the

        (219, 112, 147),  # Dress – pale violet red    # underlying segmentation model.  These come from the ATR dataset used

        (255, 255, 0),    # Belt – yellow    # during fine‑tuning.  Not all labels correspond to garments; we'll

        (0, 128, 0),      # Left shoe – green    # extract only the garment indices when cropping.

        (34, 139, 34),    # Right shoe – forest green    id2label: dict[int, str] = {

        (255, 228, 196),  # Face – bisque        0: "Background",

        (75, 0, 130),     # Left leg – indigo        1: "Hat",

        (138, 43, 226),   # Right leg – blue violet        2: "Hair",

        (0, 191, 255),    # Left arm – deep sky blue        3: "Sunglasses",

        (135, 206, 235),  # Right arm – sky blue        4: "Upper-clothes",

        (0, 255, 255),    # Bag – cyan        5: "Skirt",

        (255, 20, 147),   # Scarf – deep pink        6: "Pants",

    ]        7: "Dress",

        8: "Belt",

    def __init__(self, model_name: str = "mattmdjaga/segformer_b2_clothes") -> None:        9: "Left-shoe",

        """Initialize the segmentation model."""        10: "Right-shoe",

        self.model_name = model_name        11: "Face",

        self._ensure_loaded()        12: "Left-leg",

        13: "Right-leg",

    @classmethod        14: "Left-arm",

    def _ensure_loaded(cls) -> None:        15: "Right-arm",

        """Load the processor and model if they haven't already been loaded."""        16: "Bag",

        if cls._processor is None or cls._model is None:        17: "Scarf",

            cls._processor = SegformerImageProcessor.from_pretrained(    }

                "mattmdjaga/segformer_b2_clothes"

            )    # A simple colour palette for visualising each class.  Colours are

            cls._model = AutoModelForSemanticSegmentation.from_pretrained(    # arbitrary but distinct; the index in the list corresponds to the

                "mattmdjaga/segformer_b2_clothes"    # class ID.  When adding new classes ensure there are at least as many

            )    # colours as there are labels.

            cls._model.eval()    palette: List[Tuple[int, int, int]] = [

        (0, 0, 0),        # Background – black

    def segment(self, image: Image.Image) -> Tuple[np.ndarray, Image.Image]:        (128, 0, 0),      # Hat – maroon

        """        (255, 0, 0),      # Hair – red

        Run semantic segmentation on the provided image.        (255, 165, 0),    # Sunglasses – orange

        (255, 192, 203),  # Upper‑clothes – pink

        Parameters        (255, 105, 180),  # Skirt – hot pink

        ----------        (255, 0, 255),    # Pants – magenta

        image : PIL.Image        (219, 112, 147),  # Dress – pale violet red

            The input image containing a person wearing clothing.        (255, 255, 0),    # Belt – yellow

        (0, 128, 0),      # Left shoe – green

        Returns        (34, 139, 34),    # Right shoe – forest green

        -------        (255, 228, 196),  # Face – bisque

        mask : numpy.ndarray        (75, 0, 130),     # Left leg – indigo

            A 2-D array of shape (H, W) where each element is the class        (138, 43, 226),   # Right leg – blue violet

            index assigned to the corresponding pixel.        (0, 191, 255),    # Left arm – deep sky blue

        overlay : PIL.Image        (135, 206, 235),  # Right arm – sky blue

            A visualisation of the segmentation mask overlaid on top of the        (0, 255, 255),    # Bag – cyan

            original image.        (255, 20, 147),   # Scarf – deep pink

        """    ]

        inputs = self._processor(images=image, return_tensors="pt")

    def __init__(self, model_name: str = "mattmdjaga/segformer_b2_clothes") -> None:

        with torch.no_grad():        """

            outputs = self._model(**inputs)        Initialise the segmentation model.  If the underlying models haven't

        been loaded yet they will be downloaded from Hugging Face and cached

        logits = outputs.logits        locally.  The model name can be overridden when instantiating

        upsampled_logits = torch.nn.functional.interpolate(        additional models for experimentation.

            logits,        """

            size=image.size[::-1],  # (H, W) order expected by interpolate        # Store the name so that future calls reuse the same model.

            mode="bilinear",        self.model_name = model_name

            align_corners=False,        self._ensure_loaded()

        )

        pred_seg = upsampled_logits.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)    @classmethod

    def _ensure_loaded(cls) -> None:

        # Build a colored overlay        """Load the processor and model if they haven't already been loaded."""

        palette_arr = np.array(self.palette, dtype=np.uint8)        if cls._processor is None or cls._model is None:

        colours = palette_arr[pred_seg % len(palette_arr)]            # Download the processor and model.  They will be cached under

        colour_image = Image.fromarray(colours, mode="RGB")            # ~/.cache/huggingface so subsequent sessions avoid network calls.

        overlay = Image.blend(image.convert("RGB"), colour_image, alpha=0.4)            cls._processor = SegformerImageProcessor.from_pretrained(

                        "mattmdjaga/segformer_b2_clothes"

        return pred_seg, overlay            )

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
