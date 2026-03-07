/**
 * ======================================
 * VOICE DOPPELGANGER - FRONTEND LOGIC
 * ======================================
 * This script handles:
 * - Recording user voice with microphone
 * - Uploading audio to backend
 * - Displaying cloned voice output
 * - Managing UI interactions
 */

// ======================================
// GLOBAL VARIABLES
// ======================================

let mediaRecorder;           // Object to record audio
let audioChunks = [];        // Array to store audio data
let recordedBlob;            // Blob object of recorded audio

// ======================================
// DOM ELEMENTS
// ======================================

// Buttons
const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const submitBtn = document.getElementById('submitBtn');
const playBtn = document.getElementById('playBtn');
const clonedPlayBtn = document.getElementById('clonedPlayBtn');

// Input Elements
const textInput = document.getElementById('textInput');
const charCount = document.getElementById('charCount');

// Audio Elements
const audioPlayback = document.getElementById('audioPlayback');
const clonedAudioPlayback = document.getElementById('clonedAudioPlayback');

// Display Elements
const recordingStatus = document.getElementById('recordingStatus');
const playbackSection = document.getElementById('playbackSection');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const clonedVoiceSection = document.getElementById('clonedVoiceSection');
const rateStatus = document.getElementById('rateStatus');

// ======================================
// EVENT LISTENERS
// ======================================

/**
 * Record Button - Start recording when clicked
 */
recordBtn.addEventListener('click', async () => {
    try {
        // Request access to user's microphone
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Create MediaRecorder object
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        // Start recording
        mediaRecorder.start();
        
        // Update UI
        recordBtn.disabled = true;
        stopBtn.disabled = false;
        recordingStatus.style.display = 'flex';
        playbackSection.style.display = 'none';
        errorMessage.style.display = 'none';
        
    } catch (error) {
        showError('Microphone access denied. Please allow microphone permissions.');
        console.error('Error accessing microphone:', error);
    }
});

/**
 * Stop Button - Stop recording when clicked
 */
stopBtn.addEventListener('click', () => {
    // Stop recording
    mediaRecorder.stop();
    
    // Stop all audio tracks (turns off microphone)
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
    
    // Collect audio data when recording stops
    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };
    
    // Process audio when recording finished
    mediaRecorder.onstop = () => {
        // Create blob from audio chunks
        recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });
        
        // Show playback section
        const audioUrl = URL.createObjectURL(recordedBlob);
        audioPlayback.src = audioUrl;
        playbackSection.style.display = 'block';
        
        // Enable submit button
        submitBtn.disabled = !(recordedBlob && textInput.value.trim());
    };
    
    // Update UI
    recordBtn.disabled = false;
    stopBtn.disabled = true;
    recordingStatus.style.display = 'none';
});

/**
 * Play Button - Play original recording
 */
playBtn.addEventListener('click', () => {
    audioPlayback.play();
});

/**
 * Cloned Play Button - Play cloned voice
 */
clonedPlayBtn.addEventListener('click', () => {
    clonedAudioPlayback.play();
});

/**
 * Text Input - Track character count and enable submit
 */
textInput.addEventListener('input', () => {
    // Update character counter display
    charCount.textContent = `${textInput.value.length}/500`;
    
    // Enable submit button if both recording and text exist
    submitBtn.disabled = !(recordedBlob && textInput.value.trim());
});

/**
 * Submit Button - Send recording and text to backend
 */
submitBtn.addEventListener('click', async () => {
    if (!recordedBlob || !textInput.value.trim()) {
        showError('Please record your voice and enter text');
        return;
    }
    
    await generateClonedVoice();
});

// ======================================
// MAIN FUNCTIONS
// ======================================

/**
 * Generate cloned voice by sending data to backend
 */
async function generateClonedVoice() {
    try {
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';
        submitBtn.disabled = true;
        
        // Create FormData object to send audio and text
        const formData = new FormData();
        formData.append('audio', recordedBlob, 'recording.webm');
        formData.append('text', textInput.value);
        
        // Send data to Flask backend at port 5000
        const response = await fetch('http://localhost:5000/api/clone-voice', {
            method: 'POST',
            body: formData
        });
        
        // Check if response is valid before parsing
        if (!response.ok) {
            // Try to get error message from response
            let errorMsg = 'Failed to generate cloned voice';
            try {
                const data = await response.json();
                errorMsg = data.error || errorMsg;
            } catch (e) {
                // If response isn't JSON, use status text
                errorMsg = response.statusText || errorMsg;
                if (response.status === 0) {
                    errorMsg = 'Cannot connect to backend server. Is Flask running on port 5000?';
                }
            }
            throw new Error(errorMsg);
        }
        
        // Parse successful response
        let data;
        try {
            data = await response.json();
        } catch (e) {
            throw new Error('Invalid response from server. Is Flask running on port 5000?');
        }
        
        // Show success message
        showSuccess('Voice cloned successfully!');
        
        // Display cloned audio in player
        const clonedAudioUrl = URL.createObjectURL(
            new Blob([new Uint8Array(atob(data.audio).split('').map(c => c.charCodeAt(0)))], 
            { type: 'audio/mpeg' })
        );
        clonedAudioPlayback.src = clonedAudioUrl;
        clonedVoiceSection.style.display = 'block';
        
        // Update rate limit status
        updateRateStatus(data.requests_remaining);
        
    } catch (error) {
        showError(error.message);
        console.error('Error:', error);
    } finally {
        // Hide loading indicator
        loadingIndicator.style.display = 'none';
        submitBtn.disabled = false;
    }
}

/**
 * Display error message to user
 * @param {string} message - Error message to display
 */
function showError(message) {
    errorMessage.textContent = '❌ ' + message;
    errorMessage.style.display = 'block';
    successMessage.style.display = 'none';
}

/**
 * Display success message to user
 * @param {string} message - Success message to display
 */
function showSuccess(message) {
    successMessage.textContent = '✅ ' + message;
    successMessage.style.display = 'block';
    errorMessage.style.display = 'none';
}

/**
 * Update rate limit display
 * @param {number} remaining - Requests remaining
 */
function updateRateStatus(remaining) {
    if (remaining !== undefined) {
        rateStatus.textContent = `Requests remaining: ${remaining}/5`;
        if (remaining <= 1) {
            rateStatus.style.color = '#dc2626';
        } else if (remaining <= 3) {
            rateStatus.style.color = '#f59e0b';
        }
    }
}

// ======================================
// INITIALIZATION
// ======================================

// Disable submit button on page load (until user records voice and enters text)
document.addEventListener('DOMContentLoaded', () => {
    submitBtn.disabled = true;
    console.log('Voice Doppelganger app loaded successfully!');
});
