# -*- coding: utf-8 -*-
"""
Syntax and dependency checker for Voice Doppelganger app
"""

import sys
import ast
import os

def check_python_syntax():
    """Check if all Python files have valid syntax"""
    print("\n" + "="*50)
    print("SYNTAX & DEPENDENCY CHECK")
    print("="*50 + "\n")
    
    python_files = ['app.py', 'verify_setup.py', 'test_connection.py']
    all_valid = True
    
    for filename in python_files:
        if not os.path.exists(filename):
            print(f"Skipping {filename} - File not found")
            continue
            
        print(f"Checking {filename}...")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
                ast.parse(code)
            print(f"   Valid Python syntax")
        except SyntaxError as e:
            print(f"   Syntax error at line {e.lineno}: {e.msg}")
            all_valid = False
        except Exception as e:
            print(f"   Error: {e}")
            all_valid = False
    
    # Check dependencies
    print(f"\nChecking Python dependencies...")
    required = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS', 
        'dotenv': 'python-dotenv',
        'requests': 'requests'
    }
    
    for import_name, package_name in required.items():
        try:
            __import__(import_name)
            print(f"   OK: {package_name}")
        except ImportError:
            print(f"   MISSING: {package_name}")
            print(f"      Run: pip install {package_name}")
            all_valid = False
    
    print("\n" + "="*50)
    if all_valid:
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED")
    print("="*50 + "\n")
    
    return all_valid

if __name__ == '__main__':
    success = check_python_syntax()
    sys.exit(0 if success else 1)
