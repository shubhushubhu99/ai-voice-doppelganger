# ⚡ Quick Start Guide

Get your Voice Doppelganger app running in 5 minutes!

## 1️⃣ Get Your API Key (2 minutes)

1. Go to: **https://elevenlabs.io/app/api**
2. Sign up for free (includes credits)
3. Copy your API key

## 2️⃣ Configure API Key (1 minute)

1. Open `.env` file in this directory
2. Replace `your_api_key_here` with your API key
3. Save the file

**Example:**
```
ELEVENLABS_API_KEY=sk_abc123def456...
```

## 3️⃣ Install & Run (2 minutes)

### **Using setup.bat (Easiest - Windows only):**
- Double-click `setup.bat`
- It will install everything for you
- At the end, run `python app.py`

### **Manual Setup (All platforms):**

```powershell
# Open PowerShell in this directory

# Create virtual environment
python -m venv venv

# Activate it (Windows only, shown below)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

## 4️⃣ Open in Browser

Once the server is running, open:
```
http://localhost:5000
```

## That's It! 🎉

You're all set. Start recording and cloning voices!

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python not found" | Install from https://www.python.org/ |
| "Module not found" | Run: `pip install -r requirements.txt` |
| "API Key not set" | Check `.env` file has your key |
| "Port already in use" | Change port in `app.py` line 200 |
| "Microphone denied" | Check browser microphone permissions |

## Need More Help?

See **README.md** for detailed documentation.
