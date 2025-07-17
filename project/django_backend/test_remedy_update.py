import requests
import json

def test_remedy_update():
    """Test that remedy updates work without authentication"""
    
    # Base URL for the API
    base_url = "http://127.0.0.1:8000/api"
    
    print("Testing remedy update without authentication...")
    
    # First, let's get a list of issues to find one with remedies
    try:
        response = requests.get(f"{base_url}/issues/")
        if response.status_code == 200:
            issues = response.json()['results']
            print(f"Found {len(issues)} issues")
            
            if issues:
                issue_id = issues[0]['id']
                print(f"Testing with issue ID: {issue_id}")
                
                # Get remedies for this issue
                remedies_response = requests.get(f"{base_url}/issues/{issue_id}/remedies/")
                print(f"Remedies response status: {remedies_response.status_code}")
                if remedies_response.status_code == 200:
                    remedies = remedies_response.json()
                    print(f"Found {len(remedies)} remedies for issue {issue_id}")
                    
                    if len(remedies) > 0:
                        remedy_id = remedies[0]['id']
                        print(f"Testing remedy update for remedy ID: {remedy_id}")
                        
                        # Try to update the remedy
                        update_data = {
                            "description": "Updated description - test",
                            "technician_name": "Test Technician",
                            "is_external": False,
                            "phone_number": "",
                            "parts_purchased": "",
                            "labor_cost": None,
                            "parts_cost": None,
                            "is_machine_runnable": True
                        }
                        
                        update_response = requests.put(
                            f"{base_url}/issues/{issue_id}/remedies/{remedy_id}/",
                            json=update_data,
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        print(f"Update response status: {update_response.status_code}")
                        if update_response.status_code == 200:
                            print("✓ Remedy update successful!")
                            print(f"Response: {update_response.json()}")
                        else:
                            print(f"✗ Remedy update failed: {update_response.text}")
                    else:
                        print("No remedies found to test with")
                else:
                    print(f"Failed to get remedies: {remedies_response.status_code}")
            else:
                print("No issues found to test with")
        else:
            print(f"Failed to get issues: {response.status_code}")
    
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_remedy_update() 