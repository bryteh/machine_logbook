import React, { ReactNode } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface PermissionGateProps {
  permission?: string;
  permissions?: string[];
  requireAll?: boolean; // If true, user must have ALL permissions; if false, user needs ANY permission
  children: ReactNode;
  fallback?: ReactNode;
  requireAuth?: boolean; // If true, requires authentication regardless of permissions
  allowPublic?: boolean; // If true, allows public (unauthenticated) users
}

const PermissionGate: React.FC<PermissionGateProps> = ({
  permission,
  permissions = [],
  requireAll = false,
  children,
  fallback = null,
  requireAuth = false,
  allowPublic = false,
}) => {
  const { hasPermission, hasAnyPermission, hasAllPermissions, isAuthenticated, isPublic } = useAuth();

  // If public users are explicitly allowed and user is public
  if (allowPublic && isPublic) {
    return <>{children}</>;
  }

  // If authentication is required and user is not authenticated
  if (requireAuth && !isAuthenticated) {
    return <>{fallback}</>;
  }

  // If no permissions are specified, just check authentication requirements
  if (!permission && permissions.length === 0) {
    if (requireAuth && !isAuthenticated) {
      return <>{fallback}</>;
    }
    return <>{children}</>;
  }

  // Check single permission
  if (permission) {
    const hasAccess = isAuthenticated && hasPermission(permission);
    return hasAccess ? <>{children}</> : <>{fallback}</>;
  }

  // Check multiple permissions
  if (permissions.length > 0) {
    let hasAccess = false;
    
    if (isAuthenticated) {
      if (requireAll) {
        hasAccess = hasAllPermissions(permissions);
      } else {
        hasAccess = hasAnyPermission(permissions);
      }
    }
    
    return hasAccess ? <>{children}</> : <>{fallback}</>;
  }

  // Default: render children
  return <>{children}</>;
};

export default PermissionGate; 