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

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
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
                <Route path="/users" element={<UsersPage />} />
                <Route path="/teams" element={<TeamsPage />} />
                <Route path="/projects" element={<ProjectsPage />} />
                <Route path="/sla/config" element={<SLAConfigPage />} />
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route path="/audit" element={<AuditLogPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
