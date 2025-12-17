import requests
import json

# First, let's try to login and get a token
print("=== Testing Profile API ===\n")

# Check what token is being used (you need to get this from browser localStorage)
print("To test this properly, we need the JWT token from your browser.")
print("Open browser console and run: localStorage.getItem('token')")
print("\nPaste the token here and press Enter:")
token = input().strip()

if token:
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Test the profile endpoint
    print("\n1. Testing GET /api/auth/profile...")
    response = requests.get("http://localhost:8000/api/auth/profile", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Profile loaded successfully!")
        print(f"Email: {data.get('email')}")
        print(f"Name: {data.get('name')}")
        print(f"Headline: {data.get('headline')}")
        print(f"Skills count: {len(data.get('skills', []))}")
        print(f"\nFull response:")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Error: {response.text}")
else:
    print("No token provided, skipping API test")
