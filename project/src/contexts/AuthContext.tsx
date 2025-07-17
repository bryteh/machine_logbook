import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { auth } from '../services/api';

export interface UserRole {
  role: string;
  role_name: string;
  permissions: string[];
  can_view_costs: boolean;
  can_view_external_contacts: boolean;
}

export interface User {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
  role?: UserRole;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<User | null>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
  isPublic: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const checkAuthStatus = async () => {
    try {
      console.log('AuthContext: Checking auth status...');
      const response = await auth.getCurrentUser();
      // getCurrentUser returns user data directly in response.data
      console.log('AuthContext: Auth status check successful - user data:', response.data);
      setUser(response.data);
      setIsAuthenticated(true);
      return response.data;
    } catch (error: any) {
      console.log('AuthContext: Auth status check failed:', error.response?.status, error.message);
      
      // Only clear user state for actual authentication failures
      if (error.response?.status === 401 || error.response?.status === 403) {
        console.log('AuthContext: Authentication failed - clearing user state');
        setUser(null);
        setIsAuthenticated(false);
      } else {
        console.log('AuthContext: Network error - keeping current user state');
      }
      return null;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Only check auth status if we're not on the login page
    const isLoginPage = window.location.pathname === '/login';
    
    if (!isLoginPage) {
      console.log('AuthContext: Running initial auth status check');
      checkAuthStatus();
    } else {
      console.log('AuthContext: Skipping auth check on login page');
      setLoading(false);
    }
  }, []);

  const login = async (username: string, password: string): Promise<User | null> => {
    try {
      setLoading(true);
      console.log('AuthContext: Starting login process...');
      
      const response = await auth.login(username, password);
      // Login returns user data wrapped in 'user' key
      const userData = response.data.user;
      
      console.log('AuthContext: Login successful, setting user data:', userData);
      setUser(userData);
      setIsAuthenticated(true);
      
      // Small delay to ensure state is fully updated before navigation
      await new Promise(resolve => setTimeout(resolve, 100));
      
      console.log('AuthContext: Login complete, user state updated');
      return userData;
    } catch (error: any) {
      console.error('AuthContext: Login failed:', error.response?.data || error.message);
      setUser(null);
      setIsAuthenticated(false);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      setLoading(true);
      console.log('AuthContext: Starting logout process...');
      
      await auth.logout();
      
      console.log('AuthContext: Logout successful, clearing user state');
      setUser(null);
      setIsAuthenticated(false);
    } catch (error: any) {
      console.error('AuthContext: Logout failed:', error.response?.data || error.message);
      // Clear state anyway since logout intent is clear
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const refreshUser = async (): Promise<void> => {
    try {
      console.log('AuthContext: Refreshing user data...');
      const response = await auth.getCurrentUser();
      // getCurrentUser returns user data directly in response.data
      const userData = response.data;
      
      console.log('AuthContext: User refresh successful:', userData);
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error: any) {
      console.error('AuthContext: User refresh failed:', error.response?.status, error.response?.data);
      
      // Only clear auth state if it's a 401 (unauthorized)
      if (error.response?.status === 401) {
        console.log('AuthContext: User not authenticated, clearing state');
        setUser(null);
        setIsAuthenticated(false);
      }
      // For other errors (network, server), keep existing state
    }
  };

  const hasPermission = (permission: string): boolean => {
    if (!user || !user.role) {
      return false;
    }
    return user.role.permissions.includes(permission);
  };

  const hasAnyPermission = (permissions: string[]): boolean => {
    if (!user || !user.role) {
      return false;
    }
    return permissions.some(permission => user.role!.permissions.includes(permission));
  };

  const hasAllPermissions = (permissions: string[]): boolean => {
    if (!user || !user.role) {
      return false;
    }
    return permissions.every(permission => user.role!.permissions.includes(permission));
  };

  const isPublic = !user;

  console.log('AuthContext: Current state - user:', user, 'loading:', loading, 'isAuthenticated:', isAuthenticated);

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    refreshUser,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isPublic,
    isAuthenticated,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 