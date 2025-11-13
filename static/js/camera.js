// Camera page JavaScript

let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let preview = document.getElementById('preview');
let stream = null;
let capturedImage = null;
let boundingBoxActive = true;
let detector = null;
let detectionActive = false;

async function startCamera() {
    try {
        // Stop existing stream if any
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        // First, enumerate devices to see what's available
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        
        console.log('Available video devices:', videoDevices);
        
        if (videoDevices.length === 0) {
            throw new Error('No camera devices found. Please check if your USB webcam is connected.');
        }

        // Try multiple constraint options
        let constraints;
        
        // Try option 1: Simple constraints (most compatible)
        try {
            constraints = { 
                video: true,
                audio: false
            };
            
            console.log('Trying simple constraints...');
            stream = await navigator.mediaDevices.getUserMedia(constraints);
            console.log('Success with simple constraints!');
        } catch (e1) {
            console.log('Simple constraints failed:', e1);
            
            // Try option 2: Specific device
            try {
                constraints = {
                    video: {
                        deviceId: videoDevices[0].deviceId
                    },
                    audio: false
                };
                
                console.log('Trying specific device:', videoDevices[0].label);
                stream = await navigator.mediaDevices.getUserMedia(constraints);
                console.log('Success with specific device!');
            } catch (e2) {
                console.log('Specific device failed:', e2);
                
                // Try option 3: Basic video only
                constraints = {
                    video: {
                        width: 640,
                        height: 480
                    },
                    audio: false
                };
                
                console.log('Trying basic resolution...');
                stream = await navigator.mediaDevices.getUserMedia(constraints);
                console.log('Success with basic resolution!');
            }
        }
        
        // Set video source and wait for it to load

        video.srcObject = stream;

        // Make sure video plays and stays playing
        video.onloadedmetadata = async () => {
            video.play();
            boundingBoxActive = true;
            await loadMoveNet();
            detectionActive = true;
            drawDetectionLoop();
        };

        // Keep video playing (prevents auto-pause)
        video.setAttribute('autoplay', '');
        video.setAttribute('playsinline', '');

        video.style.display = 'block';
        preview.style.display = 'none';

        document.getElementById('start-camera').style.display = 'none';
        document.getElementById('capture').style.display = 'inline-block';
        document.getElementById('retake').style.display = 'none';
        document.getElementById('analyze').style.display = 'none';

        showStatus('Camera ready! Position yourself inside the box and click Capture.', 'info');

        console.log('Camera started successfully');
    } catch (error) {
        console.error('Camera error:', error);
        
        let errorMsg = 'Error accessing camera: ' + error.message;
        
        // Provide helpful troubleshooting
        if (error.name === 'NotFoundError' || error.message.includes('not be found')) {
            errorMsg += '\n\n❌ Camera not found!\n\nTroubleshooting:\n' +
                      '1. Is your USB webcam plugged in?\n' +
                      '2. Try unplugging and replugging the camera\n' +
                      '3. Check if another app is using the camera\n' +
                      '4. On Pi: Check with "ls /dev/video*"\n' +
                      '5. Try a different USB port';
        } else if (error.name === 'NotAllowedError') {
            errorMsg += '\n\n❌ Camera permission denied!\n\n' +
                      'Click the camera icon in your browser\'s address bar and allow access.';
        } else if (error.name === 'NotReadableError') {
            errorMsg += '\n\n❌ Camera is busy!\n\n' +
                      'Another application might be using the camera. Close other apps and try again.';
        }
        
        alert(errorMsg);
    }
}




function capturePhoto() {
    boundingBoxActive = false;
    detectionActive = false;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    let ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    capturedImage = canvas.toDataURL('image/jpeg', 0.9);

    preview.src = capturedImage;
    preview.style.display = 'block';
    video.style.display = 'none';
    canvas.style.display = 'none'; // Hide canvas overlay

    // Stop camera
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }

    document.getElementById('capture').style.display = 'none';
    document.getElementById('retake').style.display = 'inline-block';
    document.getElementById('analyze').style.display = 'inline-block';

    showStatus('Photo captured! Click "Analyze Style" to continue.', 'info');
}



