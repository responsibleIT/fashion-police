// Camera page JavaScript

let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let preview = document.getElementById('preview');
let stream = null;
let capturedImage = null;
let boundingBoxActive = true;
let detector = null;
let detectionActive = false;
let poseHoldStartTime = null;
let poseDetectedForCapture = false;
const POSE_HOLD_DURATION = 2000; // Hold pose for 2 seconds to capture

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
    poseHoldStartTime = null; // Reset pose timer
    poseDetectedForCapture = false;
    
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
    poseHoldStartTime = null; // Reset pose timer
    poseDetectedForCapture = false;
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

    // Flip the canvas context to match the mirrored video
    ctx.save();
    ctx.scale(-1, 1);
    ctx.translate(-canvas.width, 0);

    // Run pose detection
    try {
        const poses = await detector.estimatePoses(video);
        if (poses && poses.length > 0) {
            const pose = poses[0];
            
            // Get bounding box from keypoints
            const keypoints = pose.keypoints.filter(kp => kp.score > 0.3);
            if (keypoints.length > 0) {
                let minX = Math.min(...keypoints.map(kp => kp.x));
                let minY = Math.min(...keypoints.map(kp => kp.y));
                let maxX = Math.max(...keypoints.map(kp => kp.x));
                let maxY = Math.max(...keypoints.map(kp => kp.y));

                // Add padding above head (eyes are the highest keypoint, not top of head)
                const headPadding = (maxY - minY) * 0.25; // 15% of body height
                minY = Math.max(0, minY - headPadding);
                
                // Add some side and bottom padding for better framing
                const sidePadding = (maxX - minX) * 0.1; // 10% of width
                const bottomPadding = (maxY - minY) * 0.05; // 5% of height
                minX = Math.max(0, minX - sidePadding);
                maxX = Math.min(canvas.width, maxX + sidePadding);
                maxY = Math.min(canvas.height, maxY + bottomPadding);

                // Check if T-pose is detected
                const isPoseTrigger = checkCapturePose(pose);
                
                if (isPoseTrigger) {
                    if (!poseHoldStartTime) {
                        poseHoldStartTime = Date.now();
                        poseDetectedForCapture = true;
                    }
                    
                    const holdTime = Date.now() - poseHoldStartTime;
                    const progress = Math.min(holdTime / POSE_HOLD_DURATION, 1.0);
                    
                    // Draw bounding box in yellow/orange when pose detected
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = progress < 1.0 ? '#00FF00' : '#fffb00';
                    ctx.setLineDash([2, 6]);
                    ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);
                    ctx.setLineDash([]);
                    
                    // Draw progress bar
                    const barWidth = 200;
                    const barHeight = 20;
                    const barX = (canvas.width - barWidth) / 2;
                    const barY = 60;
                    
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
                    ctx.fillRect(barX, barY, barWidth, barHeight);
                    
                    ctx.fillStyle = '#fffb00';
                    ctx.fillRect(barX, barY, barWidth * progress, barHeight);
                    
                    ctx.strokeStyle = '#FFFFFF';
                    ctx.lineWidth = 2;
                    ctx.strokeRect(barX, barY, barWidth, barHeight);

                    // Trigger capture when pose held long enough
                    if (holdTime >= POSE_HOLD_DURATION && poseDetectedForCapture) {
                        poseDetectedForCapture = false;
                        poseHoldStartTime = null;
                        capturePhoto();
                        return; // Exit loop as photo is captured
                    }
                } else {
                    // Reset timer if pose is broken
                    poseHoldStartTime = null;
                    poseDetectedForCapture = false;
                    
                    // Draw normal green bounding box
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = '#fffb00';
                    ctx.setLineDash([2, 6]);
                    ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);
                    ctx.setLineDash([]);
                }
            }
        }
    } catch (err) {
        console.error('Detection error:', err);
    }
    
    ctx.restore(); // Restore canvas context after flipping
    requestAnimationFrame(drawDetectionLoop);
}

// Check if user is in the capture pose (hand at eye level)
function checkCapturePose(pose) {
    const keypoints = pose.keypoints;
    
    // Get relevant keypoints
    const leftEye = keypoints.find(kp => kp.name === 'left_eye');
    const rightEye = keypoints.find(kp => kp.name === 'right_eye');
    const nose = keypoints.find(kp => kp.name === 'nose');
    const leftWrist = keypoints.find(kp => kp.name === 'left_wrist');
    const rightWrist = keypoints.find(kp => kp.name === 'right_wrist');
    
    // Check if keypoints are detected with good confidence
    if (!leftWrist || !rightWrist) return false;
    if (leftWrist.score < 0.3 || rightWrist.score < 0.3) return false;
    
    // Calculate eye level (use average of both eyes if available, otherwise use nose as reference)
    let eyeLevel;
    if (leftEye && rightEye && leftEye.score > 0.3 && rightEye.score > 0.3) {
        eyeLevel = (leftEye.y + rightEye.y) / 2;
    } else if (nose && nose.score > 0.3) {
        eyeLevel = nose.y - 20; // Eyes are typically slightly above nose
    } else {
        return false;
    }
    
    // Create a tolerance band around eye level (±60 pixels above, 100 pixels below)
    const toleranceAbove = 60;
    const toleranceBelow = 100;
    const eyeLevelTop = eyeLevel - toleranceAbove;
    const eyeLevelBottom = eyeLevel + toleranceBelow;
    
    // Check if left wrist is at eye level
    const leftWristAtEyeLevel = 
        leftWrist.y >= eyeLevelTop && 
        leftWrist.y <= eyeLevelBottom;
    
    // Check if right wrist is at eye level
    const rightWristAtEyeLevel = 
        rightWrist.y >= eyeLevelTop && 
        rightWrist.y <= eyeLevelBottom;
    
    // Trigger if either hand is at eye level
    return leftWristAtEyeLevel || rightWristAtEyeLevel;
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
