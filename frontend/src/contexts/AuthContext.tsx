import React, { createContext, useState, useContext, useEffect } from 'react';
import { api } from '../services/api';

interface User {
  id: number;
  uuid: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  status: string;
  phone?: string;
  avatar_url?: string;
  bio?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  email_verified: boolean;
  phone_verified: boolean;
  identity_verified: boolean;
  two_factor_enabled: boolean;
  notification_email: boolean;
  notification_sms: boolean;
  notification_push: boolean;
  created_at: string;
  updated_at?: string;
  last_login?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (userData: any) => Promise<void>;
  updateProfile: (userData: any) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('🔍 AuthContext: Checking token...', token ? 'Token exists' : 'No token');
    if (token) {
      validateToken();
    } else {
      setLoading(false);
    }
  }, [token]); // eslint-disable-line react-hooks/exhaustive-deps

  const validateToken = async () => {
    try {
      console.log('🔍 AuthContext: Validating token with /auth/me...');
      const response = await api.get('/auth/me');
      console.log('✅ AuthContext: Token valid, user:', response.data);
      setUser(response.data);
      setLoading(false);
    } catch (error) {
      console.error('❌ AuthContext: Token validation failed:', error);
      logout();
    }
  };

  const login = async (email: string, password: string) => {
    try {
      console.log('🔐 AuthContext: Attempting login with email:', email);
      const response = await api.post('/auth/login', { email, password });
      console.log('🔐 AuthContext: Login response:', response.data);
      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      
      // Set default authorization header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      console.log('✅ AuthContext: Login successful, user set:', userData);
    } catch (error: any) {
      console.error('❌ AuthContext: Login failed:', error);
      console.error('❌ AuthContext: Error response:', error.response?.data);
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const register = async (userData: any) => {
    try {
      const response = await api.post('/auth/register', userData);
      const { access_token, user: newUser } = response.data;
      
      setToken(access_token);
      setUser(newUser);
      localStorage.setItem('token', access_token);
      
      // Set default authorization header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  };

  const logout = async () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.clear(); // Clear all localStorage
    delete api.defaults.headers.common['Authorization'];
    
    // Force redirect to login
    window.location.href = '/login';
  };

  const updateProfile = async (userData: any) => {
    try {
      const response = await api.put('/users/profile', userData);
      setUser(response.data);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Profile update failed');
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    loading,
    login,
    logout,
    register,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};