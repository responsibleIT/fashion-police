# Fashion Police - Flask Camera App for Raspberry PiInstall requirements.txt

Run the app with command "streamlit run src/app.py"

A lightweight Flask web application that runs on Raspberry Pi, captures photos via webcam, and sends them to an API for style analysis.

## Features

✅ **Camera Control** - Full JavaScript-based webcam handling  
✅ **Clean UI** - Responsive design with external CSS/JS  
✅ **API Ready** - Structured for future API integration  
✅ **Lightweight** - Minimal dependencies (~30MB)  
✅ **Touch-Friendly** - Optimized for touchscreen displays  

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements-flask.txt
```

### 2. Run the Application
```bash
python flask_app.py
```

### 3. Access the App
- **On Raspberry Pi**: http://localhost:5000
- **From another device**: http://PI_IP_ADDRESS:5000

## Project Structure

```
fashion-police/
├── flask_app.py              # Main Flask application
├── requirements-flask.txt    # Python dependencies
├── templates/
│   ├── camera.html          # Camera capture page
│   ├── results.html         # Results display page
│   └── feedback.html        # User feedback page
└── static/
    ├── css/
    │   ├── common.css       # Shared styles
    │   ├── camera.css       # Camera page styles
    │   ├── results.css      # Results page styles
    │   └── feedback.css     # Feedback page styles
    └── js/
        ├── camera.js        # Camera functionality
        └── feedback.js      # Feedback handling
```

## How It Works

### 1. Camera Page (`/`)
- Automatically starts webcam
- Capture photo with one click
- Preview before submitting
- Retake option available

### 2. Results Page (`/results`)
- Displays captured photo
- Shows style predictions (currently dummy data)
- Highlights top prediction
- Option to provide feedback

### 3. Feedback Page (`/feedback`)
- Shows captured photo
- Grid of style options
- Submit correction if prediction is wrong

## Hardware Requirements

- **Raspberry Pi 5** (or compatible)
- **USB Webcam**
- **Touchscreen Display** (optional but recommended)
- **Docking Station** (if using touchscreen + webcam simultaneously)

### Power Considerations

⚠️ **Important**: USB touchscreens draw significant power. If your webcam shuts down when the touchscreen is connected, use a powered docking station to connect both peripherals.

## API Integration (Future)

Currently returns dummy responses. To connect to a real inference API, modify `flask_app.py`:

```python
def get_dummy_response() -> dict:
    # Replace with:
    import requests
    response = requests.post(
        'http://your-api-server:8000/predict',
        files={'image': image_data}
    )
    return response.json()
```

## API Endpoints

- `GET /` - Camera capture page
- `POST /process_image` - Process captured image (returns dummy predictions)
- `GET /results` - Display results page
- `GET /feedback` - Feedback collection page
- `POST /submit_feedback` - Submit user feedback

## Browser Compatibility

Works best with:
- Chrome/Chromium (recommended for Pi)
- Firefox
- Safari (iOS)

**Note**: Camera access requires:
- HTTPS connection OR localhost
- User permission (browser will prompt)

## Troubleshooting

### Camera Won't Start
1. Check browser permissions (camera icon in address bar)
2. Verify webcam is connected and recognized: `ls /dev/video*`
3. Check browser console (F12) for errors

### Camera Shuts Down
- **Cause**: Insufficient USB power
- **Solution**: Use powered USB hub or docking station

### Can't Access from Other Devices
```bash
# Check firewall settings
sudo ufw status
sudo ufw allow 5000
```

### Port Already in Use
Change port in `flask_app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

## Development

The app is structured with separation of concerns:
- **Python**: Flask backend logic
- **HTML**: Page structure
- **CSS**: Styling (modular, one file per page + shared)
- **JavaScript**: Camera control and interactivity

To modify styles or behavior, edit the respective files in `static/css/` or `static/js/`.

## License

[Your License Here]
