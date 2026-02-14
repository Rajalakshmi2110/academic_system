import React, { useState, useEffect } from 'react';
import { Box, Button, Paper, Typography, List, ListItem, ListItemText, IconButton, Alert, LinearProgress, Card, CardContent, Grid } from '@mui/material';
import { CloudUpload, Delete, Refresh, Logout, Description } from '@mui/icons-material';
import axios from 'axios';

const AdminDashboard = ({ onLogout }) => {
  const [pdfs, setPdfs] = useState([]);
  const [stats, setStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadPdfs();
    loadStats();
  }, []);

  const loadPdfs = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/admin/list-pdfs');
      setPdfs(res.data.pdfs);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load PDFs' });
    }
  };

  const loadStats = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/admin/stats');
      setStats(res.data);
    } catch (err) {
      console.error('Failed to load stats');
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post('http://localhost:5000/api/admin/upload-pdf', formData);
      setMessage({ type: 'success', text: `${file.name} uploaded successfully` });
      loadPdfs();
      loadStats();
    } catch (err) {
      setMessage({ type: 'error', text: 'Upload failed' });
    }
    setUploading(false);
  };

  const handleDelete = async (filename) => {
    if (!window.confirm(`Delete ${filename}?`)) return;

    try {
      await axios.delete(`http://localhost:5000/api/admin/delete-pdf/${filename}`);
      setMessage({ type: 'success', text: `${filename} deleted` });
      loadPdfs();
      loadStats();
    } catch (err) {
      setMessage({ type: 'error', text: 'Delete failed' });
    }
  };

  const handleRebuild = async () => {
    if (!window.confirm('Rebuild vector database? This may take 1-2 minutes.')) return;

    setRebuilding(true);
    setMessage(null);

    try {
      const res = await axios.post('http://localhost:5000/api/admin/rebuild-vector-db');
      setMessage({ type: 'success', text: 'Vector database rebuilt successfully' });
      loadStats();
    } catch (err) {
      setMessage({ type: 'error', text: 'Rebuild failed' });
    }
    setRebuilding(false);
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F5F5F5' }}>
      <Box sx={{ bgcolor: '#1976D2', color: 'white', p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">Admin Dashboard</Typography>
        <Button startIcon={<Logout />} onClick={onLogout} sx={{ color: 'white' }}>Logout</Button>
      </Box>

      <Box sx={{ p: 3 }}>
        {message && <Alert severity={message.type} sx={{ mb: 2 }}>{message.text}</Alert>}

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6">PDFs Uploaded</Typography>
                <Typography variant="h3">{stats?.pdfs_uploaded || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6">Vector Chunks</Typography>
                <Typography variant="h3">{stats?.vector_chunks || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6">Actions</Typography>
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                  <Button
                    variant="contained"
                    component="label"
                    startIcon={<CloudUpload />}
                    disabled={uploading}
                    size="small"
                  >
                    Upload
                    <input type="file" hidden accept=".pdf" onChange={handleUpload} />
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Refresh />}
                    onClick={handleRebuild}
                    disabled={rebuilding}
                    size="small"
                  >
                    Rebuild DB
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {(uploading || rebuilding) && <LinearProgress sx={{ mb: 2 }} />}

        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Uploaded Class Notes</Typography>
          {pdfs.length === 0 ? (
            <Typography color="textSecondary">No PDFs uploaded yet</Typography>
          ) : (
            <List>
              {pdfs.map((pdf) => (
                <ListItem
                  key={pdf.filename}
                  secondaryAction={
                    <IconButton edge="end" onClick={() => handleDelete(pdf.filename)}>
                      <Delete />
                    </IconButton>
                  }
                >
                  <Description sx={{ mr: 2, color: '#1976D2' }} />
                  <ListItemText
                    primary={pdf.filename}
                    secondary={`${pdf.size_mb} MB • ${new Date(pdf.modified).toLocaleString()}`}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default AdminDashboard;
