# 📋 Architecture & Usage Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Browser)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ index.html                                           │   │
│  │ - Mic recording button                               │   │
│  │ - Audio playback controls                            │   │
│  │ - Text input box                                     │   │
│  │ - Status indicators                                  │   │
│  └──────────────┬────────────────────────────────────────┘   │
│                 │                                             │
│  ┌──────────────▼────────────────────────────────────────┐   │
│  │ script.js (JavaScript)                              │   │
│  │ - MediaRecorder API (record audio)                   │   │
│  │ - Fetch API (upload to backend)                      │   │
│  │ - UI interactions                                    │   │
│  └──────────────┬────────────────────────────────────────┘   │
│                 │                                             │
│  style.css      │                                             │
│  - Responsive   │                                             │
│  - Modern UI    │                                             │
│                 │                                             │
└─────────────────┼─────────────────────────────────────────────┘
                  │
                  │ HTTP POST /api/clone-voice
                  │ (FormData: audio + text)
                  │
┌─────────────────▼─────────────────────────────────────────────┐
│                   BACKEND (Flask Server)                       │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ app.py                                               │    │
│  │ ┌────────────────────────────────────────────────┐   │    │
│  │ │ 1. Validate Input                              │   │    │
│  │ │    - Check file format                         │   │    │
│  │ │    - Check text length                         │   │    │
│  │ └────────────────────────────────────────────────┘   │    │
│  │ ┌────────────────────────────────────────────────┐   │    │
│  │ │ 2. Rate Limiting                               │   │    │
│  │ │    - Max 5 requests per 60 seconds             │   │    │
│  │ │    - Track by IP address                       │   │    │
│  │ └────────────────────────────────────────────────┘   │    │
│  │ ┌────────────────────────────────────────────────┐   │    │
│  │ │ 3. Save Original Audio                         │   │    │
│  │ │    - Store in audio/ directory                 │   │    │
│  │ │    - Timestamp in filename                     │   │    │
│  │ └────────────────────────────────────────────────┘   │    │
│  └──────────────────────────────────────────────────────┘    │
│                         │                                     │
└─────────────────────────┼─────────────────────────────────────┘
                          │
                          │ API Call
                          ▼
┌──────────────────────────────────────────────────────────────┐
│             ELEVENLABS API (Cloud)                           │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ 1. Voice Clone Endpoint                               │   │
│  │    POST /v1/voice_clone                              │   │
│  │    - Receives audio sample                            │   │
│  │    - Returns voice_id                                 │   │
│  └───────────────────────────────────────────────────────┘   │
│                         │                                     │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ 2. Text-to-Speech Endpoint                            │   │
│  │    POST /v1/text-to-speech/{voice_id}               │   │
│  │    - Receives text and voice settings                 │   │
│  │    - Returns MP3 audio                                │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                          │
                          │ MP3 Audio
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                   BACKEND (Flask Server)                      │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ 4. Add Watermark Metadata                             │   │
│  │    - Timestamp                                        │   │
│  │    - Text used                                        │   │
│  │    - Original file reference                          │   │
│  └───────────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ 5. Save Cloned Audio                                  │   │
│  │    - Store in audio/ directory                        │   │
│  │    - Timestamp in filename                            │   │
│  └───────────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ 6. Return Response                                    │   │
│  │    - Base64 encoded audio                             │   │
│  │    - Filenames                                        │   │
│  │    - Rate limit info                                  │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                          │
                          │ JSON Response
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                     FRONTEND (Browser)                        │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ Display Cloned Voice                                  │   │
│  │ - Show success message                                │   │
│  │ - Display audio player                                │   │
│  │ - Allow playback                                      │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow Sequence Diagram

