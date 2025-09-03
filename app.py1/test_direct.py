#!/usr/bin/env python
"""Test Flask app directly to see errors"""
import sys
import os
sys.path.insert(0, '/home/user/webapp')
os.chdir('/home/user/webapp')

from app import app

# Enable debug mode to see errors
app.config['DEBUG'] = True
app.config['TESTING'] = True

# Create test client
client = app.test_client()

print("Testing Flask App Directly")
print("=" * 50)

# Test root endpoint
try:
    print("\n1. Testing GET /")
    response = client.get('/')
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Response: {response.data.decode()[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test API status
try:
    print("\n2. Testing GET /api/system/status")
    response = client.get('/api/system/status')
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.data.decode()[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test dashboard
try:
    print("\n3. Testing GET /dashboard")
    response = client.get('/dashboard')
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Response: {response.data.decode()[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)