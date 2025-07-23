import React, { useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Sidebar from './Sidebar';
import Header from './Header';
import ClearCache from '../Debug/ClearCache';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar 
        sidebarOpen={sidebarOpen} 
        setSidebarOpen={setSidebarOpen}
        userRole={user?.role || 'tenant'}
      />
      
      <div className="lg:pl-64 flex flex-col flex-1">
        <Header 
          setSidebarOpen={setSidebarOpen}
          user={user}
        />
        
        <main className="flex-1 pb-8">
          <div className="bg-white shadow">
            <div className="px-4 sm:px-6 lg:max-w-6xl lg:mx-auto lg:px-8">
              <div className="py-6 md:flex md:items-center md:justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center">
                    <div>
                      <div className="flex items-center">
                        <h1 className="ml-3 text-2xl font-bold leading-7 text-gray-900 sm:leading-9 sm:truncate">
                          {getPageTitle(location.pathname)}
                        </h1>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-8">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
              {children}
            </div>
          </div>
        </main>
      </div>
      
      {/* Debug tools - only show in development */}
      {process.env.NODE_ENV === 'development' && <ClearCache />}
    </div>
  );
};

function getPageTitle(pathname: string): string {
  const pathMap: { [key: string]: string } = {
    '/dashboard': 'Dashboard',
    '/properties': 'Properties',
    '/applications': 'Applications',
    '/leases': 'Leases',
    '/maintenance': 'Maintenance',
    '/payments': 'Payments',
    '/messages': 'Messages',
    '/admin': 'Admin',
    '/settings': 'Settings',
    '/profile': 'Profile'
  };
  
  return pathMap[pathname] || 'Dashboard';
}

export default DashboardLayout;