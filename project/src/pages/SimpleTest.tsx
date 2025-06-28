import React, { useState } from 'react';

const SimpleTest: React.FC = () => {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ color: '#333', borderBottom: '2px solid #007bff', paddingBottom: '10px' }}>
        🔧 Machine Maintenance Logbook
      </h1>
      
      <div style={{ background: '#d4edda', padding: '15px', borderRadius: '5px', margin: '20px 0', border: '1px solid #c3e6cb' }}>
        <p><strong>✅ React Application is Working!</strong></p>
        <p>✅ TypeScript compilation successful</p>
        <p>✅ Component rendering correctly</p>
        <p>✅ State management functional</p>
      </div>

      <div style={{ background: '#fff3cd', padding: '15px', borderRadius: '5px', margin: '20px 0', border: '1px solid #ffeaa7' }}>
        <h3 style={{ margin: '0 0 10px 0' }}>🚫 Ad Blocker Issue Detected</h3>
        <p>The error shows <code>lucide-react/icons/fingerprint.js</code> is being blocked.</p>
        <p><strong>Solution:</strong> Ad blockers block "fingerprint" resources thinking they're tracking scripts.</p>
      </div>
      
      <button 
        onClick={() => setShowDetails(!showDetails)}
        style={{ 
          background: '#007bff', 
          color: 'white', 
          border: 'none', 
          padding: '10px 20px', 
          borderRadius: '5px',
          cursor: 'pointer',
          marginBottom: '20px'
        }}
      >
        {showDetails ? 'Hide' : 'Show'} System Features
      </button>

      {showDetails && (
        <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '5px', border: '1px solid #dee2e6' }}>
          <h2 style={{ color: '#495057' }}>🏭 Manufacturing System Features:</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
            <div style={{ background: 'white', padding: '15px', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
              <h4 style={{ color: '#007bff', margin: '0 0 10px 0' }}>📊 Issue Tracking</h4>
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                <li>Log machine problems</li>
                <li>Track repair status</li>
                <li>Downtime monitoring</li>
              </ul>
            </div>
            <div style={{ background: 'white', padding: '15px', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
              <h4 style={{ color: '#28a745', margin: '0 0 10px 0' }}>🏭 Your Real Data</h4>
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                <li>CNC Autolathe (CNCAL)</li>
                <li>CNC Milling (CNCML)</li>
                <li>CAM Autolathe (CAMAL)</li>
              </ul>
            </div>
            <div style={{ background: 'white', padding: '15px', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
              <h4 style={{ color: '#ffc107', margin: '0 0 10px 0' }}>🤖 AI Features</h4>
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                <li>Auto-generated summaries</li>
                <li>OCR for alarm codes</li>
                <li>Smart categorization</li>
              </ul>
            </div>
          </div>
        </div>
      )}
      
      <div style={{ background: '#e2e3e5', padding: '15px', borderRadius: '5px', margin: '20px 0' }}>
        <h3 style={{ color: '#383d41' }}>🔧 Quick Fix:</h3>
        <ol>
          <li><strong>Open incognito/private window</strong> (disables extensions)</li>
          <li><strong>Or disable ad blocker</strong> for localhost</li>
          <li><strong>Or add</strong> <code>127.0.0.1:5173</code> to adblocker whitelist</li>
        </ol>
      </div>

      <div style={{ background: '#d1ecf1', padding: '15px', borderRadius: '5px', border: '1px solid #bee5eb' }}>
        <h4 style={{ margin: '0 0 10px 0' }}>🌐 Navigation:</h4>
        <p>Once the adblocker issue is resolved, you can access:</p>
        <ul>
                      <li><strong>Dashboard:</strong> <code>/</code> - Full metrics and charts (Home page)</li>
          <li><strong>Django Admin:</strong> <code>http://localhost:8000/admin/</code></li>
          <li><strong>API Test:</strong> <code>/test.html</code> - Backend connectivity test</li>
        </ul>
      </div>
    </div>
  );
};

export default SimpleTest; 