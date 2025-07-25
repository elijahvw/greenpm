import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import DashboardLayout from './components/Dashboard/DashboardLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Properties from './pages/Properties';
import CreateProperty from './pages/CreateProperty';
import Tenants from './pages/Tenants';
import Leases from './pages/Leases';
import CreateLease from './pages/CreateLease';

import Accounting from './pages/Accounting';
import Applications from './pages/Applications';
import Maintenance from './pages/Maintenance';
import Messages from './pages/Messages';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import Profile from './pages/Profile';
import TenantDashboard from './pages/TenantDashboard';
import MyLease from './pages/tenant/MyLease';
import RentPayments from './pages/tenant/RentPayments';
import PaymentHistory from './pages/tenant/PaymentHistory';
import './App.css';

// Role-based dashboard component
const RoleDashboard: React.FC = () => {
  const { user } = useAuth();
  
  if (user?.role === 'tenant') {
    return <TenantDashboard />;
  }
  
  return <Dashboard />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Toaster position="top-right" />
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Protected routes with dashboard layout */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardLayout />}>
              <Route index element={<RoleDashboard />} />
              <Route path="rentals" element={<Properties />} />
              <Route path="properties" element={<Properties />} />
              <Route path="properties/create" element={<CreateProperty />} />
              <Route path="tenants" element={<Tenants />} />
              <Route path="leases" element={<Leases />} />
              <Route path="leases/create" element={<CreateLease />} />
              <Route path="leasing" element={<Leases />} />

              <Route path="associations" element={<div>Associations coming soon...</div>} />
              <Route path="accounting" element={<Accounting />} />
              <Route path="maintenance" element={<Maintenance />} />
              <Route path="tasks" element={<div>Tasks coming soon...</div>} />
              <Route path="communication" element={<Messages />} />
              <Route path="files" element={<div>Files coming soon...</div>} />
              <Route path="reports" element={<Reports />} />
              <Route path="analytics" element={<Reports />} />
              <Route path="addons" element={<div>Add-ons coming soon...</div>} />
              <Route path="settings" element={<Settings />} />
              
              {/* Tenant-specific routes */}
              <Route path="lease" element={<MyLease />} />
              <Route path="payments" element={<RentPayments />} />
              <Route path="payment-history" element={<PaymentHistory />} />
              <Route path="profile" element={<Profile />} />
            </Route>
            
            {/* Legacy routes for compatibility */}
            <Route path="/properties" element={<Navigate to="/dashboard/properties" replace />} />
            <Route path="/applications" element={<Navigate to="/dashboard/leasing" replace />} />
            <Route path="/maintenance" element={<Navigate to="/dashboard/maintenance" replace />} />
            <Route path="/messages" element={<Navigate to="/dashboard/communication" replace />} />
            <Route path="/settings" element={<Navigate to="/dashboard/settings" replace />} />
            <Route path="/profile" element={<Navigate to="/dashboard/settings" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;