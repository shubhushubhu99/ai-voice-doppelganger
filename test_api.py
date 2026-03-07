#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for ElevenLabs API key and voice cloning
This script tests the API without affecting main application
"""

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# =====================================
# SETUP
# =====================================

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'audio')

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# =====================================
# TEST FUNCTIONS
# =====================================

def print_header(text):
    """Print formatted header"""
    print(f"\n{BLUE}{'='*50}")
    print(f"{text}")
    print(f"{'='*50}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ {text}{RESET}")

def test_api_key_exists():
    """Test 1: Check if API key exists"""
    print_header("TEST 1: API Key Configuration")
    
    if not ELEVENLABS_API_KEY:
        print_error("ELEVENLABS_API_KEY not set in .env file")
        return False
    
    if ELEVENLABS_API_KEY == 'your_api_key_here':
        print_error("ELEVENLABS_API_KEY still has placeholder value")
        return False
    
    # Show masked API key for verification
    masked_key = ELEVENLABS_API_KEY[:10] + "..." + ELEVENLABS_API_KEY[-5:]
    print_success(f"API Key configured: {masked_key}")
    return True

def test_api_connectivity():
    """Test 2: Check ElevenLabs API connectivity"""
    print_header("TEST 2: API Connectivity")
    
    headers = {
        'Authorization': f'Bearer {ELEVENLABS_API_KEY}'
    }
    
    try:
        # Try to get user account info
        response = requests.get(
            'https://api.elevenlabs.io/v1/user',
            headers=headers,
            timeout=10
        )
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print_success(f"Connected! User: {user_data.get('email', 'Unknown')}")
            print_info(f"Subscription: {user_data.get('subscription', {}).get('tier', 'Unknown')}")
            return True
        elif response.status_code == 401:
            print_error("Invalid API key (401 Unauthorized)")
            return False
        elif response.status_code == 403:
            print_error("Forbidden (403) - Check your API key permissions")
            return False
        else:
            print_error(f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out - ElevenLabs API is slow")
        return False
    except requests.exceptions.ConnectionError as e:
        print_error(f"Connection error: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def test_voice_clone():
    """Test 3: Test voice cloning with actual audio file"""
    print_header("TEST 3: Voice Cloning")
    
    # Find first available audio file
    if not os.path.exists(AUDIO_DIR):
        print_warning(f"Audio directory not found: {AUDIO_DIR}")
        return False
    
    audio_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(('.mp3', '.wav', '.webm', '.m4a'))]
    
    if not audio_files:
        print_warning("No audio files found in audio directory")
        return False
    
    audio_file = audio_files[0]
    audio_path = os.path.join(AUDIO_DIR, audio_file)
    
    print_info(f"Using audio file: {audio_file}")
    print_info(f"File size: {os.path.getsize(audio_path) / 1024:.1f} KB")
    
    # Prepare request
    headers = {
        'Authorization': f'Bearer {ELEVENLABS_API_KEY}'
    }
    
    data = {
        'name': f'test_voice_clone_{datetime.now().timestamp()}'
    }
    
    try:
        print_info("Uploading audio and creating voice clone...")
        
        with open(audio_path, 'rb') as f:
            response = requests.post(
                'https://api.elevenlabs.io/v1/voice_clone',
                headers=headers,
                data=data,
                files={'files': f},
                timeout=60
            )
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            voice_data = response.json()
            voice_id = voice_data.get('voice_id')
            print_success(f"Voice cloned successfully!")
            print_info(f"Voice ID: {voice_id}")
            
            # Test TTS with the cloned voice
            return test_tts(voice_id)
        else:
            print_error(f"Failed to clone voice (HTTP {response.status_code})")
            try:
                error_msg = response.json()
                print_info(f"Error response: {error_msg}")
            except:
                print_info(f"Response text: {response.text[:300]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Voice cloning request timed out")
        return False
    except Exception as e:
        print_error(f"Error during voice cloning: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tts(voice_id):
    """Test 4: Test text-to-speech with cloned voice"""
    print_header("TEST 4: Text-to-Speech Generation")
    
    headers = {
        'Authorization': f'Bearer {ELEVENLABS_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'text': 'This is a test of the cloned voice',
        'voice_settings': {
            'stability': 0.5,
            'similarity_boost': 0.75
        }
    }
    
    try:
        print_info("Generating speech from text...")
        
        response = requests.post(
            f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}',
            headers=headers,
            json=data,
            timeout=60
        )
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            audio_data = response.content
            print_success(f"Speech generated successfully!")
            print_info(f"Audio size: {len(audio_data) / 1024:.1f} KB")
            
            # Save test audio
            test_audio_path = os.path.join(AUDIO_DIR, 'test_cloned_voice.mp3')
            with open(test_audio_path, 'wb') as f:
                f.write(audio_data)
            print_success(f"Test audio saved: {test_audio_path}")
            return True
        else:
            print_error(f"Failed to generate speech (HTTP {response.status_code})")
            try:
                error_msg = response.json()
                print_info(f"Error response: {error_msg}")
            except:
                print_info(f"Response text: {response.text[:300]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("TTS request timed out")
        return False
    except Exception as e:
        print_error(f"Error during TTS generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print_header("🎤 ELEVENLABS API TEST SUITE")
    
    results = {
        'API Key Check': test_api_key_exists(),
        'API Connectivity': test_api_connectivity(),
        'Voice Cloning': test_voice_clone()
    }
    
    # Summary
    print_header("TEST SUMMARY")
    
    for test_name, passed in results.items():
        status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print()
    if all_passed:
        print_success("All tests passed! Your API is working correctly.")
        return 0
    else:
        print_error("Some tests failed. Check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
