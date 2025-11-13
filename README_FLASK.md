# Flask Version - Setup Guide

## Why Flask?

✅ **Full camera control** - JavaScript directly handles webcam
✅ **Better performance** - No constant page reloads
✅ **Cleaner UI** - Custom HTML/CSS
✅ **Camera stays on** - No automatic shutoff issues
✅ **Even lighter** - Only ~30MB dependencies

## Installation

```bash
# 1. Install dependencies
pip install -r requirements-flask.txt

# 2. Run the Flask app
python flask_app.py

# 3. Access in browser
# http://localhost:5000
# or from another device: http://PI_IP:5000
```

## How It Works

### Camera Page (`/`)
- Camera starts automatically on page load
- Click "Capture Photo" to take picture
- Camera stops after capture (saves resources)
- Click "Retake" to restart camera if needed
- Click "Analyze Style" to get predictions

### Results Page (`/results`)
- Shows your photo and predictions
- Top prediction highlighted in green
- Other matches listed below
- "Take Another Photo" goes back to camera
- "Correct me if I am wrong" goes to feedback

### Feedback Page (`/feedback`)
- Shows your photo
- Grid of style buttons
- Click any style to submit feedback
- Success message appears
- Can go back to results

## Advantages Over Streamlit

1. **Camera Control**: JavaScript handles camera directly - no automatic shutoff
2. **Performance**: No full page reloads on every interaction
3. **Customization**: Full control over HTML/CSS/JS
4. **Debugging**: Easier to see what's happening in browser console
5. **Mobile Friendly**: Better responsive design

## File Structure

```
fashion-police/
├── flask_app.py           # Main Flask application
├── templates/
│   ├── camera.html        # Camera capture page
│   ├── results.html       # Results display page
│   └── feedback.html      # Feedback collection page
└── requirements-flask.txt # Dependencies
```

## API Endpoints

- `GET /` - Camera page
- `POST /process_image` - Process captured image
- `GET /results` - Results page
- `GET /feedback` - Feedback page
- `POST /submit_feedback` - Submit user feedback

## Future: Connect to Real Server

Replace in `flask_app.py`:

```python
def get_dummy_response() -> dict:
    # Current: returns hardcoded response
    
    # Future: 
    import requests
    response = requests.post(
        'http://your-server:8000/predict',
        files={'image': image_file}
    )
    return response.json()
```

## Troubleshooting

### Camera not working?
1. Check browser permissions (camera icon in address bar)
2. Try HTTPS or localhost (not Pi's IP)
3. Check browser console (F12) for errors

### Port already in use?
```bash
# Change port in flask_app.py:
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Can't access from other devices?
```bash
# Make sure firewall allows port 5000
# On Pi:
sudo ufw allow 5000
```

## Testing

1. Open browser to `http://localhost:5000`
2. Allow camera permissions
3. Camera should start automatically
4. Take a photo
5. Click "Analyze Style"
6. See dummy results
7. Try feedback flow

Everything should work smoothly with no camera shutoff issues!
