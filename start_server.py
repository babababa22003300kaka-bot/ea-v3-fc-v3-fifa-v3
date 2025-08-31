#!/usr/bin/env python
"""Start Flask server properly"""
import os
import sys
sys.path.insert(0, '/home/user/webapp')
os.chdir('/home/user/webapp')

from app import app

if __name__ == '__main__':
    print("🚀 Starting FC26 Phase 3 Security Server...")
    print("📍 Access URL: https://5000-id7a4tchrq6p71yrkzpi9-6532622b.e2b.dev")
    print("=" * 60)
    
    # Run Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )