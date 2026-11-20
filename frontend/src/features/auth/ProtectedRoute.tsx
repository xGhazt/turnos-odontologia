import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { FullPageSpinner } from '../../components/ui/Spinner';
import { ForbiddenView } from '../../pages/ForbiddenView';
import type { Role } from '../../lib/rbac';

interface ProtectedRouteProps {
  allowedRoles?: readonly Role[];
}

export function ProtectedRoute({ allowedRoles }: ProtectedRouteProps) {
  const { status, user, expired } = useAuth();
  const location = useLocation();

  if (status === 'checking') {
    return <FullPageSpinner label="Verificando sesión…" />;
  }

  if (status === 'unauthenticated') {
    const target = expired ? '/login?motivo=sesion-expirada' : '/login';
    return <Navigate to={target} replace state={{ from: location }} />;
  }

  if (allowedRoles && !user?.roles.some((role) => allowedRoles.includes(role))) {
    return <ForbiddenView />;
  }

  return <Outlet />;
}
