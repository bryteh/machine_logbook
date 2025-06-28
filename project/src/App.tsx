import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import IssueList from './pages/IssueList';
import NewIssue from './pages/NewIssue';
import EditIssue from './pages/EditIssue';
import IssueDetail from './pages/IssueDetail';
import AddRemedy from './pages/AddRemedy';
import SimpleTest from './pages/SimpleTest';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/issues" element={<IssueList />} />
          <Route path="/issues/new" element={<NewIssue />} />
          <Route path="/issues/:id" element={<IssueDetail />} />
          <Route path="/issues/:id/edit" element={<EditIssue />} />
          <Route path="/issues/:id/add-remedy" element={<AddRemedy />} />
          <Route path="/test" element={<SimpleTest />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;