import React, { useState } from 'react';
import { Box } from '@mui/material';
import AdminLogin from './AdminLogin';
import AdminDashboard from './AdminDashboard';
import MetricsPage from './MetricsPage';

const AdminPage = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);

  if (!isLoggedIn) {
    return <AdminLogin onLogin={() => setIsLoggedIn(true)} />;
  }

  return (
    <Box>
      {currentTab === 0 && <AdminDashboard onLogout={() => setIsLoggedIn(false)} onSwitchTab={setCurrentTab} />}
      {currentTab === 1 && <MetricsPage onSwitchTab={setCurrentTab} onLogout={() => setIsLoggedIn(false)} />}
    </Box>
  );
};

export default AdminPage;
