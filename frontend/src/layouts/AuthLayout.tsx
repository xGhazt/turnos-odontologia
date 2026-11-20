import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../features/auth/AuthContext';
import { homeFor } from '../lib/rbac';
import { Brand } from '../components/ui/Brand';
import { FullPageSpinner } from '../components/ui/Spinner';

export function AuthLayout() {
  const { status, user } = useAuth();

  if (status === 'checking') {
    return <FullPageSpinner label="Verificando sesión…" />;
  }

  if (status === 'authenticated' && user) {
    return <Navigate to={homeFor(user.roles)} replace />;
  }

  return (
    <div className="min-h-screen bg-canvas">
      <div className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-4 py-10">
        <div className="mb-6">
          <Brand to="/login" />
        </div>
        <div className="rounded-xl border border-line bg-surface p-6 shadow-sm">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
