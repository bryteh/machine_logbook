import requests
import json

def test_remedy_crud():
    """Test complete CRUD operations on remedies without authentication"""
    
    print("Testing remedy CRUD operations...")
    
    base_url = "http://127.0.0.1:8000/api"
    
    try:
        # Get an issue to work with
        issues_response = requests.get(f"{base_url}/issues/")
        if issues_response.status_code != 200:
            print("Failed to get issues")
            return
        
        issues_data = issues_response.json()
        if not issues_data['results']:
            print("No issues found")
            return
        
        issue_id = issues_data['results'][0]['id']
        print(f"Using issue ID: {issue_id}")
        
        # Create a remedy
        remedy_data = {
            "description": "Test remedy for API testing",
            "technician_name": "API Test Tech",
            "is_external": False,
            "phone_number": "",
            "parts_purchased": "Test parts",
            "labor_cost": 100.50,
            "parts_cost": 50.25,
            "is_machine_runnable": True
        }
        
        print("\n1. Creating remedy...")
        create_response = requests.post(f"{base_url}/issues/{issue_id}/remedies/", json=remedy_data)
        print(f"Create status: {create_response.status_code}")
        
        if create_response.status_code != 201:
            print(f"Create failed: {create_response.text}")
            return
        
        remedy = create_response.json()
        print(f"Create response data: {remedy}")
        remedy_id = remedy['id']
        print(f"✓ Remedy created with ID: {remedy_id}")
        
        # Update the remedy
        update_data = {
            "description": "UPDATED: Test remedy for API testing",
            "technician_name": "UPDATED API Test Tech",
            "is_external": True,
            "phone_number": "123-456-7890",
            "parts_purchased": "UPDATED test parts",
            "labor_cost": 200.75,
            "parts_cost": 75.50,
            "is_machine_runnable": False
        }
        
        print("\n2. Updating remedy...")
        update_response = requests.put(f"{base_url}/issues/{issue_id}/remedies/{remedy_id}/", json=update_data)
        print(f"Update status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            updated_remedy = update_response.json()
            print("✓ Remedy updated successfully!")
            print(f"Update response: {updated_remedy}")
            print(f"Updated description: {updated_remedy.get('description', 'N/A')}")
            print(f"Updated technician: {updated_remedy.get('technician_name', 'N/A')}")
        else:
            print(f"✗ Update failed: {update_response.text}")
            return
        
        # Get the remedy to verify
        print("\n3. Retrieving updated remedy...")
        get_response = requests.get(f"{base_url}/issues/{issue_id}/remedies/")
        if get_response.status_code == 200:
            remedies = get_response.json()['results']
            found_remedy = next((r for r in remedies if r['id'] == remedy_id), None)
            if found_remedy:
                print("✓ Remedy retrieved successfully!")
                print(f"Final description: {found_remedy['description']}")
            else:
                print("✗ Remedy not found in list")
        else:
            print(f"✗ Failed to retrieve remedies: {get_response.text}")
        
        print("\n✓ All remedy operations completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_remedy_crud() 