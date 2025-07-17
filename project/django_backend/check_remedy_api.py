#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, Remedy, Attachment
from issues.serializers import IssueSerializer

def check_remedy_attachments():
    print("=== Checking Remedy Attachments ===")
    
    # Check database state
    remedies = Remedy.objects.all()
    print(f"Total remedies in database: {remedies.count()}")
    
    for remedy in remedies:
        attachments = remedy.attachments.all()
        print(f"\nRemedy ID: {remedy.id}")
        print(f"Remedy description: {remedy.description[:50]}...")
        print(f"Attachments count: {attachments.count()}")
        
        for attachment in attachments:
            print(f"  - Attachment ID: {attachment.id}")
            print(f"    File: {attachment.file.name if attachment.file else 'No file'}")
            print(f"    File type: {attachment.file_type}")
            print(f"    File exists: {attachment.file.storage.exists(attachment.file.name) if attachment.file else False}")
            if attachment.file:
                print(f"    File URL: {attachment.file.url}")
                print(f"    File path: {attachment.file.path}")
    
    # Check API response
    print("\n=== Checking API Response ===")
    issues = Issue.objects.all()[:2]  # Check first 2 issues
    
    for issue in issues:
        print(f"\nIssue ID: {issue.id}")
        serializer = IssueSerializer(issue)
        data = serializer.data
        
        print(f"Remedies in serialized data: {len(data.get('remedies', []))}")
        
        for i, remedy_data in enumerate(data.get('remedies', [])):
            print(f"  Remedy {i+1}:")
            print(f"    Description: {remedy_data.get('description', '')[:50]}...")
            print(f"    Attachments: {len(remedy_data.get('attachments', []))}")
            
            for j, attachment_data in enumerate(remedy_data.get('attachments', [])):
                print(f"      Attachment {j+1}:")
                print(f"        File name: {attachment_data.get('file_name', 'N/A')}")
                print(f"        File URL: {attachment_data.get('file_url', 'N/A')}")
                print(f"        File type: {attachment_data.get('file_type', 'N/A')}")
    
    # Test actual API endpoint
    print("\n=== Testing API Endpoint ===")
    try:
        response = requests.get('http://127.0.0.1:8000/api/issues/', timeout=5)
        if response.status_code == 200:
            api_data = response.json()
            print(f"API returned {len(api_data)} issues")
            
            for issue in api_data[:2]:  # Check first 2 issues
                print(f"\nIssue {issue.get('id', 'Unknown')}:")
                remedies = issue.get('remedies', [])
                print(f"  Remedies: {len(remedies)}")
                
                for remedy in remedies:
                    attachments = remedy.get('attachments', [])
                    print(f"    Remedy attachments: {len(attachments)}")
                    for attachment in attachments:
                        print(f"      - {attachment.get('file_name', 'No name')}: {attachment.get('file_url', 'No URL')}")
        else:
            print(f"API request failed with status: {response.status_code}")
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == '__main__':
    check_remedy_attachments()