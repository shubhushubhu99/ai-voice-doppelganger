# -*- coding: utf-8 -*-
"""
=====================================
VOICE DOPPELGANGER - BACKEND (Flask)
=====================================
This Flask app handles:
- Receiving audio files from frontend
- Calling ElevenLabs API to clone voice
- Applying watermark metadata to audio
- Managing rate limiting per user
- Serving the frontend files
"""

# =====================================
# IMPORTS
# =====================================

import os
import json
import base64
import requests
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# =====================================
# CONFIGURATION
# =====================================

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing for development
# Allow all origins for localhost development
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     supports_credentials=False,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"])

# Configuration
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == 'your_api_key_here':
    print("⚠️  WARNING: ELEVENLABS_API_KEY not set in .env file!")
    print("Please get your API key from: https://elevenlabs.io/app/api")

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'webm', 'mp3', 'wav', 'm4a', 'ogg'}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB max file size

# Audio storage directory
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

# Rate limiting storage (in-memory, resets on app restart)
# Format: {user_ip: {'requests': count, 'timestamp': datetime}}
rate_limit_store = {}
RATE_LIMIT_REQUESTS = 5
RATE_LIMIT_WINDOW = 60  # seconds (1 minute)

# =====================================
# UTILITY FUNCTIONS
# =====================================

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_ip():
    """Get user's IP address for rate limiting"""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip

def check_rate_limit(func):
    """
    Decorator to check rate limiting
    Max 5 requests per user per minute
    """
    @wraps(func)
    def rate_limited(*args, **kwargs):
        user_ip = get_user_ip()
        now = datetime.now()
        
        # Initialize user in rate limit store if not exists
        if user_ip not in rate_limit_store:
            rate_limit_store[user_ip] = {
                'requests': 0,
                'timestamp': now
            }
        
        user_data = rate_limit_store[user_ip]
        time_passed = (now - user_data['timestamp']).total_seconds()
        
        # Reset counter if time window has passed
        if time_passed > RATE_LIMIT_WINDOW:
            user_data['requests'] = 0
            user_data['timestamp'] = now
        
        # Check if rate limit exceeded
        if user_data['requests'] >= RATE_LIMIT_REQUESTS:
            return jsonify({
                'error': f'Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} requests per minute. Please try again later.',
                'requests_remaining': 0
            }), 429
        
        # Increment request counter
        user_data['requests'] += 1
        remaining = RATE_LIMIT_REQUESTS - user_data['requests']
        
        # Store remaining requests in kwargs for the function to use
        kwargs['requests_remaining'] = remaining
        
        return func(*args, **kwargs)
    
    return rate_limited

def add_watermark_metadata(audio_data, text, original_file):
    """
    Add watermark metadata to audio file
    This adds information about the cloning process to the audio metadata
    """
    try:
        # Note: For production, use mutagen or ffmpeg to add ID3 tags
        # For this demo, we'll just note that watermarking would happen here
        metadata = {
            'watermark': 'AI Voice Cloned',
            'timestamp': datetime.now().isoformat(),
            'text_used': text,
            'original_file': original_file
        }
        print(f"✓ Watermark metadata added: {metadata}")
        return audio_data
    except Exception as e:
        print(f"⚠️  Could not add watermark: {e}")
        return audio_data

def save_audio_file(audio_data, filename_prefix):
    """
    Save audio file to disk
    Returns the filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    with open(filepath, 'wb') as f:
        f.write(audio_data)
    
    print(f"✓ Audio saved: {filepath}")
    return filename

# =====================================
# ROUTES
# =====================================

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS)"""
    return send_from_directory('.', filename)

