#!/usr/bin/env python
import requests
import json

base_url = "https://5000-id7a4tchrq6p71yrkzpi9-6532622b.e2b.dev"

print("Testing FC26 Phase 3 Security System")
print("=" * 50)

# Test endpoints
endpoints = [
    ("/", "GET", None),
    ("/api/system/status", "GET", None),
    ("/dashboard", "GET", None),
    ("/fortress/v2/", "GET", None),
]

for endpoint, method, data in endpoints:
    try:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting: {method} {endpoint}")
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        print(f"Status: {response.status_code}")
        
        # Try to parse as JSON
        try:
            content = response.json()
            if "error" in content:
                print(f"Error: {content['error']}")
            else:
                print(f"Response: {json.dumps(content, indent=2)[:200]}")
        except:
            # If not JSON, show HTML snippet
            print(f"HTML Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"Failed: {str(e)}")

print("\n" + "=" * 50)
print("Test completed!")