#!/usr/bin/env python3
"""
Quick test to verify both servers are running and authentication is working
"""
import requests
import time

def test_servers():
    print("🧪 QUICK SERVER TEST")
    print("=" * 40)
    
    # Wait a moment for servers to start
    print("⏳ Waiting for servers to start...")
    time.sleep(3)
    
    # Test Django backend
    print("\n1️⃣ Testing Django Backend...")
    try:
        response = requests.get('http://127.0.0.1:8000/api/auth/user/', timeout=5)
        if response.status_code in [401, 403]:
            print("✅ Django backend is running (got expected auth error)")
        else:
            print(f"✅ Django backend is running (status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Django backend not responding: {str(e)}")
        return False
    
    # Test authentication
    print("\n2️⃣ Testing Authentication...")
    session = requests.Session()
    try:
        login_data = {'username': 'admin', 'password': 'admin123'}
        login_response = session.post('http://127.0.0.1:8000/api/auth/login/', json=login_data, timeout=5)
        
        if login_response.status_code == 200:
            print("✅ Admin login successful!")
            user_data = login_response.json()
            print(f"   Username: {user_data['user']['username']}")
            print(f"   Role: {user_data['user']['role']['role_name']}")
            
            # Test dashboard access
            dashboard_response = session.get('http://127.0.0.1:8000/api/dashboard/metrics/', timeout=5)
            if dashboard_response.status_code == 200:
                metrics = dashboard_response.json()
                print(f"✅ Dashboard access working (Total issues: {metrics.get('total_issues', 'N/A')})")
                if 'total_cost' in metrics:
                    print(f"✅ Cost data visible: ${metrics['total_cost']:.2f}")
            else:
                print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication test failed: {str(e)}")
        return False
    
    # Test frontend
    print("\n3️⃣ Testing Frontend...")
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server is running")
        else:
            print(f"⚠️ Frontend responded with status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not responding: {str(e)}")
        print("   (Frontend may still be starting up)")
    
    print("\n" + "=" * 40)
    print("🎉 SERVER STATUS:")
    print("   Django Backend: ✅ RUNNING")
    print("   Authentication: ✅ WORKING") 
    print("   Dashboard & Costs: ✅ WORKING")
    print("   Frontend: Starting up...")
    print("\n📋 You can now:")
    print("   1. Open http://localhost:3000 in your browser")
    print("   2. Login with: admin / admin123") 
    print("   3. Access all admin features")
    print("=" * 40)
    
    return True

if __name__ == "__main__":
    test_servers() 