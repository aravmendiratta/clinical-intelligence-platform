// frontend/src/App.tsx
import React, { useState } from 'react';
import { AuthContext, useAuthProvider } from './hooks/useAuth';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import ChatPage from './pages/ChatPage';
import UploadPage from './pages/UploadPage';
import SearchPage from './pages/SearchPage';
import AuditPage from './pages/AuditPage';

const AppContent: React.FC = () => {
  const [activePage, setActivePage] = useState('dashboard');

  return (
    <div style={{ display: 'flex', width: '100%', minHeight: '100vh' }}>
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      <main style={{ flex: 1, overflow: 'auto', minHeight: '100vh' }}>
        {activePage === 'dashboard' && <DashboardPage onNavigate={setActivePage} />}
        {activePage === 'chat' && <ChatPage />}
        {activePage === 'upload' && <UploadPage onNavigate={setActivePage} />}
        {activePage === 'search' && <SearchPage />}
        {activePage === 'audit' && <AuditPage />}
      </main>
    </div>
  );
};

const App: React.FC = () => {
  const auth = useAuthProvider();

  return (
    <AuthContext.Provider value={auth}>
      <AppContent />
    </AuthContext.Provider>
  );
};

export default App;
