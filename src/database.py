"""
Database module for Fashion Police
Stores predictions and user feedback for model improvement
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class FashionDB:
    """JSON-based database handler for storing predictions and feedback"""
    
    def __init__(self, db_path: str = "data/predictions.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize JSON file if it doesn't exist"""
        if not self.db_path.exists():
            self._write_data({"predictions": []})
    
    def _read_data(self) -> Dict:
        """Read data from JSON file"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"predictions": []}
    
    def _write_data(self, data: Dict):
        """Write data to JSON file"""
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_prediction(
        self,
        record_id: str,
        image_path: str,
        overlay_path: str,
        predictions: List[Dict]
    ) -> bool:
        """
        Save a new prediction to the database
        
        Args:
            record_id: Unique identifier for this prediction
            image_path: Path to anonymized overlay image
            overlay_path: Path to segmentation overlay
            predictions: List of style predictions with scores
        
        Returns:
            True if successful
        """
        try:
            data = self._read_data()
            
            prediction_record = {
                "record_id": record_id,
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "overlay_path": overlay_path,
                "top_prediction": predictions[0]["name"],
                "top_confidence": predictions[0]["score"],
                "all_predictions": predictions,
                "user_correction": None,
                "feedback_timestamp": None
            }
            
            data["predictions"].append(prediction_record)
            self._write_data(data)
            return True
        except Exception as e:
            print(f"Error saving prediction: {e}")
            return False
    
    def save_feedback(self, record_id: str, user_correction: str) -> bool:
        """
        Save user feedback/correction for a prediction
        
        Args:
            record_id: The record to update
            user_correction: The style the user says is correct
        
        Returns:
            True if successful
        """
        try:
            data = self._read_data()
            
            for prediction in data["predictions"]:
                if prediction["record_id"] == record_id:
                    prediction["user_correction"] = user_correction
                    prediction["feedback_timestamp"] = datetime.now().isoformat()
                    break
            
            self._write_data(data)
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False
    
    def get_prediction(self, record_id: str) -> Optional[Dict]:
        """Get a prediction by record_id"""
        data = self._read_data()
        for prediction in data["predictions"]:
            if prediction["record_id"] == record_id:
                return prediction
        return None
    
    def get_all_predictions(self, limit: int = 100) -> List[Dict]:
        """Get all predictions, most recent first"""
        data = self._read_data()
        predictions = data["predictions"]
        # Sort by timestamp descending
        predictions.sort(key=lambda x: x["timestamp"], reverse=True)
        return predictions[:limit]
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        data = self._read_data()
        predictions = data["predictions"]
        
        total_predictions = len(predictions)
        total_feedback = sum(1 for p in predictions if p["user_correction"] is not None)
        
        # Count top predictions
        top_pred_counts = {}
        for p in predictions:
            style = p["top_prediction"]
            top_pred_counts[style] = top_pred_counts.get(style, 0) + 1
        
        top_predictions = sorted(top_pred_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Count user corrections
        correction_counts = {}
        for p in predictions:
            if p["user_correction"]:
                style = p["user_correction"]
                correction_counts[style] = correction_counts.get(style, 0) + 1
        
        corrections = sorted(correction_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_predictions": total_predictions,
            "total_feedback": total_feedback,
            "feedback_rate": total_feedback / total_predictions if total_predictions > 0 else 0,
            "top_predictions": top_predictions,
            "user_corrections": corrections
        }
