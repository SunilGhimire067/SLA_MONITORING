import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/common/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import TicketsPage from './pages/TicketsPage';
import TicketDetailPage from './pages/TicketDetailPage';
import CreateTicketPage from './pages/CreateTicketPage';
import UsersPage from './pages/UsersPage';
import TeamsPage from './pages/TeamsPage';
import ProjectsPage from './pages/ProjectsPage';
import SLAConfigPage from './pages/SLAConfigPage';
import SLADashboardPage from './pages/SLADashboardPage';
import NotificationsPage from './pages/NotificationsPage';
import AuditLogPage from './pages/AuditLogPage';
import SettingsPage from './pages/SettingsPage';
import RolePermissionsPage from './pages/RolePermissionsPage';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const RoleRoute = ({ children, roles }: { children: React.ReactNode; roles: string[] }) => {
  const { hasRole } = useAuth();
  if (!hasRole(...roles)) return <Navigate to="/" replace />;
  return <>{children}</>;
};

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/dashboard/sla" element={<SLADashboardPage />} />
                <Route path="/tickets" element={<TicketsPage />} />
                <Route path="/tickets/new" element={<CreateTicketPage />} />
                <Route path="/tickets/:id" element={<TicketDetailPage />} />
                <Route path="/users" element={<RoleRoute roles={['admin']}><UsersPage /></RoleRoute>} />
                <Route path="/teams" element={<RoleRoute roles={['admin', 'manager']}><TeamsPage /></RoleRoute>} />
                <Route path="/projects" element={<RoleRoute roles={['admin', 'manager']}><ProjectsPage /></RoleRoute>} />
                <Route path="/sla/config" element={<RoleRoute roles={['admin', 'manager']}><SLAConfigPage /></RoleRoute>} />
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route path="/audit" element={<RoleRoute roles={['admin', 'manager']}><AuditLogPage /></RoleRoute>} />
                <Route path="/roles" element={<RoleRoute roles={['admin']}><RolePermissionsPage /></RoleRoute>} />
                <Route path="/settings" element={<RoleRoute roles={['admin', 'manager']}><SettingsPage /></RoleRoute>} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
