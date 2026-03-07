"""
Voice Doppelganger - Setup Verification Script

This script checks if everything is properly configured before running the app.
Run this before running app.py to catch any issues early.
"""

import os
import sys
from pathlib import Path

def print_header():
    print("\n" + "="*50)
    print("🎤 VOICE DOPPELGANGER - SETUP VERIFICATION")
    print("="*50 + "\n")

def check_python_version():
    """Check if Python version is 3.8+"""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ❌ ERROR: Python 3.8+ required. You have {version.major}.{version.minor}")
        return False

def check_required_files():
    """Check if all required files exist"""
    print("\n✓ Checking required files...")
    required_files = [
        'app.py',
        'index.html',
        'style.css',
        'script.js',
        'requirements.txt',
        '.env'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ Missing: {file}")
            all_exist = False
    
    return all_exist

def check_audio_directory():
    """Check if audio directory exists"""
    print("\n✓ Checking audio directory...")
    if os.path.exists('audio'):
        print(f"  ✅ audio/ directory exists")
        return True
    else:
        print(f"  ❌ audio/ directory missing (creating...)")
        os.makedirs('audio', exist_ok=True)
        print(f"  ✅ audio/ directory created")
        return True

def check_env_configuration():
    """Check if .env file is properly configured"""
    print("\n✓ Checking .env configuration...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('ELEVENLABS_API_KEY')
        
        if not api_key:
            print(f"  ❌ ELEVENLABS_API_KEY not set in .env")
            return False
        elif api_key == 'your_api_key_here':
            print(f"  ⚠️  WARNING: ELEVENLABS_API_KEY is still the default value")
            print(f"     Please set your actual API key from https://elevenlabs.io/app/api")
            return False
        else:
            print(f"  ✅ ELEVENLABS_API_KEY is configured")
            print(f"     Key starts with: {api_key[:6]}...")
            return True
    except Exception as e:
        print(f"  ❌ Error reading .env: {e}")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n✓ Checking Python dependencies...")
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'dotenv': 'python-dotenv',
        'requests': 'requests'
    }
    
    all_installed = True
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ Missing: {package_name}")
            all_installed = False
    
    if not all_installed:
        print("\n  💡 Install missing packages with:")
        print("     pip install -r requirements.txt")
    
    return all_installed

def check_port_available():
    """Check if port 5000 is available"""
    print("\n✓ Checking if port 5000 is available...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    sock.close()
    
    if result == 0:
        print(f"  ⚠️  WARNING: Port 5000 is already in use")
        print(f"     Another Flask app might be running")
        print(f"     You can change the port in app.py line 200")
        return False
    else:
        print(f"  ✅ Port 5000 is available")
        return True

def run_all_checks():
    """Run all verification checks"""
    print_header()
    
    checks = [
        ("Python Version", check_python_version()),
        ("Required Files", check_required_files()),
        ("Audio Directory", check_audio_directory()),
        ("Dependencies", check_dependencies()),
        ("Port 5000 Availability", check_port_available()),
        (".env Configuration", check_env_configuration()),
    ]
    
    print("\n" + "="*50)
    print("VERIFICATION SUMMARY")
    print("="*50)
    
    all_passed = True
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check_name}")
        if not result:
            all_passed = False
    
    print("="*50 + "\n")
    
    if all_passed:
        print("🎉 All checks passed! You're ready to run:")
        print("   python app.py\n")
    else:
        print("⚠️  Please fix the issues above before running the app\n")
        print("Need help? Check the README.md or QUICKSTART.md files.\n")
    
    return all_passed

if __name__ == '__main__':
    success = run_all_checks()
    sys.exit(0 if success else 1)