```
User                Frontend               Backend                ElevenLabs API
  │                   │                      │                         │
  ├─Click Record─────►│                      │                         │
  │                   ├─Start Recording─►    │                         │
  │                   │◄─Audio Stream────    │                         │
  │                   │                      │                         │
  ├─Stop Recording───►│                      │                         │
  │                   ├─Submit Form──────────►│                         │
  │                   │  (audio + text)      ├─Validate Input          │
  │                   │                      ├─Check Rate Limit        │
  │                   │                      ├─Save Original Audio     │
  │                   │                      │                         │
  │                   │                      ├─POST /voice_clone──────►│
  │                   │                      │◄─voice_id───────────────┤
  │                   │                      │                         │
  │                   │                      ├─POST /text-to-speech───►│
  │                   │                      │◄─MP3 Audio──────────────┤
  │                   │                      │                         │
  │                   │                      ├─Add Watermark          │
  │                   │                      ├─Save Cloned Audio      │
  │                   │◄─JSON Response───────┤                         │
  │                   │  (audio base64)      │                         │
  │                   ├─Display Player──┐ │                         │
  │                   │ Decode Audio    │ │                         │
  │Play Cloned Voice──┤ Playback────────┘ │                         │
  │                   │                      │                         │
```

## File Descriptions

### Frontend Files

#### `index.html` (287 lines)
**Purpose**: Main UI structure
**Key Features**:
- Semantic HTML5 structure
- Four main sections: Record, Enter Text, Generate, Playback
- Audio player elements
- Status and error message containers
- Accessibility labels

**Main Elements**:
```html
<button id="recordBtn">        <!-- Start recording -->
<button id="stopBtn">          <!-- Stop recording -->
<textarea id="textInput">      <!-- Text input -->
<button id="submitBtn">        <!-- Submit button -->
<audio id="audioPlayback">     <!-- Original audio player -->
<audio id="clonedAudioPlayback"> <!-- Cloned audio player -->
```

#### `style.css` (340 lines)
**Purpose**: UI styling and responsive design
**Key Features**:
- CSS variables for consistent theming
- Gradient backgrounds
- Animations (pulse, spin)
- Responsive mobile design
- Dark text on light backgrounds
- Color-coded status indicators

