import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Box, Button } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import ChatInterface from './components/Student/ChatInterface';
import AdminPage from './components/Admin/AdminPage';

const theme = createTheme({
  palette: {
    primary: { main: '#1976D2' },
    success: { main: '#4CAF50' },
    warning: { main: '#FFC107' },
    error: { main: '#F44336' },
  },
});

function App() {
  const [isAdmin, setIsAdmin] = useState(false);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {isAdmin ? (
        <AdminPage />
      ) : (
        <>
          <Box sx={{ position: 'fixed', top: 10, right: 10, zIndex: 1000 }}>
            <Button
              variant="outlined"
              size="small"
              onClick={() => setIsAdmin(true)}
              sx={{ bgcolor: 'white' }}
            >
              Admin
            </Button>
          </Box>
          <ChatInterface />
        </>
      )}
    </ThemeProvider>
  );
}

export default App;
