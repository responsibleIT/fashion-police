"""
Database module for Fashion Police
Stores predictions and user feedback for model improvement
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json


class FashionDB:
    """SQLite database handler for storing predictions and feedback"""
    
    def __init__(self, db_path: str = "data/fashion_police.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table for predictions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT UNIQUE NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    image_path TEXT NOT NULL,
                    overlay_path TEXT NOT NULL,
                    top_prediction TEXT NOT NULL,
                    top_confidence REAL NOT NULL,
                    all_predictions TEXT NOT NULL,
                    user_correction TEXT,
                    feedback_timestamp DATETIME
                )
            """)
            
            conn.commit()
    
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO predictions 
                    (record_id, image_path, overlay_path, top_prediction, top_confidence, all_predictions)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    record_id,
                    image_path,
                    overlay_path,
                    predictions[0]["name"],
                    predictions[0]["score"],
                    json.dumps(predictions)
                ))
                conn.commit()
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE predictions 
                    SET user_correction = ?, feedback_timestamp = CURRENT_TIMESTAMP
                    WHERE record_id = ?
                """, (user_correction, record_id))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False
    
    def get_prediction(self, record_id: str) -> Optional[Dict]:
        """Get a prediction by record_id"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM predictions WHERE record_id = ?
            """, (record_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_all_predictions(self, limit: int = 100) -> List[Dict]:
        """Get all predictions, most recent first"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM predictions 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM predictions")
            total_predictions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_correction IS NOT NULL")
            total_feedback = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT top_prediction, COUNT(*) as count 
                FROM predictions 
                GROUP BY top_prediction 
                ORDER BY count DESC
            """)
            top_predictions = cursor.fetchall()
            
            cursor.execute("""
                SELECT user_correction, COUNT(*) as count 
                FROM predictions 
                WHERE user_correction IS NOT NULL
                GROUP BY user_correction 
                ORDER BY count DESC
            """)
            corrections = cursor.fetchall()
            
            return {
                "total_predictions": total_predictions,
                "total_feedback": total_feedback,
                "feedback_rate": total_feedback / total_predictions if total_predictions > 0 else 0,
                "top_predictions": top_predictions,
                "user_corrections": corrections
            }
