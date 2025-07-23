import React from 'react';

const ClearCache: React.FC = () => {
  const handleClearCache = () => {
    // Clear all localStorage
    localStorage.clear();
    
    // Clear sessionStorage
    sessionStorage.clear();
    
    // Clear any cached API data
    if ('caches' in window) {
      caches.keys().then(names => {
        names.forEach(name => {
          caches.delete(name);
        });
      });
    }
    
    // Force reload
    window.location.reload();
  };

  const handleForceLogout = () => {
    // Clear everything
    localStorage.clear();
    sessionStorage.clear();
    
    // Redirect to login
    window.location.href = '/login';
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className="bg-red-600 text-white p-2 rounded-lg shadow-lg">
        <div className="text-xs mb-2">Debug Tools</div>
        <button
          onClick={handleClearCache}
          className="block w-full text-left px-2 py-1 text-xs bg-red-700 hover:bg-red-800 rounded mb-1"
        >
          Clear Cache & Reload
        </button>
        <button
          onClick={handleForceLogout}
          className="block w-full text-left px-2 py-1 text-xs bg-red-700 hover:bg-red-800 rounded"
        >
          Force Logout
        </button>
      </div>
    </div>
  );
};

export default ClearCache;