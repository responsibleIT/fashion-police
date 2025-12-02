
# Fashion Police - Flask Camera App for Raspberry Pi

A Flask web application that runs on Raspberry Pi with on-device ML inference. Captures photos via webcam and performs real-time fashion style classification and clothing segmentation using FashionCLIP and SegFormer models.

## Features

✅ **On-Device ML Inference** - FashionCLIP style classification runs locally on Pi  
✅ **Clothing Segmentation** - SegFormer model identifies clothing regions  
✅ **AI-Powered Pose Detection** - T-pose gesture to capture photos hands-free  
✅ **Real-time Bounding Box** - MoveNet AI tracks person in camera feed  
✅ **Fullscreen Portrait Mode** - Optimized for vertical touchscreen displays  
✅ **Mirror Mode** - Camera feed flipped for intuitive positioning  
✅ **Clean UI** - Minimal, distraction-free interface  
✅ **Touch-Friendly** - Optimized for Raspberry Pi touchscreen displays  

## Quick Start

### 1. Create an virtual env
```bash
python -m venv env_name
```
### 2. Install Dependencies
```bash
pip install -r requirements-flask.txt
```

### 3. Run the Application
```bash
python flask_app.py
```

### 4. Access the App
- **On Raspberry Pi**: http://localhost:5000
- **From another device**: http://PI_IP_ADDRESS:5000

## Project Structure


```
fashion-police/
├── flask_app.py              # Main Flask application
├── requirements-flask.txt    # Python dependencies (includes PyTorch, Transformers)
├── data/                     # Data storage (gitignored)
│   ├── predictions.json      # JSON database (predictions + feedback)
│   └── images/               # Anonymized overlay images
├── src/
│   ├── database.py           # Database handler
│   ├── data/
│   │   └── styles.py         # Fashion style definitions (11 categories)
│   └── scripts/
│       ├── load_model.py     # SegFormer segmentation model
│       ├── style_predictor.py # FashionCLIP style classifier
│       └── classify_outfit.py # Combined inference pipeline
├── templates/
│   ├── camera.html           # Camera capture page
│   ├── results.html          # Results display page
│   ├── feedback.html         # User feedback page
│   └── stats.html            # Statistics dashboard
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
- Shows clothing segmentation overlay (colored regions with black face, white background)
- Displays style predictions ranked by confidence
- 11 fashion categories: Urban Streetwear, Formal Business, Casual Chic, etc.
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
- **Flask 3.0.0** - Python web framework
- **PyTorch 2.9+** - Deep learning framework (CPU-only)
- **Transformers** - Hugging Face models library
- **FashionCLIP** - Fashion-specific CLIP model for style classification
- **SegFormer** - Semantic segmentation model for clothing regions
- **Pillow** - Image processing

### Performance
- **Camera**: 10-15 FPS pose detection on Raspberry Pi 5
- **ML Inference**: 3-5 seconds per image (CPU-only on Pi 5)
- **Model Downloads**: ~500MB total (FashionCLIP + SegFormer, cached after first load)
- **Models load at startup** to avoid delays during photo capture
- Fullscreen optimized for portrait touchscreens

## Hardware Requirements

- **Raspberry Pi 5** (or compatible)
- **USB Webcam**
- **Touchscreen Display** (optional but recommended)
- **Docking Station** (if using touchscreen + webcam simultaneously)

### Power Considerations

⚠️ **Important**: USB touchscreens draw significant power. If your webcam shuts down when the touchscreen is connected, use a powered docking station to connect both peripherals.

## Machine Learning Models

### Fashion Style Classification
Uses **FashionCLIP** (patrickjohncyh/fashion-clip), a CLIP model fine-tuned for fashion:
- Zero-shot classification using text-image similarity
- 11 predefined style categories with text descriptions
- Returns ranked predictions with confidence scores
- Runs on CPU (no CUDA required)

### Clothing Segmentation
Uses **SegFormer** (mattmdjaga/segformer_b2_clothes) for semantic segmentation:
- 18 clothing/body part classes (hat, upper-clothes, pants, face, etc.)
- Generates colored overlay visualization
- White background, black face for privacy
- Helps isolate clothing regions from background

### Style Categories
1. Urban Streetwear
2. Formal Business
3. Casual Chic
4. Sporty / Athleisure
5. Vintage / Retro
6. Bohemian
7. Elegant Evening
8. Preppy
9. Punk / Alt
10. Gothic
11. Artsy / Expressive

## Application Routes

- `GET /` - Camera capture page
- `POST /process_image` - Process captured image with on-device ML inference
- `GET /results` - Display results page with segmentation overlay and predictions
- `GET /feedback` - Feedback collection page
- `POST /submit_feedback` - Submit user feedback
- `GET /stats` - View statistics dashboard (predictions, feedback, trends)

## Data Storage & Privacy

The application stores data locally on the Raspberry Pi for model improvement:

### What Gets Stored
- **Anonymized images only**: Segmentation overlay images (with black face, white background)
- **Predictions**: Model's style classifications with confidence scores
- **User feedback**: Corrections when users indicate the model was wrong
- **Metadata**: Timestamps, record IDs

### What Does NOT Get Stored
- ❌ Original photos (discarded after processing)
- ❌ Identifiable faces (replaced with solid black in overlay)
- ❌ Any personal information

### Storage Location
- **Database**: `data/predictions.json` (JSON file)
- **Images**: `data/images/` (anonymized overlays only)
- **Note**: The `data/` directory is gitignored and never committed

### Viewing Statistics
Access the statistics dashboard at `http://PI_IP:5000/stats` to see:
- Total predictions made
- User feedback rate
- Most common style predictions
- User correction patterns

### Managing Data
To clear all stored data:
```bash
rm -rf data/
```

The database and image directory will be recreated on next run.

## Browser Compatibility

Works best with:
- Chrome/Chromium (recommended for Pi)
- Firefox
- Safari (iOS)

**Requirements**:
- JavaScript enabled
- HTTPS connection OR localhost
- User permission for camera access
- Internet connection (first run only, to download ML models ~500MB)
- Python 3.11+ or 3.13 recommended for best compatibility

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
- **Camera**: Expected 10-15 FPS on Raspberry Pi 5
- **ML Inference**: Expected 3-5 seconds per photo (CPU-only)
- Models load at startup (may take 10-20 seconds on first launch)
- Close other applications to free up RAM (models use ~2GB)
- Ensure webcam resolution isn't too high (640x480 recommended)
- AI models cache after first download (faster on subsequent runs)

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
