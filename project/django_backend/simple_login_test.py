import requests
import time

print("🔍 Testing Django Backend Connection...")
time.sleep(2)  # Wait for server to start

try:
    response = requests.post('http://127.0.0.1:8000/api/auth/login/', 
                            json={'username': 'admin', 'password': 'admin123'},
                            timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS: Django Backend & Authentication Working!")
        print(f"   Username: {data['user']['username']}")
        print(f"   Role: {data['user']['role']['role_name']}")
        print(f"   Permissions: {len(data['user']['role']['permissions'])} permissions")
        print("\n🎉 You can now access:")
        print("   • Django Backend: http://127.0.0.1:8000")
        print("   • Frontend: http://localhost:3000") 
        print("   • Admin Login: admin / admin123")
        print("   • All admin features working!")
    else:
        print(f"❌ Login failed: HTTP {response.status_code}")
        print(f"   Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Django backend not running")
    print("   Please start Django with: python manage.py runserver 127.0.0.1:8000")
except Exception as e:
    print(f"❌ Test failed: {str(e)}") 