import { useAuth } from '../contexts/AuthContext';

export const usePermissions = () => {
  const { hasPermission, hasAnyPermission, hasAllPermissions, user, isAuthenticated, isPublic } = useAuth();

  return {
    // Direct permission checking methods
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    
    // User state
    user,
    isAuthenticated,
    isPublic,
    
    // Specific permission checkers for common actions
    canViewDashboard: () => hasPermission('view_dashboard'),
    canCRUDIssues: () => hasPermission('crud_issues'),
    canCRUDRemedies: () => hasPermission('crud_remedies'),
    canMarkResolved: () => hasPermission('mark_resolved'),
    canConfigureLimits: () => hasPermission('configure_limits'),
    canManageUsers: () => hasPermission('manage_users'),
    canViewCosts: () => hasPermission('view_costs'),
    canViewExternalContacts: () => hasPermission('view_external_contacts'),
    canGenerateReports: () => hasPermission('generate_reports'),
    
    // Role-based checks
    isAdmin: () => user?.role?.role === 'admin',
    isManagement: () => user?.role?.role === 'management',
    isExecutive: () => user?.role?.role === 'executive',
    isTechnician: () => user?.role?.role === 'technician',
    isOperator: () => user?.role?.role === 'operator',
    
    // Combined permission checks for common scenarios
    canAccessSettings: () => hasAnyPermission(['configure_limits', 'manage_users']),
    canModifyIssues: () => hasPermission('crud_issues') && isAuthenticated,
    canModifyRemedies: () => hasPermission('crud_remedies') && isAuthenticated,
    
    // Public access checks (for components that allow public users)
    canCreateIssues: () => {
      // Both authenticated users with permission and public users can create issues
      return isPublic || (isAuthenticated && hasPermission('crud_issues'));
    },
    
    canCreateRemedies: () => {
      // Both authenticated users with permission and public users can create remedies
      return isPublic || (isAuthenticated && hasPermission('crud_remedies'));
    },
    
    canViewIssues: () => {
      // Issues are publicly viewable
      return true;
    },
    
    canViewRemedies: () => {
      // Remedies are publicly viewable (but with filtered data for public users)
      return true;
    },
    
    // UI-specific permission checks
    shouldShowCosts: () => {
      return isAuthenticated && (hasPermission('view_costs') || user?.role?.can_view_costs);
    },
    
    shouldShowExternalContacts: () => {
      return isAuthenticated && (hasPermission('view_external_contacts') || user?.role?.can_view_external_contacts);
    },
    
    // Get current user role information
    getCurrentRole: () => user?.role?.role || null,
    getCurrentRoleName: () => user?.role?.role_name || 'Public User',
    getAllPermissions: () => user?.role?.permissions || [],
  };
}; 