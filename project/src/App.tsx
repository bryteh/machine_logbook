import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import IssueList from './pages/IssueList';
import IssueDetail from './pages/IssueDetail';
import NewIssue from './pages/NewIssue';
import EditIssue from './pages/EditIssue';
import AddRemedy from './pages/AddRemedy';
import EditRemedy from './pages/EditRemedy';
import Login from './pages/Login';
import Settings from './pages/Settings';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public login route without layout */}
          <Route path="/login" element={<Login />} />
          
          {/* All other routes use the layout with RBAC protection */}
          <Route path="/" element={<Layout />}>
            {/* Dashboard - temporarily allow all authenticated users */}
            <Route 
              index 
              element={
                <ProtectedRoute requireAuth={true}>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            
            {/* Issues - publicly accessible for viewing, auth required for creating */}
            <Route path="issues" element={<IssueList />} />
            <Route 
              path="issues/new" 
              element={
                <ProtectedRoute allowPublic={true}>
                  <NewIssue />
                </ProtectedRoute>
              } 
            />
            <Route path="issues/:id" element={<IssueDetail />} />
            <Route 
              path="issues/:id/edit" 
              element={
                <ProtectedRoute permission="crud_issues">
                  <EditIssue />
                </ProtectedRoute>
              } 
            />
            
            {/* Remedies - publicly accessible for creating, auth required for editing */}
            <Route 
              path="issues/:id/add-remedy" 
              element={
                <ProtectedRoute allowPublic={true}>
                  <AddRemedy />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="issues/:id/remedies/:remedyId/edit" 
              element={
                <ProtectedRoute allowPublic={true}>
                  <EditRemedy />
                </ProtectedRoute>
              } 
            />
            
            {/* Settings - requires configure_limits or manage_users permission */}
            <Route 
              path="settings" 
              element={
                <ProtectedRoute permissions={['configure_limits', 'manage_users']}>
                  <Settings />
                </ProtectedRoute>
              } 
            />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;