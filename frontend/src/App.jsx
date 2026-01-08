import { Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import ProjectSelector from './pages/ProjectSelector';
import WikiList from './pages/WikiList';
import WikiDetail from './pages/WikiDetail';

// Placeholder pages
const Placeholder = ({ title }) => (
  <div className="p-8 border border-dashed border-border rounded-xl flex items-center justify-center text-text-muted bg-surface">
    {title} - Coming Soon
  </div>
);

function App() {
  return (
    <Routes>
      {/* Gateway: Project Selection */}
      <Route path="/" element={<ProjectSelector />} />

      {/* World Context: All routes under a specific project */}
      <Route path="/project/:projectId" element={<AppLayout />}>
        {/* Redirect /project/:id to /project/:id/dashboard */}
        <Route index element={<Navigate to="dashboard" replace />} />

        <Route path="dashboard" element={<Dashboard />} />

        {/* Wiki List Route (e.g., wiki/characters) */}
        <Route path="wiki/:category" element={<WikiList />} />

        {/* Wiki Detail/Edit Route (e.g., wiki/characters/gabriel) */}
        <Route path="wiki/:category/:docSlug" element={<WikiDetail />} />

        <Route path="search" element={<Placeholder title="Search Interface" />} />
        <Route path="settings" element={<Placeholder title="Settings" />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
