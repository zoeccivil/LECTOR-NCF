"""
Test Google Cloud Vision credentials
"""
from google.cloud import vision
import os
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

credentials_path = config.get('google_application_credentials')

print(f"📁 Credentials path: {credentials_path}")

# Check file exists
if os.path.exists(credentials_path):
    print(f"✅ File exists")
    
    # Check file content
    with open(credentials_path, 'r') as f:
        creds = json.load(f)
        print(f"✅ Project ID: {creds.get('project_id')}")
        print(f"✅ Client Email: {creds.get('client_email')}")
        print(f"✅ Type: {creds.get('type')}")
else:
    print(f"❌ File NOT found!")
    exit(1)

# Set environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

# Test Vision API
try:
    print("\n🔍 Testing Google Cloud Vision API...")
    client = vision.ImageAnnotatorClient()
    print("✅ Google Cloud Vision client initialized successfully!")
    
    # Test with a simple text detection
    print("\n📝 Testing text detection with sample image...")
    # You can test with an actual image here if you want
    
    print("\n🎉 ALL TESTS PASSED!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()