from __future__ import annotations
from typing import Dict, Any, List
import numpy as np
from PIL import Image

from scripts.load_model import SegmentationModel
from scripts.style_predictor import StylePredictor


class OutfitClassifier:
    """
    - Segment to create an evidence/overlay image to show user.
    - Run FashionCLIP (StylePredictor) on the ORIGINAL image to get style candidates.
    - Return both.
    """

    def __init__(self):
        self.seg_model = SegmentationModel()
        self.style_predictor = StylePredictor()

    def process(self, image: Image.Image) -> Dict[str, Any]:
        # 1. segmentation (for visual feedback / fairness comms)
        mask, overlay = self.seg_model.segment(image)

        # 2. optional fairness masking (we won't use it yet, but keep if you want later)
        np_frame = np.array(image.convert("RGB"))
        face_mask = (mask == 11)  # 11 == face in seg labels
        if face_mask.any():
            np_frame[face_mask] = 0
        # masked_for_display = Image.fromarray(np_frame)  # not used right now

        # we choose overlay as "evidence" because it's visually cool
        evidence_image = overlay

        # 3. style prediction using ORIGINAL image (not masked)
        ranked_styles: List[Dict[str, float]] = self.style_predictor.predict(
            original_image=image
        )

        return {
            "evidence_image": evidence_image,
            "ranked_styles": ranked_styles,
        }
