"""
classify_outfit.py
-------------------

This module combines **clothing segmentation** and **style prediction** into a single
unified class, `OutfitClassifier`, that performs both tasks on a given image.

Usage
-----
>>> classifier = OutfitClassifier()
>>> predictions, overlay = classifier.classify(image)
>>> print(predictions[0])  # highest-scoring style
>>> overlay.show()
"""

from __future__ import annotations

from PIL import Image
from typing import List, Dict, Tuple

from .load_model import SegmentationModel
from .style_predictor import StylePredictor


class OutfitClassifier:
    """
    High-level class that orchestrates segmentation + style classification.
    
    This is the main entry point for Fashion Police's ML pipeline.
    """

    def __init__(self) -> None:
        """Initialize both the segmentation model and the style predictor."""
        print("Loading segmentation model...")
        self.seg_model = SegmentationModel()
        print("Loading FashionCLIP style predictor...")
        self.style_predictor = StylePredictor()
        print("Outfit classifier ready!")

    def classify(self, image: Image.Image) -> Tuple[List[Dict], Image.Image, Image.Image]:
        """
        Classify the outfit in the image into fashion styles.

        Parameters
        ----------
        image : PIL.Image
            The input image containing a person wearing clothing.

        Returns
        -------
        predictions : List[Dict]
            A list of style predictions sorted by confidence score.
            Each dict contains:
                - 'name': str (style name)
                - 'score': float (similarity score 0-1)
                - 'description': str (style description)
        
        display_overlay : PIL.Image
            A visualisation of the segmentation mask overlaid on the
            original image with colored clothing regions (for web display).
        
        anonymized_overlay : PIL.Image
            A privacy-preserving version with only background (white) and
            face (black) colored, keeping clothing as original (for storage).
        """
        # Run segmentation to get both overlays
        _, display_overlay, anonymized_overlay = self.seg_model.segment(image)
        
        # Run style prediction
        predictions = self.style_predictor.predict(image)
        
        return predictions, display_overlay, anonymized_overlay
