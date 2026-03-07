/**
 * ======================================
 * AI VOICE DOPPELGANGER - FRONTEND
 * ======================================
 * Modern SaaS UI with full voice cloning
 */

// Global Variables
let mediaRecorder;
let audioChunks = [];
let recordedBlob;

// DOM Elements
const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const submitBtn = document.getElementById('submitBtn');
const textInput = document.getElementById('textInput');
const charCount = document.getElementById('charCount');
const audioPlayback = document.getElementById('audioPlayback');
const clonedAudioPlayback = document.getElementById('clonedAudioPlayback');
const recordingStatus = document.getElementById('recordingStatus');
const playbackSection = document.getElementById('playbackSection');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const clonedVoiceSection = document.getElementById('clonedVoiceSection');
const emptyState = document.getElementById('emptyState');
const downloadBtn = document.getElementById('downloadBtn');

// ======================================
// RECORDING FUNCTIONALITY
// ======================================

recordBtn.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.start();
        
        recordBtn.disabled = true;
        stopBtn.disabled = false;
        recordingStatus.style.display = 'flex';
        playbackSection.style.display = 'none';
        errorMessage.style.display = 'none';
        
    } catch (error) {
        showError('Microphone access denied. Please allow microphone permissions.');
    }
});

stopBtn.addEventListener('click', () => {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
    
    mediaRecorder.onstop = () => {
        recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(recordedBlob);
        audioPlayback.src = audioUrl;
        playbackSection.style.display = 'block';
        updateSubmitButton();
    };
    
    recordBtn.disabled = false;
    stopBtn.disabled = true;
    recordingStatus.style.display = 'none';
});

// ======================================
// TEXT INPUT HANDLING
// ======================================

textInput.addEventListener('input', () => {
    charCount.textContent = `${textInput.value.length}/500`;
    updateSubmitButton();
});

// ======================================
// SUBMIT & GENERATION
// ======================================

submitBtn.addEventListener('click', async () => {
    if (!recordedBlob || !textInput.value.trim()) {
        showError('Please record your voice and enter text');
        return;
    }
    
    await generateClonedVoice();
});

async function generateClonedVoice() {
    try {
        loadingIndicator.style.display = 'flex';
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';
        submitBtn.disabled = true;
        
        const formData = new FormData();
        formData.append('audio', recordedBlob, 'recording.webm');
        formData.append('text', textInput.value);
        
        const response = await fetch('http://127.0.0.1:5000/api/clone-voice', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            let errorMsg = 'Failed to generate cloned voice';
            try {
                const data = await response.json();
                errorMsg = data.error || errorMsg;
            } catch (e) {
                errorMsg = response.statusText || errorMsg;
            }
            throw new Error(errorMsg);
        }
        
        const data = await response.json();
        
        // Display cloned audio
        const clonedAudioUrl = URL.createObjectURL(
            new Blob([new Uint8Array(atob(data.audio).split('').map(c => c.charCodeAt(0)))], 
            { type: 'audio/mpeg' })
        );
        clonedAudioPlayback.src = clonedAudioUrl;
        
        emptyState.style.display = 'none';
        clonedVoiceSection.style.display = 'block';
        
        showSuccess('Voice cloned successfully!');
        
        // Set up download button
        if (downloadBtn) {
            downloadBtn.onclick = () => downloadAudio(data.cloned_file, clonedAudioUrl);
        }
        
    } catch (error) {
        showError(error.message);
        console.error('Error:', error);
    } finally {
        loadingIndicator.style.display = 'none';
        submitBtn.disabled = false;
    }
}

// ======================================
// UI UTILITIES
// ======================================

function updateSubmitButton() {
    submitBtn.disabled = !(recordedBlob && textInput.value.trim());
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'flex';
    successMessage.style.display = 'none';
}

function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = 'flex';
    errorMessage.style.display = 'none';
}

function downloadAudio(filename, audioUrl) {
    const link = document.createElement('a');
    link.href = audioUrl;
    link.download = filename || 'cloned-voice.mp3';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ======================================
// INITIALIZATION
// ======================================

document.addEventListener('DOMContentLoaded', () => {
    updateSubmitButton();
    console.log('🎤 AI Voice Doppelganger loaded successfully!');
});
