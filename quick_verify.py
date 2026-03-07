#!/usr/bin/env python3
"""Quick API key validator"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ELEVENLABS_API_KEY')

if not api_key or api_key == 'your_api_key_here':
    print("❌ No API key found")
else:
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        r = requests.get('https://api.elevenlabs.io/v1/user', headers=headers, timeout=5)
        if r.status_code == 200:
            user = r.json()
            print(f"✅ API Key is VALID!\nUser: {user.get('email')}\nTier: {user.get('subscription', {}).get('tier')}")
        else:
            print(f"❌ API Key is INVALID - HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
