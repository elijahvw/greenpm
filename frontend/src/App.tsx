import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Provider } from 'react-redux';
import { Toaster } from 'react-hot-toast';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';

import { store } from './store/store';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { PublicRoute } from './components/auth/PublicRoute';

// Layouts
import { PublicLayout } from './layouts/PublicLayout';
import { DashboardLayout } from './layouts/DashboardLayout';

// Public Pages
import { HomePage } from './pages/public/HomePage';
import { PropertiesPage } from './pages/public/PropertiesPage';
import { PropertyDetailPage } from './pages/public/PropertyDetailPage';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { ForgotPasswordPage } from './pages/auth/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/auth/ResetPasswordPage';

// Dashboard Pages
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { PropertiesListPage } from './pages/dashboard/PropertiesListPage';
import { PropertyCreatePage } from './pages/dashboard/PropertyCreatePage';
import { PropertyEditPage } from './pages/dashboard/PropertyEditPage';
import { LeasesPage } from './pages/dashboard/LeasesPage';
import { LeaseDetailPage } from './pages/dashboard/LeaseDetailPage';
import { PaymentsPage } from './pages/dashboard/PaymentsPage';
import { MaintenancePage } from './pages/dashboard/MaintenancePage';
import { MessagesPage } from './pages/dashboard/MessagesPage';
import { ApplicationsPage } from './pages/dashboard/ApplicationsPage';
import { ProfilePage } from './pages/dashboard/ProfilePage';
import { SettingsPage } from './pages/dashboard/SettingsPage';

// Admin Pages
import { AdminDashboardPage } from './pages/admin/AdminDashboardPage';
import { AdminUsersPage } from './pages/admin/AdminUsersPage';
import { AdminPropertiesPage } from './pages/admin/AdminPropertiesPage';
import { AdminAnalyticsPage } from './pages/admin/AdminAnalyticsPage';

// Error Pages
import { NotFoundPage } from './pages/errors/NotFoundPage';
import { ErrorBoundary } from './components/common/ErrorBoundary';

// Initialize Stripe
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || '');

// Initialize React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          <Elements stripe={stripePromise}>
            <AuthProvider>
              <Router>
                <div className="App">
                  <Routes>
                    {/* Public Routes */}
                    <Route path="/" element={<PublicLayout />}>
                      <Route index element={<HomePage />} />
                      <Route path="properties" element={<PropertiesPage />} />
                      <Route path="properties/:id" element={<PropertyDetailPage />} />
                    </Route>

                    {/* Auth Routes */}
                    <Route path="/auth" element={<PublicRoute />}>
                      <Route path="login" element={<LoginPage />} />
                      <Route path="register" element={<RegisterPage />} />
                      <Route path="forgot-password" element={<ForgotPasswordPage />} />
                      <Route path="reset-password" element={<ResetPasswordPage />} />
                    </Route>

                    {/* Dashboard Routes */}
                    <Route path="/dashboard" element={
                      <ProtectedRoute>
                        <DashboardLayout />
                      </ProtectedRoute>
                    }>
                      <Route index element={<DashboardPage />} />
                      
                      {/* Properties */}
                      <Route path="properties" element={<PropertiesListPage />} />
                      <Route path="properties/new" element={<PropertyCreatePage />} />
                      <Route path="properties/:id/edit" element={<PropertyEditPage />} />
                      
                      {/* Leases */}
                      <Route path="leases" element={<LeasesPage />} />
                      <Route path="leases/:id" element={<LeaseDetailPage />} />
                      
                      {/* Payments */}
                      <Route path="payments" element={<PaymentsPage />} />
                      
                      {/* Maintenance */}
                      <Route path="maintenance" element={<MaintenancePage />} />
                      
                      {/* Messages */}
                      <Route path="messages" element={<MessagesPage />} />
                      
                      {/* Applications */}
                      <Route path="applications" element={<ApplicationsPage />} />
                      
                      {/* Profile & Settings */}
                      <Route path="profile" element={<ProfilePage />} />
                      <Route path="settings" element={<SettingsPage />} />
                    </Route>

                    {/* Admin Routes */}
                    <Route path="/admin" element={
                      <ProtectedRoute requiredRole="admin">
                        <DashboardLayout />
                      </ProtectedRoute>
                    }>
                      <Route index element={<AdminDashboardPage />} />
                      <Route path="users" element={<AdminUsersPage />} />
                      <Route path="properties" element={<AdminPropertiesPage />} />
                      <Route path="analytics" element={<AdminAnalyticsPage />} />
                    </Route>

                    {/* Redirects */}
                    <Route path="/login" element={<Navigate to="/auth/login" replace />} />
                    <Route path="/register" element={<Navigate to="/auth/register" replace />} />

                    {/* 404 */}
                    <Route path="*" element={<NotFoundPage />} />
                  </Routes>

                  {/* Global Toast Notifications */}
                  <Toaster
                    position="top-right"
                    toastOptions={{
                      duration: 4000,
                      style: {
                        background: '#363636',
                        color: '#fff',
                      },
                      success: {
                        style: {
                          background: '#22c55e',
                        },
                      },
                      error: {
                        style: {
                          background: '#ef4444',
                        },
                      },
                    }}
                  />
                </div>
              </Router>
            </AuthProvider>
          </Elements>
        </QueryClientProvider>
      </Provider>
    </ErrorBoundary>
  );
}

export default App;