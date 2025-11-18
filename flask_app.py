"""
Flask-based Fashion Police Pi Client
More control over camera and UI than Streamlit
"""

from flask import Flask, render_template, request, jsonify, session
import base64
import io
from PIL import Image
import time
import secrets
from pathlib import Path

from src.scripts.classify_outfit import OutfitClassifier
from src.database import FashionDB

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Store results in memory (could use Redis/DB for production)
results_store = {}

# Initialize database and storage directories
db = FashionDB("data/fashion_police.db")
DATA_DIR = Path("data/images")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load the outfit classifier at startup
print("Initializing Fashion Police ML models...")
classifier = OutfitClassifier()
print("Fashion Police is ready!")


@app.route('/')
def index():
    """Main camera page"""
    return render_template('camera.html')


@app.route('/process_image', methods=['POST'])
def process_image():
    """Process captured image and return predictions"""
    data = request.get_json()
    image_data = data.get('image')
    
    if not image_data:
        return jsonify({'error': 'No image provided'}), 400
    
    # Decode base64 image
    image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64, prefix
    image_bytes = base64.b64decode(image_data)
    
    # Convert to PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    
    # Run FashionCLIP inference
    predictions, overlay = classifier.classify(image)
    
    # Generate record ID
    record_id = f"outfit_{int(time.time())}"
    
    # Save anonymized overlay image to disk (ONLY the overlay, not original photo)
    overlay_filename = f"{record_id}_overlay.jpg"
    overlay_path = DATA_DIR / overlay_filename
    overlay.save(overlay_path, format='JPEG', quality=95)
    
    # Convert overlay to base64 for web display
    overlay_buffer = io.BytesIO()
    overlay.save(overlay_buffer, format='JPEG', quality=95)
    overlay_base64 = base64.b64encode(overlay_buffer.getvalue()).decode('utf-8')
    
    # Build result structure
    result = {
        "record_id": record_id,
        "predictions": [
            {
                "name": pred["name"],
                "description": pred["description"],
                "confidence": pred["score"]
            }
            for pred in predictions
        ],
        "top_prediction": {
            "name": predictions[0]["name"],
            "description": predictions[0]["description"],
            "confidence": predictions[0]["score"]
        }
    }
    
    # Save prediction to database
    db.save_prediction(
        record_id=record_id,
        image_path=str(overlay_path),
        overlay_path=str(overlay_path),
        predictions=predictions
    )
    
    # Store result in memory for session
    results_store[record_id] = {
        'result': result,
        'image': image_data,
        'overlay': overlay_base64
    }
    
    # Store in session
    session['current_record_id'] = record_id
    
    return jsonify(result)


@app.route('/results')
def results():
    """Results page"""
    record_id = session.get('current_record_id')
    if not record_id or record_id not in results_store:
        return "No results available. Please take a photo first.", 404
    
    data = results_store[record_id]
    return render_template('results.html', 
                         result=data['result'], 
                         image_data=data['image'],
                         overlay_data=data['overlay'])


@app.route('/feedback')
def feedback():
    """Feedback page"""
    record_id = session.get('current_record_id')
    if not record_id or record_id not in results_store:
        return "No results available. Please take a photo first.", 404
    
    data = results_store[record_id]
    
    styles = [
        "Urban Streetwear", "Formal Business", "Casual Chic",
        "Sporty / Athleisure", "Vintage / Retro", "Bohemian",
        "Elegant Evening", "Preppy", "Punk / Alt", "Gothic",
        "Artsy / Expressive"
    ]
    
    return render_template('feedback.html', 
                         styles=styles,
                         image_data=data['image'])


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    """Handle feedback submission"""
    data = request.get_json()
    style = data.get('style')
    record_id = session.get('current_record_id')
    
    if not record_id:
        return jsonify({'error': 'No active session'}), 400
    
    # Save user correction to database
    success = db.save_feedback(record_id, style)
    
    if success:
        print(f"Feedback saved: {record_id} -> {style}")
    
    return jsonify({'success': success, 'style': style})


@app.route('/stats')
def statistics():
    """Display statistics dashboard"""
    stats = db.get_statistics()
    return render_template('stats.html', stats=stats)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
