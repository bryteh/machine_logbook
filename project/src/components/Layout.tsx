import React, { useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { 
  Home, 
  List, 
  Plus, 
  Wrench,
  Menu,
  X,
  Settings,
  LogIn,
  LogOut,
  User,
  Shield
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import PermissionGate from './PermissionGate';

const Layout: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { user, logout, loading } = useAuth();
  const { 
    canViewDashboard, 
    canCreateIssues, 
    canAccessSettings,
    getCurrentRoleName,
    isAuthenticated,
    isPublic
  } = usePermissions();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Show loading while checking auth
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Dynamic navigation based on permissions
  const navigation = [
    ...(canViewDashboard() ? [{ name: 'Dashboard', href: '/', icon: Home }] : []),
    { name: 'Issues', href: '/issues', icon: List },
    ...(canCreateIssues() ? [{ name: 'New Issue', href: '/issues/new', icon: Plus }] : []),
  ];

  const isActive = (path: string) => {
    if (path === '/') {
    return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile menu button */}
      <div className="lg:hidden bg-white shadow-sm border-b border-gray-200">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-2">
            <Wrench className="h-8 w-8 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-900">Erabase Logbook</h1>
          </div>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
          >
            {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile menu overlay */}
      {isMobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 z-50 bg-gray-600 bg-opacity-75">
          <div className="fixed inset-y-0 left-0 flex flex-col w-64 bg-white shadow-xl">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <Wrench className="h-8 w-8 text-blue-600" />
                <h1 className="text-xl font-bold text-gray-900">Erabase</h1>
              </div>
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="p-2 rounded-md text-gray-600 hover:text-gray-900"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <nav className="flex-1 px-4 py-4 space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive(item.href)
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* Bottom section with Settings and Auth */}
            <div className="px-4 pb-4 space-y-2">
              <PermissionGate permissions={['configure_limits', 'manage_users']}>
                <Link
                  to="/settings"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive('/settings')
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Settings className="h-5 w-5" />
                  <span>Settings</span>
                </Link>
              </PermissionGate>
              
              {isAuthenticated ? (
                <div className="border-t border-gray-200 pt-2 mt-2">
                  <div className="px-3 py-2 text-xs">
                    <div className="flex items-center space-x-2">
                      <Shield className="h-3 w-3 text-blue-500" />
                      <span className="text-gray-500">{getCurrentRoleName()}</span>
                    </div>
                    <div className="text-gray-700 font-medium">
                      Hi, {user?.first_name && user?.last_name 
                        ? `${user.first_name} ${user.last_name}` 
                        : user?.username}
                    </div>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 w-full text-left transition-colors"
                  >
                    <LogOut className="h-5 w-5" />
                    <span>Logout</span>
                  </button>
                </div>
              ) : (
                <div className="border-t border-gray-200 pt-2 mt-2">
                  <div className="px-3 py-2 text-xs">
                    <div className="flex items-center space-x-2">
                      <User className="h-3 w-3 text-gray-400" />
                      <span className="text-gray-500">Public User</span>
                    </div>
                    <div className="text-gray-600 text-xs">Limited access</div>
                  </div>
                  <Link
                    to="/login"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive('/login')
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <LogIn className="h-5 w-5" />
                    <span>Login</span>
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="lg:flex">
        {/* Desktop sidebar */}
        <div className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0">
          <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
            <div className="flex items-center px-6 py-4 border-b border-gray-200">
              <Wrench className="h-8 w-8 text-blue-600" />
              <h1 className="ml-3 text-xl font-bold text-gray-900">Erabase Logbook</h1>
            </div>
            <nav className="flex-1 px-4 py-4 space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive(item.href)
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>
            
            {/* Bottom section with Settings and User Info */}
            <div className="px-4 py-4 border-t border-gray-200 space-y-2">
              <PermissionGate permissions={['configure_limits', 'manage_users']}>
                <Link
                  to="/settings"
                  className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive('/settings')
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Settings className="h-5 w-5" />
                  <span>Settings</span>
                </Link>
              </PermissionGate>

              {isAuthenticated ? (
                <div className="mt-2">
                  <div className="px-3 py-2 text-xs">
                    <div className="flex items-center space-x-2">
                      <Shield className="h-3 w-3 text-blue-500" />
                      <span className="text-gray-500">{getCurrentRoleName()}</span>
                    </div>
                    <div className="text-gray-700 font-medium">
                      Hi, {user?.first_name && user?.last_name 
                        ? `${user.first_name} ${user.last_name}` 
                        : user?.username}
                    </div>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 w-full text-left transition-colors"
                  >
                    <LogOut className="h-5 w-5" />
                    <span>Logout</span>
                  </button>
                </div>
              ) : (
                <div className="mt-2">
                  <div className="px-3 py-2 text-xs">
                    <div className="flex items-center space-x-2">
                      <User className="h-3 w-3 text-gray-400" />
                      <span className="text-gray-500">Public User</span>
                    </div>
                    <div className="text-gray-600 text-xs">Limited access</div>
                  </div>
                  <Link
                    to="/login"
                    className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive('/login')
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <LogIn className="h-5 w-5" />
                    <span>Login</span>
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="lg:pl-64 flex-1">
          <main className="flex-1">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};

export default Layout;