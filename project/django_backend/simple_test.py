import requests

try:
    print("Testing basic API access...")
    response = requests.get("http://127.0.0.1:8000/api/issues/")
    print(f"Issues API status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            issue_id = data['results'][0]['id']
            print(f"First issue ID: {issue_id}")
            
            # Test remedies endpoint
            remedies_url = f"http://127.0.0.1:8000/api/issues/{issue_id}/remedies/"
            print(f"Testing remedies URL: {remedies_url}")
            
            remedies_response = requests.get(remedies_url)
            print(f"Remedies status: {remedies_response.status_code}")
            
            if remedies_response.status_code == 200:
                remedies_data = remedies_response.json()
                print(f"Remedies data type: {type(remedies_data)}")
                print(f"Remedies data: {remedies_data}")
                
                if 'results' in remedies_data and len(remedies_data['results']) > 0:
                    remedy_id = remedies_data['results'][0]['id']
                    print(f"First remedy ID: {remedy_id}")
                    
                    # Test remedy update
                    update_url = f"http://127.0.0.1:8000/api/issues/{issue_id}/remedies/{remedy_id}/"
                    update_data = {
                        "description": "Test update",
                        "technician_name": "Test Tech",
                        "is_external": False,
                        "phone_number": "",
                        "parts_purchased": "",
                        "is_machine_runnable": True
                    }
                    
                    print(f"Testing remedy update at: {update_url}")
                    update_response = requests.put(update_url, json=update_data)
                    print(f"Update status: {update_response.status_code}")
                    print(f"Update response: {update_response.text}")
            else:
                print(f"Failed to get remedies: {remedies_response.text}")
        else:
            print("No issues found")
    else:
        print(f"Failed to get issues: {response.text}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 