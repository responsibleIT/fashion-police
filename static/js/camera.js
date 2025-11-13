// Camera page JavaScript
let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let preview = document.getElementById('preview');
let stream = null;
let capturedImage = null;

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
        video.onloadedmetadata = () => {
            video.play();
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
        
        showStatus('Camera ready! Position yourself and click Capture.', 'info');
        
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
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    let ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    capturedImage = canvas.toDataURL('image/jpeg', 0.9);
    
    preview.src = capturedImage;
    preview.style.display = 'block';
    video.style.display = 'none';
    
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
    startCamera();
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

async function checkDevices() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        
        let message = '📹 Video Devices Found:\n\n';
        
        if (videoDevices.length === 0) {
            message = '❌ No camera devices detected!\n\n';
            message += 'Troubleshooting steps:\n';
            message += '1. Check if USB webcam is plugged in\n';
            message += '2. Try a different USB port\n';
            message += '3. On Raspberry Pi, run: ls /dev/video*\n';
            message += '4. Check if camera works in other apps\n';
            message += '5. Try rebooting the Pi';
        } else {
            videoDevices.forEach((device, index) => {
                message += `${index + 1}. ${device.label || 'Camera ' + (index + 1)}\n`;
                message += `   ID: ${device.deviceId.substring(0, 20)}...\n\n`;
            });
        }
        
        message += '\nAll devices:\n';
        devices.forEach(device => {
            message += `- ${device.kind}: ${device.label || 'Unknown'}\n`;
        });
        
        alert(message);
        console.log('All devices:', devices);
    } catch (error) {
        alert('Error checking devices: ' + error.message);
        console.error('Device check error:', error);
    }
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
