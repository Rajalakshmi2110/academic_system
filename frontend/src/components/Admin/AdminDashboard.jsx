import React, { useState, useEffect } from 'react';
import { Box, Button, Paper, Typography, List, ListItem, ListItemText, IconButton, Alert, LinearProgress, Card, CardContent, Grid, TextField, Accordion, AccordionSummary, AccordionDetails, Chip } from '@mui/material';
import { CloudUpload, Delete, Refresh, Logout, Description, ExpandMore, Folder } from '@mui/icons-material';
import axios from 'axios';

const AdminDashboard = ({ onLogout }) => {
  const [folders, setFolders] = useState({});
  const [stats, setStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [message, setMessage] = useState(null);
  const [folderName, setFolderName] = useState('');

  useEffect(() => {
    loadPdfs();
    loadStats();
  }, []);

  const loadPdfs = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/admin/list-pdfs');
      setFolders(res.data.folders);
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
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setMessage(null);

    try {
      for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);
        if (folderName) formData.append('folder', folderName);
        await axios.post('http://localhost:5000/api/admin/upload-pdf', formData);
      }
      setMessage({ type: 'success', text: `${files.length} file(s) uploaded` });
      setFolderName('');
      loadPdfs();
      loadStats();
    } catch (err) {
      setMessage({ type: 'error', text: 'Upload failed' });
    }
    setUploading(false);
  };

  const handleDelete = async (path) => {
    if (!window.confirm(`Delete ${path}?`)) return;

    try {
      await axios.delete('http://localhost:5000/api/admin/delete-pdf', { data: { path } });
      setMessage({ type: 'success', text: 'File deleted' });
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
                <TextField
                  size="small"
                  placeholder="Folder name (optional)"
                  value={folderName}
                  onChange={(e) => setFolderName(e.target.value)}
                  sx={{ mb: 1, width: '100%' }}
                />
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    component="label"
                    startIcon={<CloudUpload />}
                    disabled={uploading}
                    size="small"
                  >
                    Upload
                    <input type="file" hidden accept=".pdf" multiple onChange={handleUpload} />
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
          <Typography variant="h6" sx={{ mb: 2 }}>Uploaded PDFs by Folder</Typography>
          {Object.keys(folders).length === 0 ? (
            <Typography color="textSecondary">No PDFs uploaded yet</Typography>
          ) : (
            Object.entries(folders).map(([folderName, files]) => (
              <Accordion key={folderName}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Folder sx={{ color: '#1976D2' }} />
                    <Typography>{folderName}</Typography>
                    <Chip label={files.length} size="small" />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <List>
                    {files.map((pdf) => (
                      <ListItem
                        key={pdf.path}
                        secondaryAction={
                          <IconButton edge="end" onClick={() => handleDelete(pdf.path)}>
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
                </AccordionDetails>
              </Accordion>
            ))
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default AdminDashboard;
