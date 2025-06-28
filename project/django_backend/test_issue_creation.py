#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

def test_issue_creation():
    """Test issue creation with API call"""
    
    # Test data similar to what frontend sends
    test_data = {
        'category': 'mechanical',
        'priority': 'medium',
        'alarm_code': '101',
        'description': 'Test issue for debugging',
        'is_runnable': False,
        'machine_id_ref': 'SPOOL001',
        'reported_by': 'Test User'
    }
    
    print("Testing issue creation...")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Make API call
        response = requests.post(
            'http://127.0.0.1:8000/api/issues/',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 201:
            print("✅ Issue creation successful!")
            issue_data = response.json()
            print(f"Created issue ID: {issue_data.get('id')}")
        else:
            print("❌ Issue creation failed!")
            
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    test_issue_creation() 