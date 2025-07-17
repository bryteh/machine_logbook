import requests
import json

try:
    response = requests.get('http://127.0.0.1:8000/api/issues/')
    if response.status_code == 200:
        data = response.json()
        print(f"Total issues: {len(data)}")
        
        for issue in data:
            print(f"\nIssue ID: {issue.get('id')}")
            print(f"Description: {issue.get('description', '')[:50]}...")
            
            remedies = issue.get('remedies', [])
            print(f"Remedies count: {len(remedies)}")
            
            for i, remedy in enumerate(remedies):
                print(f"  Remedy {i+1}:")
                print(f"    Description: {remedy.get('description', '')[:30]}...")
                print(f"    Technician: {remedy.get('technician_name', 'N/A')}")
                print(f"    Labor cost: {remedy.get('labor_cost', 0)}")
                print(f"    Parts cost: {remedy.get('parts_cost', 0)}")
                print(f"    Total cost: {remedy.get('total_cost', 0)}")
                
                attachments = remedy.get('attachments', [])
                print(f"    Attachments count: {len(attachments)}")
                
                if attachments:
                    for j, attachment in enumerate(attachments):
                        print(f"      Attachment {j+1}:")
                        print(f"        File name: {attachment.get('file_name', 'N/A')}")
                        print(f"        File URL: {attachment.get('file_url', 'N/A')}")
                        print(f"        File type: {attachment.get('file_type', 'N/A')}")
                        print(f"        Purpose: {attachment.get('purpose', 'N/A')}")
                else:
                    print("      No attachments found")
            
            if len(remedies) == 0:
                print("  No remedies found")
                
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"Error connecting to API: {e}")