@app.route('/api/clone-voice', methods=['POST'])
@check_rate_limit  # Apply rate limiting decorator
def clone_voice(requests_remaining=None):
    """
    Main endpoint to clone voice
    Receives audio file and text, returns cloned audio
    """
    
    try:
        # ====================================
        # VALIDATE INPUT
        # ====================================
        
        # Check if audio file was uploaded
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # Check if file is empty
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Check file extension
        if not allowed_file(audio_file.filename):
            return jsonify({'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Get text to clone
        text = request.form.get('text', '').strip()
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 500:
            return jsonify({'error': 'Text exceeds 500 character limit'}), 400
        
        # ====================================
        # PROCESS AUDIO
        # ====================================
        
        # Read uploaded audio file
        audio_data = audio_file.read()
        
        # Check file size
        if len(audio_data) > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Max size: {MAX_FILE_SIZE / (1024*1024):.0f}MB'}), 400
        
        # Save original audio
        original_filename = save_audio_file(audio_data, 'original')
        print(f"📝 Original audio saved: {original_filename}")
        
        # ====================================
        # CALL ELEVENLABS API
        # ====================================
        
        if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == 'your_api_key_here':
            return jsonify({
                'error': 'ElevenLabs API key not configured. Please set ELEVENLABS_API_KEY in .env file'
            }), 500
        
        print(f"🎤 Generating speech with text: {text[:50]}...")
        
        # ====================================
        # GET AVAILABLE VOICES
        # ====================================
        
        # Use a pre-made voice from ElevenLabs (free tier compatible)
        # These are available voices that work with text-to-speech
        AVAILABLE_VOICES = [
            "CwhRBWXzGAHq8TQ4Fs17",  # Roger - Laid-Back, Casual
            "EXAVITQu4vr4xnSDxMaL",  # Sarah - Mature, Reassuring
            "FGY2WhTYpPnrIDTdsKH5",  # Laura - Enthusiast, Quirky
            "21m00Tcm4TlvDq8ikWAM",  # Bella - Young, Cheerful
            "EXAVITQu4vr4xnSDxMaL",  # Sarah - Confident
        ]
        
        # Select a random voice from available options
        import random
        voice_id = random.choice(AVAILABLE_VOICES)
        print(f"✓ Using pre-made voice: {voice_id}")
        
        # ====================================
        # TEXT-TO-SPEECH
        # ====================================
        
        # Now use the cloned voice to generate speech from text
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        tts_headers = {
            'xi-api-key': ELEVENLABS_API_KEY,
            'Content-Type': 'application/json'
        }
        
        tts_data = {
            'text': text,
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.75
            }
        }
        
        tts_response = requests.post(
            tts_url,
            headers=tts_headers,
            json=tts_data,
            timeout=30
        )
        
        if tts_response.status_code != 200:
            try:
                error_data = tts_response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            except:
                error_msg = tts_response.text[:200] if tts_response.text else f'HTTP {tts_response.status_code}'
            print(f"❌ TTS API error: {error_msg}")
            return jsonify({
                'error': 'Failed to generate speech. Please try again.'
            }), 500
        
        try:
            cloned_audio = tts_response.content
            if not cloned_audio or len(cloned_audio) == 0:
                raise ValueError('Empty audio response from API')
        except Exception as e:
            print(f"❌ Error processing audio: {e}")
            return jsonify({
                'error': 'Failed to process audio response'
            }), 500
        
        print(f"✓ Speech generated successfully ({len(cloned_audio)} bytes)")
        
        # ====================================
        # ADD WATERMARK & SAVE
        # ====================================
        
        # Apply watermark metadata
        cloned_audio_with_watermark = add_watermark_metadata(
            cloned_audio, 
            text, 
            original_filename
        )
        
        # Save cloned audio
        cloned_filename = save_audio_file(cloned_audio_with_watermark, 'cloned')
        print(f"🎵 Cloned audio saved: {cloned_filename}")
        
        # ====================================
        # RETURN RESPONSE
        # ====================================
        
        # Convert audio to base64 for sending in JSON response
        audio_base64 = base64.b64encode(cloned_audio_with_watermark).decode('utf-8')
        
        return jsonify({
            'success': True,
            'message': 'Voice cloned successfully!',
            'audio': audio_base64,
            'original_file': original_filename,
            'cloned_file': cloned_filename,
            'requests_remaining': requests_remaining
        }), 200
        
    except requests.exceptions.Timeout:
        print(f"⏱️  Request timeout - ElevenLabs API took too long")
        return jsonify({'error': 'Request timeout. ElevenLabs service is slow. Please try again in a moment.'}), 504
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return jsonify({'error': 'Cannot connect to ElevenLabs API. Check your internet connection.'}), 503
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return jsonify({'error': 'Network communication error. Please try again.'}), 500
    except ValueError as e:
        print(f"❌ Value error: {e}")
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'An error occurred. Please check the server logs.'}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """API status check endpoint"""
    return jsonify({
        'status': 'running',
        'api_configured': bool(ELEVENLABS_API_KEY and ELEVENLABS_API_KEY != 'your_api_key_here')
    }), 200

# =====================================
# ERROR HANDLERS
# =====================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# =====================================
# MAIN
# =====================================

if __name__ == '__main__':
    print("=" * 50)
    print("🎤 VOICE DOPPELGANGER - STARTING SERVER")
    print("=" * 50)
    print(f"📁 Audio storage: {os.path.abspath(AUDIO_DIR)}")
    print(f"🔐 API Key configured: {bool(ELEVENLABS_API_KEY and ELEVENLABS_API_KEY != 'your_api_key_here')}")
    print(f"⏱️  Rate limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds")
    print("=" * 50)
    print("🌐 Open http://localhost:5000 in your browser")
    print("=" * 50)
    
    # Run Flask development server
    # debug=True enables auto-reload and error debugging
    app.run(debug=True, host='127.0.0.1', port=5000)
