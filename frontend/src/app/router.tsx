import { createBrowserRouter, Navigate, type RouteObject } from 'react-router-dom';
import { AuthLayout } from '../layouts/AuthLayout';
import { PublicLayout } from '../layouts/PublicLayout';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { ProtectedRoute } from '../features/auth/ProtectedRoute';
import { LoginPage } from '../features/auth/pages/LoginPage';
import { RegisterPage } from '../features/auth/pages/RegisterPage';
import { useAuth } from '../features/auth/AuthContext';
import { APP_ROUTES, homeFor } from '../lib/rbac';
import { FullPageSpinner } from '../components/ui/Spinner';
import { ModulePlaceholder } from '../pages/ModulePlaceholder';
import { NotFoundPage } from '../pages/NotFoundPage';

function HomeRedirect() {
  const { status, user } = useAuth();

  if (status === 'checking') {
    return <FullPageSpinner label="Verificando sesión…" />;
  }
  if (status === 'authenticated' && user) {
    return <Navigate to={homeFor(user.roles)} replace />;
  }
  return <Navigate to="/login" replace />;
}

/** Cada módulo sin backend se protege por rol y muestra un marcador de posición. */
const moduleRoutes: RouteObject[] = APP_ROUTES.map((route) => ({
  element: <ProtectedRoute allowedRoles={route.roles} />,
  children: [
    {
      path: route.path,
      element: <ModulePlaceholder title={route.label} change={route.change} />,
    },
  ],
}));

export const routes: RouteObject[] = [
  { path: '/', element: <HomeRedirect /> },
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/registro', element: <RegisterPage /> },
    ],
  },
  {
    element: <PublicLayout />,
    children: [
      {
        path: '/reservar-turno',
        element: <ModulePlaceholder title="Reservar turno" change="C-11" />,
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [{ element: <DashboardLayout />, children: moduleRoutes }],
  },
  { path: '*', element: <NotFoundPage /> },
];

export function createAppRouter() {
  return createBrowserRouter(routes);
}
