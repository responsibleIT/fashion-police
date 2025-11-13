
# Fashion Police - Flask Camera App for Raspberry Pi

A lightweight Flask web application that runs on Raspberry Pi, captures photos via webcam, and sends them to an API for style analysis.

## Features

✅ **AI-Powered Pose Detection** - T-pose gesture to capture photos hands-free  
✅ **Real-time Bounding Box** - MoveNet AI tracks person in camera feed  
✅ **Fullscreen Portrait Mode** - Optimized for vertical touchscreen displays  
✅ **Mirror Mode** - Camera feed flipped for intuitive positioning  
✅ **Clean UI** - Minimal, distraction-free interface  
✅ **API Ready** - Structured for future style analysis integration  
✅ **Touch-Friendly** - Optimized for Raspberry Pi touchscreen displays  

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
│   ├── camera.html           # Camera capture page
│   ├── results.html          # Results display page
│   └── feedback.html         # User feedback page
└── static/
    ├── css/
    │   ├── common.css        # Shared styles
    │   ├── camera.css        # Camera page styles
    │   ├── results.css       # Results page styles
    │   └── feedback.css      # Feedback page styles
    └── js/
        ├── camera.js         # Camera functionality
        └── feedback.js       # Feedback handling
```

## How It Works

### 1. Camera Page (`/`)
- **Automatic camera startup** with fullscreen portrait view
- **Real-time AI person detection** using TensorFlow.js MoveNet
- **Green bounding box** tracks detected person
- **T-pose gesture capture**: Extend arms horizontally and hold for 2 seconds
- **Orange bounding box + progress bar** appears when T-pose detected
- **Manual capture button** available as backup
- **Mirror mode** for intuitive self-positioning
- **Preview and retake** options before final submission

### 2. Results Page (`/results`)
- Displays captured photo
- Shows style predictions (currently dummy data)
- Highlights top prediction
- Option to provide feedback

### 3. Feedback Page (`/feedback`)
- Shows captured photo
- Grid of style options
- Submit correction if prediction is wrong
- Returns to start screen after submission

## Technologies

### Frontend
- **TensorFlow.js** - Browser-based machine learning
- **MoveNet (Lightning)** - Real-time pose estimation model
- **MediaDevices API** - Webcam access and control
- **Canvas API** - Overlay graphics and bounding boxes

### Backend
- **Flask 3.0.0** - Lightweight Python web framework
- **Pillow** - Image processing

### Performance
- Runs at 10-15 FPS on Raspberry Pi 5
- ~3MB model download (cached after first load)
- Fullscreen optimized for portrait touchscreens

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

**Requirements**:
- JavaScript enabled
- HTTPS connection OR localhost
- User permission for camera access
- Internet connection (first load only, to download AI model)

## Using the T-Pose Capture

1. **Stand in front of the camera** - Position yourself in the frame
2. **Watch for green bounding box** - System tracks your body position
3. **Extend arms horizontally** - Make a T-pose with arms at shoulder height
4. **Box turns orange** - T-pose detected! Hold steady
5. **Progress bar fills** - Keep holding for 2 seconds
6. **Photo captured automatically** - No need to touch anything!

**Tips:**
- Keep wrists ~20px away from shoulders (doesn't need to be perfect)
- Arms should be roughly at shoulder height (±80px tolerance)
- Works in mirror mode - move naturally as you see yourself
- Manual capture button available if T-pose doesn't work

## Troubleshooting

### Camera Won't Start
1. Check browser permissions (camera icon in address bar)
2. Verify webcam is connected and recognized: `ls /dev/video*`
3. Check browser console (F12) for errors
4. Ensure internet connection for first-time AI model download

### T-Pose Not Detecting
1. Ensure good lighting for better pose detection
2. Stand 1-2 meters from camera for optimal detection
3. Extend arms horizontally at shoulder height
4. Keep arms extended outward (wrists away from body)
5. Use manual capture button if gesture doesn't work
6. Check browser console for detection errors

### Slow Performance
- Expected: 10-15 FPS on Raspberry Pi 5
- Close other browser tabs to free up resources
- Ensure webcam resolution isn't too high (640x480 recommended)
- AI model caches after first load (faster on subsequent uses)

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
- **Python**: Flask backend logic (`flask_app.py`)
- **HTML**: Page structure (`templates/`)
- **CSS**: Styling (modular, one file per page + shared, in `static/css/`)
- **JavaScript**: Camera control, AI detection, and interactivity (`static/js/`)

### Key Components

**camera.js**:
- MoveNet pose detection integration
- T-pose gesture recognition
- Real-time bounding box rendering
- Mirror mode canvas transformation
- Camera stream management

**camera.css**:
- Fullscreen portrait layout
- Mirrored video feed
- Overlay positioning for controls

To modify styles or behavior, edit the respective files in `static/css/` or `static/js/`.

### Customizing T-Pose Detection

Edit `camera.js` to adjust detection parameters:
```javascript
const POSE_HOLD_DURATION = 2000; // Hold time in milliseconds
const leftArmHorizontal = Math.abs(leftWrist.y - shoulderHeight) < 80; // Vertical tolerance
const leftArmExtended = Math.abs(leftWrist.x - leftShoulder.x) > 20; // Extension threshold
```

## License

[Your License Here]
