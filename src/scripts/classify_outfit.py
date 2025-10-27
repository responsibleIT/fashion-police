from __future__ import annotations
from typing import Dict, Any
import numpy as np
from PIL import Image

from scripts.load_model import SegmentationModel
from scripts.style_predictor import StylePredictor


class OutfitClassifier:
    """Main pipeline combining segmentation and style prediction."""

    def __init__(self):
        self.seg_model = SegmentationModel()
        self.style_predictor = StylePredictor()

    def process(self, image: Image.Image) -> Dict[str, Any]:
        # Step 1: Run segmentation
        mask, overlay = self.seg_model.segment(image)

        # Step 2: Mask out the face for fairness
        np_image = np.array(image.convert("RGB"))
        face_mask = (mask == 11)  # class 11 is face
        if face_mask.any():
            np_image[face_mask] = 0
        masked_image = Image.fromarray(np_image)

        # Step 3: Run the style predictor directly
        style, style_score, style_desc = self.style_predictor.predict(masked_image)

        return {
            "mask": mask,
            "overlay": overlay,
            "style": style,
            "style_score": style_score,
            "style_description": style_desc,
        }
