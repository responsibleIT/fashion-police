"""
data_storage.py
---------------

This module handles storing user data including images, system predictions,
and user corrections for the Fashion Police application.

Data is stored in a simple JSON file with images saved separately.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
from PIL import Image


class DataStorage:
    """Handles saving and loading fashion classification data."""
    
    def __init__(self, storage_dir: str = "data/saved"):
        """
        Initialize the data storage.
        
        Parameters
        ----------
        storage_dir : str
            Directory where data will be stored.
        """
        self.storage_dir = Path(storage_dir)
        self.images_dir = self.storage_dir / "images"
        self.metadata_file = self.storage_dir / "classifications.json"
        
        # Create directories if they don't exist
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metadata file if it doesn't exist
        if not self.metadata_file.exists():
            self._save_metadata([])
    
    def _save_metadata(self, data: list) -> None:
        """Save metadata to JSON file."""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_metadata(self) -> list:
        """Load metadata from JSON file."""
        if not self.metadata_file.exists():
            return []
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _anonymize_image(self, image: Image.Image, mask: Optional[np.ndarray] = None) -> Image.Image:
        """
        Anonymize image by showing only clothing and hair, blacking out the person,
        and making the background white.
        
        Parameters
        ----------
        image : PIL.Image
            The original image to anonymize.
        mask : numpy.ndarray, optional
            Segmentation mask where each pixel value represents a class.
            If None, returns the original image.
            
        Returns
        -------
        PIL.Image
            Anonymized image with clothing/hair visible, person blacked out, 
            and background white.
        """
        if mask is None:
            return image
        
        # Define classes to keep visible: clothing + hair
        # 2: Hair, 4: Upper-clothes, 5: Skirt, 6: Pants, 7: Dress, 8: Belt, 16: Bag, 17: Scarf
        visible_classes = {2, 4, 5, 6, 7, 8, 16, 17}
        
        # Background class
        background_class = 0
        
        # Create masks
        visible_mask = np.isin(mask, list(visible_classes))
        background_mask = mask == background_class
        
        # Convert image to numpy array
        img_array = np.array(image)
        
        # Create anonymized version
        anonymized = img_array.copy()
        
        # Set background to white
        anonymized[background_mask] = [255, 255, 255]
        
        # Set person parts (non-clothing, non-background) to black
        person_mask = ~visible_mask & ~background_mask
        anonymized[person_mask] = [0, 0, 0]
        
        # Convert back to PIL Image
        return Image.fromarray(anonymized)
    
    def save_classification(
        self,
        image: Image.Image,
        system_guess: str,
        system_confidence: float,
        user_input: Optional[str] = None,
        all_predictions: Optional[list] = None,
        mask: Optional[np.ndarray] = None
    ) -> str:
        """
        Save a classification record with anonymized image.
        
        Parameters
        ----------
        image : PIL.Image
            The outfit image to save.
        system_guess : str
            The top prediction from the system.
        system_confidence : float
            Confidence score for the system's guess.
        user_input : str, optional
            The user's correction/input for the actual style.
        all_predictions : list, optional
            Full list of ranked predictions from the system.
        mask : numpy.ndarray, optional
            Segmentation mask for anonymization. If provided, non-clothing
            pixels will be blacked out before saving.
            
        Returns
        -------
        str
            The ID of the saved record.
        """
        # Generate unique ID based on timestamp
        timestamp = datetime.now()
        record_id = timestamp.strftime("%Y%m%d_%H%M%S_%f")
        
        # Anonymize image before saving
        anonymized_image = self._anonymize_image(image, mask)
        
        # Save anonymized image
        image_filename = f"{record_id}.png"
        image_path = self.images_dir / image_filename
        anonymized_image.save(image_path, format="PNG")
        
        # Create metadata record
        record = {
            "id": record_id,
            "timestamp": timestamp.isoformat(),
            "image_path": str(image_path.relative_to(self.storage_dir)),
            "system_guess": system_guess,
            "system_confidence": system_confidence,
            "user_input": user_input,
            "all_predictions": all_predictions or [],
            "is_correct": user_input == system_guess if user_input else None
        }
        
        # Load existing data, append new record, and save
        metadata = self._load_metadata()
        metadata.append(record)
        self._save_metadata(metadata)
        
        return record_id
    
    def update_user_input(self, record_id: str, user_input: str) -> bool:
        """
        Update an existing record with user input.
        
        Parameters
        ----------
        record_id : str
            The ID of the record to update.
        user_input : str
            The user's correction/input for the actual style.
            
        Returns
        -------
        bool
            True if update was successful, False otherwise.
        """
        metadata = self._load_metadata()
        
        for record in metadata:
            if record["id"] == record_id:
                record["user_input"] = user_input
                record["is_correct"] = user_input == record["system_guess"]
                self._save_metadata(metadata)
                return True
        
        return False
    
    def get_all_records(self) -> list:
        """Get all saved classification records."""
        return self._load_metadata()
    
    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific record by ID."""
        metadata = self._load_metadata()
        for record in metadata:
            if record["id"] == record_id:
                return record
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about saved data.
        
        Returns
        -------
        dict
            Statistics including total records, accuracy, etc.
        """
        metadata = self._load_metadata()
        
        total = len(metadata)
        with_user_input = sum(1 for r in metadata if r.get("user_input"))
        correct = sum(1 for r in metadata if r.get("is_correct") is True)
        
        stats = {
            "total_classifications": total,
            "with_user_feedback": with_user_input,
            "correct_predictions": correct,
            "accuracy": correct / with_user_input if with_user_input > 0 else 0.0
        }
        
        return stats
