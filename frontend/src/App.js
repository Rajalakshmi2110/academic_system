import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ChatInterface from './components/Student/ChatInterface';
import StudentLanding from './components/Student/StudentLanding';
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
  const [showChat, setShowChat] = useState(false);

  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('admin') === 'true') {
      setIsAdmin(true);
    }
  }, []);

  if (isAdmin) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AdminPage />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {showChat ? <ChatInterface onBackToHome={() => setShowChat(false)} openSubjectModal={true} /> : <StudentLanding onGetStarted={() => setShowChat(true)} />}
    </ThemeProvider>
  );
}

export default App;
