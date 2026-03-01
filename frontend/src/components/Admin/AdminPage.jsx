import React, { useState } from 'react';
import { Box } from '@mui/material';
import AdminLogin from './AdminLogin';
import AdminHome from './AdminHome';
import AdminDashboard from './AdminDashboard';
import MetricsPage from './MetricsPage';
import AddSubjectPage from './AddSubjectPage';

const AdminPage = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [selectedSubject, setSelectedSubject] = useState(null);

  if (!isLoggedIn) {
    return <AdminLogin onLogin={() => setIsLoggedIn(true)} />;
  }

  const handleSelectSubject = (subjectId) => {
    setSelectedSubject(subjectId);
    setCurrentTab(3); // Switch to dashboard tab
  };

  return (
    <Box>
      {currentTab === 0 && <AdminHome onLogout={() => setIsLoggedIn(false)} onSwitchTab={setCurrentTab} onSelectSubject={handleSelectSubject} />}
      {currentTab === 1 && <MetricsPage onSwitchTab={setCurrentTab} onLogout={() => setIsLoggedIn(false)} selectedSubject={selectedSubject} />}
      {currentTab === 2 && <AddSubjectPage onSwitchTab={setCurrentTab} onLogout={() => setIsLoggedIn(false)} />}
      {currentTab === 3 && selectedSubject && <AdminDashboard onLogout={() => setIsLoggedIn(false)} onSwitchTab={setCurrentTab} initialSubject={selectedSubject} />}
    </Box>
  );
};

export default AdminPage;
