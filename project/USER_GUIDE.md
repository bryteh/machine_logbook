# Machine Maintenance Logbook - User Guide

## 🌐 Access Methods

### **Public User Access (No Login Required)**
You can use many features without logging in:

#### What Public Users Can Do:
- ✅ View all issues and their details
- ✅ View all remedies (without sensitive cost/contact info)
- ✅ Create new issues
- ✅ Create new remedies
- ✅ Edit existing remedies
- ✅ Upload and view media attachments
- ✅ Download attachments

#### What Public Users Cannot Do:
- ❌ View dashboard metrics
- ❌ See cost information (labor_cost, parts_cost)
- ❌ See external technician phone numbers
- ❌ Mark issues as resolved/on hold
- ❌ Update issue status directly

### **Authenticated User Access (Admin)**
Login with: `admin` / `admin123`

#### Additional Admin Features:
- ✅ View dashboard with metrics and charts
- ✅ See all cost information
- ✅ See external technician contact details
- ✅ Mark issues as resolved/on hold
- ✅ Update issue status
- ✅ Full administrative access

---

## 🚀 How to Use Each Feature

### **1. Public Access - No Login**
1. Go to `http://localhost:3000`
2. You'll see the issue list immediately (no login needed)
3. Click any issue to view details
4. Use "Add New Issue" to create issues
5. Use "Add Remedy" to create remedies
6. Click on remedies to edit them

### **2. Admin Access - With Login**
1. Go to `http://localhost:3000/login`
2. Enter credentials: `admin` / `admin123`
3. You'll be redirected to the dashboard automatically
4. From dashboard, you can:
   - View metrics and charts
   - See cost breakdowns
   - Access all issues with full details

### **3. Creating Issues (Public & Admin)**
1. Click "Add New Issue" from any page
2. Fill in required fields:
   - Machine ID
   - Category
   - Description
   - Reporter name
3. Optionally attach photos/videos
4. Submit

### **4. Adding Remedies (Public & Admin)**
1. Go to any issue detail page
2. Click "Add Remedy"
3. Fill in remedy details
4. Toggle between Internal/External technician
5. Add parts and cost info (if admin)
6. Upload remedy photos/videos
7. Submit

### **5. Editing Remedies (Public & Admin)**
1. Go to issue detail page
2. Find the remedy you want to edit
3. Click the edit button
4. Modify any fields
5. Upload additional attachments if needed
6. Save changes

---

## 🔧 Troubleshooting

### **"Failed to load dashboard metrics"**
- **Cause**: Not logged in as admin
- **Solution**: Login with `admin` / `admin123` first

### **"Authentication credentials were not provided"**
- **Cause**: Trying to access admin-only features without login
- **Solution**: Either login as admin or use public features instead

### **Cannot see cost information**
- **Public users**: This is intentional for privacy
- **Admin users**: Make sure you're logged in properly

### **Cannot see external technician phone numbers**
- **Public users**: This is intentional for privacy
- **Admin users**: Make sure you're logged in properly

### **Cannot mark issues as resolved**
- **Public users**: This requires executive-level permissions
- **Admin users**: Should work - check if you're logged in

---

## 📱 URLs and Navigation

### **Direct Access URLs:**
- **Public Issue List**: `http://localhost:3000/`
- **Admin Login**: `http://localhost:3000/login`
- **Admin Dashboard**: `http://localhost:3000/dashboard` (login required)
- **Add Issue**: `http://localhost:3000/issues/new` (public access)

### **Navigation Tips:**
- Logo always takes you to main page (issue list)
- "Dashboard" link requires admin login
- All other navigation works for public users

---

## 🎯 Testing Scenarios

### **Test as Public User:**
1. Don't login - go directly to `http://localhost:3000`
2. Create a new issue
3. Add a remedy to any issue
4. Edit an existing remedy
5. Upload photos to remedies
6. Verify you cannot see costs/phone numbers

### **Test as Admin:**
1. Login at `http://localhost:3000/login`
2. View dashboard metrics
3. See cost information in remedies
4. Mark issues as resolved/on hold
5. View external technician contact info

---

## 🔍 What's Fixed

### ✅ **Login Issues - RESOLVED**
- No more redirect loops
- Stable session management
- Proper authentication state

### ✅ **Dashboard Metrics - RESOLVED**
- Works for authenticated admin users
- Clear error messages if not logged in
- Proper permission handling

### ✅ **Public Remedy Editing - RESOLVED**
- Public users can edit without authentication errors
- Backend handles issue status automatically
- File uploads work for all users

### ✅ **Media Attachments - RESOLVED**
- Public users can view all media
- Both issue and remedy attachments visible
- Download functionality works

### ✅ **Permission System - RESOLVED**
- Resolved/Hold buttons only for authorized users
- Cost information properly protected
- External contact info properly protected

---

## 🆘 Still Having Issues?

1. **Clear browser cache and cookies**
2. **Check browser console for errors** (F12 → Console)
3. **Ensure both servers are running:**
   - Frontend: `http://localhost:3000`
   - Backend: `http://127.0.0.1:8000`
4. **Try in incognito/private browsing mode**

The system is now fully functional with both public and authenticated access working correctly! 