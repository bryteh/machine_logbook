import os
import sys
import subprocess
import time
import requests
import threading
import signal
import webbrowser

def run_django_server():
    """Run the Django development server"""
    print("Starting Django server...")
    try:
        # Run Django server on port 8000
        django_process = subprocess.Popen(
            ["python", "manage.py", "runserver", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://127.0.0.1:8000/api/")
            if response.status_code == 200 or response.status_code == 404:
                print("Django server is running on http://127.0.0.1:8000/")
                return django_process
            else:
                print(f"Django server returned status code {response.status_code}")
                django_process.terminate()
                return None
        except requests.RequestException:
            print("Django server is not responding")
            django_process.terminate()
            return None
            
    except Exception as e:
        print(f"Error starting Django server: {e}")
        return None

def verify_fixes():
    """Verify that our fixes are working"""
    print("\nVerifying fixes...")
    
    # Check if Django API is accessible
    try:
        response = requests.get("http://127.0.0.1:8000/api/issues/")
        if response.status_code == 200:
            print("✓ API is accessible and returning data")
        else:
            print(f"✗ API returned status code {response.status_code}")
    except requests.RequestException as e:
        print(f"✗ Error accessing API: {e}")
    
    # Check if remedy update endpoint allows OPTIONS request (CORS preflight)
    try:
        response = requests.options(
            "http://127.0.0.1:8000/api/issues/1/remedies/1/",
            headers={"Origin": "http://localhost:3000"}
        )
        
        if response.status_code == 200:
            allow_header = response.headers.get("Allow", "")
            if "PUT" in allow_header:
                print("✓ Remedy update endpoint allows PUT method")
            else:
                print(f"✗ Remedy update endpoint does not allow PUT method. Allowed methods: {allow_header}")
        else:
            print(f"✗ OPTIONS request failed with status code {response.status_code}")
    except requests.RequestException as e:
        print(f"✗ Error checking remedy update endpoint: {e}")
    
    print("\nTo test the fixes manually:")
    print("1. Go to http://127.0.0.1:8000/admin/ and log in with admin credentials")
    print("2. Then try editing a remedy at http://127.0.0.1:8000/api/issues/1/remedies/1/")
    print("3. Check that you can upload attachments to remedies")
    print("4. Verify that login works properly and redirects to the correct page")

def main():
    """Main function to run servers and test fixes"""
    print("=== Testing Machine Maintenance Logbook Fixes ===")
    
    # Run Django server
    django_process = run_django_server()
    
    if django_process:
        try:
            # Verify fixes
            verify_fixes()
            
            # Keep servers running until user presses Ctrl+C
            print("\nPress Ctrl+C to stop the servers...")
            
            # Open admin page in browser
            webbrowser.open("http://127.0.0.1:8000/admin/")
            
            # Wait for Ctrl+C
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nStopping servers...")
        finally:
            # Stop Django server
            if django_process:
                django_process.terminate()
                print("Django server stopped")
    
    print("Done!")

if __name__ == "__main__":
    main() 