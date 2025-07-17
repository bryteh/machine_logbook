// Browser debugging script for login flow
// Copy and paste this into browser console after opening the app

console.log('🐛 LOGIN FLOW DEBUGGER ACTIVATED');
console.log('=====================================');

// Store original console methods
const originalLog = console.log;
const originalError = console.error;

// Track authentication-related console messages
let authLogs = [];

// Override console methods to capture auth-related logs
console.log = function(...args) {
  const message = args.join(' ');
  if (message.includes('AuthContext') || message.includes('API:') || message.includes('Login')) {
    authLogs.push({
      type: 'log',
      timestamp: new Date().toISOString(),
      message: message
    });
  }
  originalLog.apply(console, args);
};

console.error = function(...args) {
  const message = args.join(' ');
  if (message.includes('AuthContext') || message.includes('API:') || message.includes('Login')) {
    authLogs.push({
      type: 'error',
      timestamp: new Date().toISOString(),
      message: message
    });
  }
  originalError.apply(console, args);
};

// Function to print the captured logs
window.printAuthLogs = function() {
  console.log('\n📋 CAPTURED AUTHENTICATION LOGS:');
  console.log('==================================');
  authLogs.forEach((log, index) => {
    const time = new Date(log.timestamp).toLocaleTimeString();
    const icon = log.type === 'error' ? '❌' : '📝';
    console.log(`${icon} [${time}] ${log.message}`);
  });
  console.log('\n');
};

// Function to clear logs
window.clearAuthLogs = function() {
  authLogs = [];
  console.log('🧹 Authentication logs cleared');
};

// Monitor network requests to auth endpoints
const originalFetch = window.fetch;
window.fetch = function(...args) {
  const url = args[0];
  if (typeof url === 'string' && url.includes('/auth/')) {
    console.log(`🌐 Network Request: ${args[1]?.method || 'GET'} ${url}`);
  }
  return originalFetch.apply(this, args);
};

// Monitor localStorage and sessionStorage changes
const originalSetItem = Storage.prototype.setItem;
Storage.prototype.setItem = function(key, value) {
  if (key.includes('auth') || key.includes('user') || key.includes('token')) {
    console.log(`💾 Storage SET: ${key} = ${value.substring(0, 50)}...`);
  }
  return originalSetItem.apply(this, arguments);
};

// Monitor cookie changes
let lastCookies = document.cookie;
setInterval(() => {
  if (document.cookie !== lastCookies) {
    console.log('🍪 Cookies changed:', document.cookie);
    lastCookies = document.cookie;
  }
}, 1000);

console.log(`
📖 DEBUGGING INSTRUCTIONS:
1. Navigate to /login
2. Enter credentials: admin / admin123
3. Click login and watch the console
4. After the issue reproduces, run: printAuthLogs()
5. To clear logs, run: clearAuthLogs()

🔍 WHAT TO LOOK FOR:
- Multiple "AuthContext: Checking auth status..." messages
- "API: getCurrentUser failed" messages
- Timing between login success and auth check failures
- Cookie/session issues

Ready to debug! Try logging in now...
`);

// Debug script to test login flow
// Run this in browser console to debug login issues

console.log('🔍 DEBUGGING LOGIN FLOW');
console.log('========================');

async function testLoginFlow() {
  try {
    // Clear any existing session first
    document.cookie.split(";").forEach(function(c) { 
      document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
    });
    
    console.log('1️⃣ Cleared existing cookies');
    
    // Step 1: Login request
    console.log('2️⃣ Attempting login...');
    const loginResponse = await fetch('http://127.0.0.1:8000/api/auth/login/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: 'admin',
        password: 'admin123'
      })
    });
    
    console.log('Login response status:', loginResponse.status);
    
    if (loginResponse.ok) {
      const loginData = await loginResponse.json();
      console.log('✅ Login successful!');
      console.log('User data:', loginData);
      
      // Check what cookies were set
      console.log('3️⃣ Cookies after login:', document.cookie);
      
      // Test getCurrentUser
      console.log('4️⃣ Testing getCurrentUser...');
      const userResponse = await fetch('http://127.0.0.1:8000/api/auth/user/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (userResponse.ok) {
        const userData = await userResponse.json();
        console.log('✅ getCurrentUser successful!');
        console.log('Current user:', userData);
        console.log('User permissions:', userData.role?.permissions || 'No permissions');
        console.log('Has view_dashboard?', userData.role?.permissions?.includes('view_dashboard'));
      } else {
        console.log('❌ getCurrentUser failed:', userResponse.status);
        const errorText = await userResponse.text();
        console.log('Error:', errorText);
      }
      
    } else {
      console.log('❌ Login failed:', loginResponse.status);
      const errorText = await loginResponse.text();
      console.log('Error:', errorText);
    }
    
  } catch (error) {
    console.error('❌ Login flow error:', error);
  }
}

testLoginFlow(); 