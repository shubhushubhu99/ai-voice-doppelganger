# -*- coding: utf-8 -*-
"""
Connection Test Script
Tests Flask server and all connections
"""

import requests
import sys
import time

def test_server():
    """Test if Flask server is running"""
    print("\n" + "="*50)
    print("TESTING VOICE DOPPELGANGER SERVER")
    print("="*50 + "\n")
    
    # Test 1: Server running
    print("1️⃣  Testing if Flask server is running on localhost:5000...")
    try:
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        if response.status_code == 200:
            print("   ✅ Flask server is running!")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Server returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Flask server on localhost:5000")
        print("   Make sure Flask is running: python app.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Frontend accessible
    print("\n2️⃣  Testing if frontend is accessible...")
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is accessible!")
        else:
            print(f"   ❌ Frontend returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cannot access frontend: {e}")
    
    # Test 3: API key configured
    print("\n3️⃣  Testing if ElevenLabs API key is configured...")
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if api_key and api_key != 'your_api_key_here':
            print("   ✅ API key is configured!")
            print(f"   Key preview: {api_key[:10]}...")
        else:
            print("   ❌ API key not configured or is default value")
            print("   Edit .env and add your ElevenLabs API key")
    except Exception as e:
        print(f"   ❌ Error checking API key: {e}")
    
    # Test 4: Network connectivity
    print("\n4️⃣  Testing network connectivity to ElevenLabs API...")
    try:
        response = requests.get('https://api.elevenlabs.io/v1/ping', timeout=5)
        print("   ✅ Can reach ElevenLabs API")
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot reach ElevenLabs API - check internet connection")
    except Exception as e:
        print(f"   ⚠️  ElevenLabs test result: {type(e).__name__}")
    
    print("\n" + "="*50)
    print("✅ TESTS COMPLETE")
    print("="*50 + "\n")
    
    return True

if __name__ == '__main__':
    test_server()
