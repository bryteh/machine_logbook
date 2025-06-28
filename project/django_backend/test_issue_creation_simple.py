#!/usr/bin/env python
import requests
import json

# Test issue creation API
data = {
    'machine_id_ref': 'SPOOL001',
    'category': 'mechanical',
    'description': 'test issue with id fix',
    'is_runnable': False,
    'priority': 'medium',
    'reported_by': 'Test User'
}

print("Testing issue creation...")
response = requests.post('http://127.0.0.1:8000/api/issues/', json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Check if 'id' is in response
response_data = response.json()
if 'id' in response_data:
    print(f"✅ SUCCESS: Issue created with ID: {response_data['id']}")
else:
    print("❌ ERROR: No 'id' field in response") 