function retakePhoto() {
    capturedImage = null;
    preview.style.display = 'none';
    video.style.display = 'block';
    canvas.style.display = 'block'; // Show canvas overlay again
    startCamera();
}


// Load MoveNet model
async function loadMoveNet() {
    if (!window.poseDetection) {
        showStatus('MoveNet model not loaded. Check your internet connection.', 'error');
        return;
    }
    detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, {
        modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING,
        enableSmoothing: true
    });
}

// Run detection and draw bounding box around person
async function drawDetectionLoop() {
    if (!detectionActive || !detector || video.videoWidth === 0 || video.videoHeight === 0) {
        requestAnimationFrame(drawDetectionLoop);
        return;
    }
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    let ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Run pose detection
    try {
        const poses = await detector.estimatePoses(video);
        if (poses && poses.length > 0) {
            // Get bounding box from keypoints
            const keypoints = poses[0].keypoints.filter(kp => kp.score > 0.3);
            if (keypoints.length > 0) {
                let minX = Math.min(...keypoints.map(kp => kp.x));
                let minY = Math.min(...keypoints.map(kp => kp.y));
                let maxX = Math.max(...keypoints.map(kp => kp.x));
                let maxY = Math.max(...keypoints.map(kp => kp.y));

                ctx.lineWidth = 4;
                ctx.strokeStyle = '#00FF00';
                ctx.setLineDash([12, 8]);
                ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);
                ctx.setLineDash([]);

                ctx.font = '24px Arial';
                ctx.fillStyle = '#00FF00';
                ctx.textAlign = 'center';
                ctx.fillText('Stand inside the box', (minX + maxX) / 2, minY - 12);
            }
        }
    } catch (err) {
        console.error('Detection error:', err);
    }
    requestAnimationFrame(drawDetectionLoop);
}

async function analyzePhoto() {
    if (!capturedImage) {
        alert('Please capture a photo first');
        return;
    }

    showStatus('Processing your style...', 'processing', true);
    
    document.getElementById('retake').disabled = true;
    document.getElementById('analyze').disabled = true;

    try {
        const response = await fetch('/process_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: capturedImage })
        });

        if (response.ok) {
            window.location.href = '/results';
        } else {
            throw new Error('Failed to process image');
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('retake').disabled = false;
        document.getElementById('analyze').disabled = false;
        hideStatus();
    }
}

function showStatus(message, type, showSpinner = false) {
    const status = document.getElementById('status');
    status.innerHTML = showSpinner ? '<div class="spinner"></div>' + message : message;
    status.className = 'status-' + type;
    status.style.display = 'block';
}

function hideStatus() {
    document.getElementById('status').style.display = 'none';
}

// Prevent video from pausing
video.addEventListener('pause', (e) => {
    if (stream && video.srcObject) {
        console.log('Video paused, restarting...');
        video.play();
    }
});

// Monitor stream health
setInterval(() => {
    if (stream && video.srcObject && video.style.display === 'block') {
        const tracks = stream.getVideoTracks();
        if (tracks.length > 0 && tracks[0].readyState === 'live') {
            // Stream is healthy
            if (video.paused) {
                console.log('Video paused unexpectedly, resuming...');
                video.play();
            }
        } else {
            console.error('Stream died, restarting camera...');
            startCamera();
        }
    }
}, 1000); // Check every second

// Auto-start camera on page load
window.addEventListener('load', () => {
    setTimeout(startCamera, 500); // Small delay for reliability
});

// Prevent page from going to sleep
if ('wakeLock' in navigator) {
    let wakeLock = null;
    async function requestWakeLock() {
        try {
            wakeLock = await navigator.wakeLock.request('screen');
            console.log('Wake lock acquired');
        } catch (err) {
            console.log('Wake lock error:', err);
        }
    }
    requestWakeLock();
}
