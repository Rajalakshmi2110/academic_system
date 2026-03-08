import React, { useState } from 'react';
import { Box, TextField, Button, Paper, Typography, Alert } from '@mui/material';
import { Lock } from '@mui/icons-material';
import axios from 'axios';

const AdminLogin = ({ onLogin }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    
    try {
      const res = await axios.post('http://localhost:5001/api/admin/login', { password });
      if (res.data.status === 'success') {
        onLogin();
      }
    } catch (err) {
      setError('Invalid password');
    }
    setLoading(false);
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#F5F5F5' }}>
      <Paper sx={{ p: 4, maxWidth: 400, width: '100%' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Lock sx={{ color: '#1976D2' }} />
            <Typography variant="h5">Admin Login</Typography>
          </Box>
          <Button
            size="small"
            onClick={() => window.location.href = '/'}
            sx={{ color: '#666' }}
          >
            Home
          </Button>
        </Box>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        <TextField
          fullWidth
          type="password"
          label="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
          sx={{ mb: 2 }}
        />
        
        <Button
          fullWidth
          variant="contained"
          onClick={handleLogin}
          disabled={loading || !password}
        >
          Login
        </Button>
      </Paper>
    </Box>
  );
};

export default AdminLogin;
