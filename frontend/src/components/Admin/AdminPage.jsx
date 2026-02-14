import React, { useState } from 'react';
import { Box, Tabs, Tab } from '@mui/material';
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
      <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: '#1976D2' }}>
        <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)} sx={{ '& .MuiTab-root': { color: 'white' }, '& .Mui-selected': { color: 'white !important' } }}>
          <Tab label="Dashboard" />
          <Tab label="Metrics" />
        </Tabs>
      </Box>
      {currentTab === 0 && <AdminDashboard onLogout={() => setIsLoggedIn(false)} />}
      {currentTab === 1 && <MetricsPage />}
    </Box>
  );
};

export default AdminPage;
