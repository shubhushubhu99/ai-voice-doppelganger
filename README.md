# 🎤 AI Voice Doppelganger

A web application that clones your voice and uses it to read any text you provide using AI. Built with Flask (Python backend) and vanilla JavaScript (frontend). Powered by ElevenLabs API.

## ✨ Features

- **Voice Recording**: Record your voice directly from your browser (10-30 seconds recommended)
- **Voice Cloning**: Automatically clone your voice using ElevenLabs API
- **Text-to-Speech**: Generate speech in your cloned voice for any text
- **Audio Storage**: All recordings stored locally for your reference
- **Rate Limiting**: Built-in protection (max 5 requests per minute per user)
- **Security**: API key stored safely in `.env` file, never exposed to frontend
- **Watermark Metadata**: Audio files include metadata about the cloning process
- **Beginner Friendly**: Well-commented code with clear explanations

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - Download from https://www.python.org/
- **ElevenLabs API Key** - Get free credits at https://elevenlabs.io/app/api
- **Modern Web Browser** - Chrome, Firefox, Safari, or Edge (needs microphone access)

### Setup Instructions

#### 1. Get Your API Key

1. Visit [https://elevenlabs.io/app/api](https://elevenlabs.io/app/api)
2. Sign up for a free account (includes free credits)
3. Copy your API key from the dashboard

#### 2. Configure Environment

1. Open the `.env` file in this directory (or create one)
2. Replace `your_api_key_here` with your actual ElevenLabs API key:
   ```
   ELEVENLABS_API_KEY=sk-xxxxxxxxxxxxxxxxxxx
   FLASK_ENV=development
   ```
3. Save the file

#### 3. Install Dependencies

Open PowerShell or Command Prompt in this directory and run:

```powershell
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
# source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

#### 4. Run the Application

```powershell
python app.py
```

You should see:
```
==================================================
🎤 VOICE DOPPELGANGER - STARTING SERVER
==================================================
📁 Audio storage: C:\Users\hp\Desktop\ai voice doppelganger\audio
🔐 API Key configured: True
⏱️  Rate limit: 5 requests per 60 seconds
==================================================
🌐 Open http://localhost:5000 in your browser
==================================================
```

#### 5. Access the App

Open your web browser and go to:
```
http://localhost:5000
```

## 📖 How to Use

### Step 1: Record Your Voice
- Click **"🎙️ Start Recording"** button
- Speak for 10-30 seconds to record a sample (read a paragraph, tell a story, etc.)
- Click **"⏹️ Stop Recording"** to finish
- Click **"▶️ Play Recording"** to hear your recording

### Step 2: Enter Text
- Type any text in the text area (up to 500 characters)
- The character count updates as you type

### Step 3: Generate Cloned Voice
- Click **"🚀 Generate Cloned Voice"** button
- Wait 15-30 seconds for processing
- A loading indicator shows the progress

### Step 4: Listen to Result
- Once done, listen to the cloned voice reading your text
- Click **"▶️ Play Cloned Voice"** to play anytime

## 📁 Project Structure

```
ai voice doppelganger/
├── index.html           # Main frontend page
├── style.css            # Styling and layout
├── script.js            # Frontend logic (recording, uploading)
├── app.py               # Flask backend server
├── requirements.txt     # Python dependencies
├── .env                 # API key configuration (NOT in git!)
├── README.md            # This file
└── audio/               # Folder for storing audio files
    ├── original_*.mp3   # Original voice recordings
    └── cloned_*.mp3     # AI-cloned voice outputs
```

## 🔒 Security Features

### ✅ What's Secure:
- **API Key Protection**: ElevenLabs API key stored in `.env`, never sent to frontend
- **Rate Limiting**: Max 5 requests per user per minute prevents abuse
- **Watermark Metadata**: All cloned audio includes metadata about the process
- **Local Storage**: All audio files saved locally on your computer
- **CORS Setup**: Cross-origin requests properly configured

### ⚠️ Important Notes:
- **Never** commit `.env` file to Git with your real API key
- **Never** share your `.env` file or API key publicly
- Add `.env` to `.gitignore` for version control
- Free ElevenLabs accounts have usage limits - check your dashboard

## 🛠️ Technical Details

### Frontend Technologies
- **HTML5**: Audio recording with MediaRecorder API
- **CSS3**: Modern responsive design with gradients and animations
- **JavaScript**: Vanilla JS (no frameworks) - easy to understand and modify

### Backend Technologies
- **Flask**: Lightweight Python web framework
- **Python Requests**: For API calls to ElevenLabs
- **python-dotenv**: Environment variable management
- **Flask-CORS**: Cross-origin resource sharing

### API Integration
- **ElevenLabs Voice Clone API**: To clone your voice from a sample
- **ElevenLabs TTS API**: To generate speech in your cloned voice

## 🎯 How It Works (Behind the Scenes)

1. **Recording**: Browser captures mic audio using MediaRecorder API
2. **Preprocessing**: Audio sent to Flask backend as FormData
3. **Voice Cloning**: 
   - Flask receives audio file
   - Sends to ElevenLabs API to create voice profile
   - Gets back a unique voice ID
4. **Text-to-Speech**: 
   - Uses the voice ID to generate speech from your text
   - ElevenLabs API returns MP3 file
5. **Watermarking**: Metadata added to audio file (timestamp, text used, etc.)
6. **Storage**: Both original and cloned audio saved locally
7. **Return**: Cloned audio sent back to frontend for playback

## ⚙️ Configuration Options

### Rate Limiting (in `app.py`)
```python
RATE_LIMIT_REQUESTS = 5       # Max requests
RATE_LIMIT_WINDOW = 60        # Per 60 seconds
```

### Audio Settings (in `app.py`)
```python
ALLOWED_EXTENSIONS = {'webm', 'mp3', 'wav', 'm4a', 'ogg'}  # File types
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB max
```

### Voice Settings (in `app.py`, TTS section)
```python
'stability': 0.5,           # Voice stability (0-1)
'similarity_boost': 0.75    # How similar to original (0-1)
```

## 🐛 Troubleshooting

### "Microphone access denied"
- Browser doesn't have permission to use your microphone
- Check browser settings: Settings > Privacy > Microphone
- Make sure camera/microphone permission is allowed for localhost

### "ELEVENLABS_API_KEY not set"
- `.env` file not found or API key not configured
- Check that `.env` file exists in the same directory as `app.py`
- Verify the API key is correct (get it from https://elevenlabs.io/app/api)

### "Rate limit exceeded"
- You've made more than 5 requests in 60 seconds
- Wait 1 minute and try again
- Rate limiting resets automatically

### "Failed to clone voice"
- Recording might be too short or unclear
- Try re-recording with a longer, clearer sample
- Check ElevenLabs account for sufficient credits

### Server won't start
- Another app using port 5000
- Try changing port in `app.py`: `app.run(port=5001)`
- Or close any other Flask apps running

## 📊 Rate Limiting Details

- **Limit**: 5 requests per user
- **Window**: 60 seconds
- **Tracked by**: IP address
- **Reset**: Automatic after 60 seconds of no requests
- **Purpose**: Prevent abuse and manage API costs

## 💾 Audio Files

### Original Recordings
- Stored as: `audio/original_YYYYMMDD_HHMMSS.mp3`
- Your raw voice sample
- Used as reference for voice cloning

### Cloned Outputs
- Stored as: `audio/cloned_YYYYMMDD_HHMMSS.mp3`
- Your cloned voice reading the requested text
- Includes watermark metadata

## 🚀 Advanced Usage

### Custom Voice Parameters
Edit the voice settings in `app.py`:
```python
tts_data = {
    'text': text,
    'voice_settings': {
        'stability': 0.3,        # Lower = more expressive (0-1)
        'similarity_boost': 0.9  # Higher = closer to original (0-1)
    }
}
```

### Deploy to Production
For production deployment:
1. Change `debug=False` in `app.py`
2. Use production WSGI server (Gunicorn, uWSGI)
3. Set up HTTPS/SSL certificate
4. Add authentication if needed
5. Use database for rate limiting instead of in-memory storage

## 📝 Common Modifications

### Change Port Number
In `app.py`, modify the last line:
```python
app.run(debug=True, host='localhost', port=8000)  # Changed from 5000
```

### Increase File Size Limit
In `app.py`:
```python
MAX_FILE_SIZE = 100 * 1024 * 1024  # Changed from 25MB to 100MB
```

### Add More Supported Audio Formats
In `app.py`:
```python
ALLOWED_EXTENSIONS = {'webm', 'mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac'}
```

## 📚 Learning Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **ElevenLabs API Docs**: https://elevenlabs.io/docs
- **Web Audio API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- **JavaScript Fetch API**: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

## ❓ FAQ

**Q: Can I use this offline?**
A: No, you need internet to access ElevenLabs API. However, you can run the server locally on your network.

**Q: Is my voice data stored by ElevenLabs?**
A: Yes, ElevenLabs stores voice data as per their privacy policy. Check their docs for details.

**Q: Can I use this for commercial purposes?**
A: Check ElevenLabs' terms of service. Free tier may have limitations.

**Q: How long does voice cloning take?**
A: Usually 15-30 seconds depending on API load.

**Q: Can I use multiple voices?**
A: Yes, record different samples - each gets a unique voice ID.

**Q: What if I want to customize the web interface?**
A: Edit `style.css` for styling, `index.html` for layout, `script.js` for behavior.

## 📄 License

This project is provided as-is for educational and personal use.

## 🤝 Support

For issues with:
- **Frontend**: Check browser console (F12) for JavaScript errors
- **Backend**: Check terminal output for Flask errors
- **API Issues**: Visit https://support.elevenlabs.io/
- **Microphone**: Check your OS audio settings

## 🎉 Enjoy!

You're now ready to create amazing cloned voice content! Have fun experimenting with different texts and voices.

---

**Made with ❤️ for beginners and AI enthusiasts**
