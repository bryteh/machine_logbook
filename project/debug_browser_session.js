// Browser Console Debug Script for Session Issues
// Copy and paste this into your browser console while on the frontend

console.log('🔍 DEBUGGING BROWSER SESSION ISSUES');
console.log('================================');

// Check current cookies
console.log('1️⃣ Current cookies:');
console.log('Document cookies:', document.cookie);

// Check if session cookies exist
const cookies = document.cookie.split(';').reduce((acc, cookie) => {
  const [name, value] = cookie.trim().split('=');
  acc[name] = value;
  return acc;
}, {});

console.log('Parsed cookies:', cookies);
console.log('CSRF Token exists:', !!cookies.csrftoken);
console.log('Session ID exists:', !!cookies.sessionid);

// Test API call to auth endpoint
console.log('\n2️⃣ Testing getCurrentUser API call...');
fetch('http://127.0.0.1:8000/api/auth/user/', {
  method: 'GET',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': cookies.csrftoken || ''
  }
})
.then(response => {
  console.log('getCurrentUser response status:', response.status);
  return response.json();
})
.then(data => {
  console.log('getCurrentUser response data:', data);
})
.catch(error => {
  console.error('getCurrentUser error:', error);
});

// Test dashboard API call
console.log('\n3️⃣ Testing dashboard metrics API call...');
fetch('http://127.0.0.1:8000/api/dashboard/metrics/?days=30', {
  method: 'GET',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': cookies.csrftoken || ''
  }
})
.then(response => {
  console.log('Dashboard response status:', response.status);
  return response.json();
})
.then(data => {
  console.log('Dashboard response data:', data);
})
.catch(error => {
  console.error('Dashboard error:', error);
});

// Check current URL and origin
console.log('\n4️⃣ Current page info:');
console.log('Current URL:', window.location.href);
console.log('Origin:', window.location.origin);

console.log('\n================================');
console.log('Check the results above to identify the session issue!'); 