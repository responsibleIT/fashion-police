from __future__ import annotations
from typing import Tuple, List
import numpy as np
from PIL import Image
from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
import torch

class SegmentationModel:
    _processor: SegformerImageProcessor | None = None
    _model: AutoModelForSemanticSegmentation | None = None
    
    id2label: dict[int, str] = {
        0: "Background", 1: "Hat", 2: "Hair", 3: "Sunglasses",
        4: "Upper-clothes", 5: "Skirt", 6: "Pants", 7: "Dress",
        8: "Belt", 9: "Left-shoe", 10: "Right-shoe", 11: "Face",
        12: "Left-leg", 13: "Right-leg", 14: "Left-arm", 15: "Right-arm",
        16: "Bag", 17: "Scarf"
    }
    
    palette: List[Tuple[int, int, int]] = [
        (255, 255, 255), (128, 0, 0), (255, 0, 0), (255, 165, 0),
        (255, 192, 203), (255, 105, 180), (255, 0, 255), (219, 112, 147),
        (255, 255, 0), (0, 128, 0), (34, 139, 34), (0, 0, 0),
        (75, 0, 130), (138, 43, 226), (0, 191, 255), (135, 206, 235),
        (0, 255, 255), (255, 20, 147)
    ]
    
    def __init__(self, model_name: str = "mattmdjaga/segformer_b2_clothes") -> None:
        self.model_name = model_name
        self._ensure_loaded()
    
    @classmethod
    def _ensure_loaded(cls) -> None:
        if cls._processor is None or cls._model is None:
            cls._processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
            cls._model = AutoModelForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")
            cls._model.eval()
    
    def segment(self, image: Image.Image) -> Tuple[np.ndarray, Image.Image, Image.Image]:
        inputs = self._processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = self._model(**inputs)
        logits = outputs.logits
        upsampled_logits = torch.nn.functional.interpolate(
            logits, size=image.size[::-1], mode="bilinear", align_corners=False
        )
        pred_seg = upsampled_logits.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)
        
        # Create display overlay (with colored clothing) starting from original image
        display_overlay = image.convert("RGB").copy()
        display_arr = np.array(display_overlay)
        
        # Create anonymized overlay (only background and face colored)
        anonymized_overlay = image.convert("RGB").copy()
        anonymized_arr = np.array(anonymized_overlay)
        
        # Make face (class 11) solid black in both overlays
        face_mask = pred_seg == 11
        display_arr[face_mask] = [0, 0, 0]
        anonymized_arr[face_mask] = [0, 0, 0]
        
        # Make background (class 0) solid white in both overlays
        bg_mask = pred_seg == 0
        display_arr[bg_mask] = [255, 255, 255]
        anonymized_arr[bg_mask] = [255, 255, 255]
        
        # For display overlay: blend clothing regions with transparency
        palette_arr = np.array(self.palette, dtype=np.uint8)
        colours = palette_arr[pred_seg % len(palette_arr)]
        colour_image = Image.fromarray(colours, mode="RGB")
        
        # Apply transparent overlay only to non-face, non-background regions (display only)
        other_mask = ~(face_mask | bg_mask)
        if other_mask.any():
            display_img = Image.fromarray(display_arr)
            blended = Image.blend(display_img, colour_image, alpha=0.4)
            blended_arr = np.array(blended)
            display_arr[other_mask] = blended_arr[other_mask]
        
        # For anonymized overlay: keep original clothing (no coloring)
        # anonymized_arr already has original image for clothing regions
        
        display_overlay = Image.fromarray(display_arr)
        anonymized_overlay = Image.fromarray(anonymized_arr)
        return pred_seg, display_overlay, anonymized_overlay