**Color Scheme**:
- Primary: Purple (#7c3aed)
- Success: Green (#10b981)
- Danger: Red (#ef4444)
- Warning: Amber (#f59e0b)

#### `script.js` (232 lines)
**Purpose**: Frontend logic and interactivity
**Key Functions**:
- `generateClonedVoice()`: Send data to backend
- `showError()`: Display error messages
- `showSuccess()`: Display success messages
- Event listeners for all buttons
- MediaRecorder API integration

**Key Libraries**:
- MediaRecorder API (native browser)
- Fetch API (HTTP requests)
- FormData (file uploads)

### Backend Files

#### `app.py` (340+ lines)
**Purpose**: Flask server with API endpoints
**Key Features**:
- Rate limiting (5 requests/minute)
- File validation
- ElevenLabs API integration
- Audio file storage
- Error handling
- CORS support

**Main Endpoints**:
```python
@app.route('/')                 # Serve HTML
@app.route('/api/clone-voice', methods=['POST'])  # Main API
@app.route('/api/status', methods=['GET'])  # Health check
```

**Rate Limiting Logic**:
```python
RATE_LIMIT_REQUESTS = 5         # Max 5 requests
RATE_LIMIT_WINDOW = 60          # Per 60 seconds
rate_limit_store = {}           # Track by IP address
```

#### `requirements.txt`
**Purpose**: Python dependencies

Dependencies:
- `Flask==3.0.0` - Web framework
- `python-dotenv==1.0.0` - Environment variables
- `requests==2.31.0` - HTTP client
- `Flask-Cors==4.0.0` - CORS support

### Configuration Files

#### `.env`
**Purpose**: Store sensitive API keys
**Format**:
```
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxxx
FLASK_ENV=development
```

#### `.gitignore`
**Purpose**: Prevent committing sensitive files
**Ignores**: .env, __pycache__, venv, etc.

## Usage Examples

### Example 1: Recording and Cloning

```javascript
// Step 1: User clicks "Start Recording"
// - Browser requests microphone permission
// - MediaRecorder starts capturing audio

// Step 2: User speaks for 15 seconds
// - Audio is captured in chunks
// - Visualized with pulse indicator

// Step 3: User clicks "Stop Recording"
// - Recording stops
// - Audio displayed in playback control

// Step 4: User types text
// - "Tell me about AI voice cloning"

// Step 5: User clicks "Generate Cloned Voice"
// - JavaScript creates FormData with audio + text
// - Sends POST request to /api/clone-voice
// - Backend responds with base64 audio

// Step 6: Audio plays in cloned voice
// - User hears their cloned voice reading the text
```

### Example 2: Rate Limiting in Action

```
User at IP 192.168.1.100:

Request 1: ✅ Success (4 remaining)
Request 2: ✅ Success (3 remaining)
Request 3: ✅ Success (2 remaining)
Request 4: ✅ Success (1 remaining)
Request 5: ✅ Success (0 remaining)
Request 6: ❌ Rate limit exceeded (wait 60 seconds)
           ⏱️  After 60 seconds, counter resets

Request 7 (after 60s): ✅ Success (4 remaining)
```

### Example 3: Error Handling

```python
# Scenario: User submits without recording

@app.route('/api/clone-voice', methods=['POST'])
def clone_voice():
    if 'audio' not in request.files:
        return jsonify({
            'error': 'No audio file provided'
        }), 400

# Frontend shows:
# ❌ No audio file provided
```

### Example 4: API Response Structure

```json
{
  "success": true,
  "message": "Voice cloned successfully!",
  "audio": "//NExAAiUAP4AQEQAL...(base64 encoded MP3)",
  "original_file": "original_20260307_143022.mp3",
  "cloned_file": "cloned_20260307_143025.mp3",
  "requests_remaining": 3
}
```

## Security Measures Explained

1. **API Key Protection**
   - Stored in `.env` (never in code)
   - Only accessible server-side
   - Never sent to frontend

2. **Rate Limiting**
   - Tracks requests by IP address
   - Resets every 60 seconds
   - Returns 429 status code when exceeded

3. **File Validation**
   - Checks file extension
   - Validates file size (max 25MB)
   - Checks content types

4. **Watermarking**
   - Adds metadata to audio files
   - Includes timestamp and text used
   - Helps track cloned content

5. **CORS Configuration**
   - Prevents unauthorized cross-origin requests
   - Only allows requests from same server

## Performance Considerations

### Request Timeline
```
User uploads: ~100-500ms (depending on microphone sample)
ElevenLabs processing: ~10-30 seconds
Database storage: ~100-500ms
Response time: ~15-30 seconds total
```

### File Sizes
```
Original recording: ~200-800 KB (10-30 seconds)
Cloned MP3 output: ~200-500 KB (depends on text length)
Base64 encoded: ~1.3x larger than binary
```

### Scaling Considerations

For production with many users:
1. Use database instead of in-memory rate limiting
2. Implement Redis for session management
3. Use async workers (Celery)
4. Add audio processing queue
5. Implement user authentication
6. Use S3 or cloud storage for audio files

## Testing the API

### Using cURL:

```bash
# Test if server is running
curl http://localhost:5000/api/status

# Response:
# {"status":"running","api_configured":true}
```

### Using Python:

```python
import requests

response = requests.post(
    'http://localhost:5000/api/clone-voice',
    files={'audio': open('sample.mp3', 'rb')},
    data={'text': 'Hello world'}
)

print(response.json())
```

### Using JavaScript (in browser console):

```javascript
const formData = new FormData();
formData.append('audio', recordedBlob);
formData.append('text', 'Test text');

fetch('/api/clone-voice', {
    method: 'POST',
    body: formData
})
.then(r => r.json())
.then(data => console.log(data));
```

## Common Customizations

### Change Voice Settings

In `app.py`, modify:
```python
tts_data = {
    'text': text,
    'voice_settings': {
        'stability': 0.3,        # More expressive (0-1)
        'similarity_boost': 0.9  # More like original (0-1)
    }
}
```

### Add User Authentication

```python
from flask_login import LoginManager, login_required

@app.route('/api/clone-voice', methods=['POST'])
@login_required
def clone_voice():
    # Rest of code...
```

### Increase Rate Limit

```python
RATE_LIMIT_REQUESTS = 10  # Changed from 5
RATE_LIMIT_WINDOW = 3600   # Changed to 1 hour
```

---

## Next Steps

1. ✅ Setup complete
2. ✅ Test the app locally
3. ✅ Experiment with different voices and texts
4. ✅ Review the code and learn
5. ✅ Customize for your needs
6. ✅ Deploy to production (optional)

For more details, see README.md!
