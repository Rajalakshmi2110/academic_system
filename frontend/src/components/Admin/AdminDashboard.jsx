import React, { useState, useEffect } from 'react';
import { Box, Button, Paper, Typography, List, ListItem, ListItemText, IconButton, Alert, LinearProgress, Card, CardContent, Grid, TextField, Accordion, AccordionSummary, AccordionDetails, Chip, Select, MenuItem, FormControl, InputLabel, Radio, RadioGroup, FormControlLabel, FormLabel, Drawer, ListItemButton, Divider } from '@mui/material';
import { CloudUpload, Delete, Refresh, Logout, Description, ExpandMore, Folder, Download, Search, Dashboard as DashboardIcon, Assessment, Add, HourglassEmpty, CheckCircle } from '@mui/icons-material';
import axios from 'axios';

const AdminDashboard = ({ onLogout, onSwitchTab, initialSubject }) => {
  const [folders, setFolders] = useState({});
  const [stats, setStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [message, setMessage] = useState(null);
  const [selectedFolder, setSelectedFolder] = useState('');
  const [newFolderName, setNewFolderName] = useState('');
  const [createNew, setCreateNew] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [subjects, setSubjects] = useState([]);
  const [currentSubject, setCurrentSubject] = useState('data_structures');

  useEffect(() => {
    if (initialSubject) {
      setCurrentSubject(initialSubject);
    }
    loadSubjects();
  }, [initialSubject]);

  useEffect(() => {
    if (currentSubject) {
      loadPdfs();
      loadStats();
    }
    
    // Poll for training status every 10 seconds
    const interval = setInterval(() => {
      loadSubjects();
    }, 10000);
    
    return () => clearInterval(interval);
  }, [currentSubject]);

  useEffect(() => {
    if (currentSubject) {
      loadPdfs();
      loadStats();
    }
  }, [currentSubject]);

  const loadSubjects = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/subjects/list');
      setSubjects(res.data.subjects || []);
      // Only set currentSubject if it's not already set
      if (!currentSubject && res.data.subjects.length > 0) {
        setCurrentSubject(res.data.subjects[0].id);
      }
    } catch (err) {
      console.error('Failed to load subjects:', err);
    }
  };

  const loadPdfs = async () => {
    try {
      const res = await axios.get(`http://localhost:5000/api/admin/list-pdfs?subject_id=${currentSubject}`);
      setFolders(res.data.folders);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load PDFs' });
    }
  };

  const loadStats = async () => {
    try {
      const res = await axios.get(`http://localhost:5000/api/admin/stats?subject_id=${currentSubject}`);
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
      const folderToUse = createNew ? newFolderName : selectedFolder;
      
      for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('subject_id', currentSubject);
        if (folderToUse) formData.append('folder', folderToUse);
        await axios.post('http://localhost:5000/api/admin/upload-pdf', formData);
      }
      setMessage({ type: 'success', text: `${files.length} file(s) uploaded` });
      setSelectedFolder('');
      setNewFolderName('');
      setCreateNew(false);
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
      await axios.delete('http://localhost:5000/api/admin/delete-pdf', { 
        data: { path, subject_id: currentSubject } 
      });
      setMessage({ type: 'success', text: 'File deleted' });
      loadPdfs();
      loadStats();
    } catch (err) {
      setMessage({ type: 'error', text: 'Delete failed' });
    }
  };

  const handleDownload = async (path, filename) => {
    try {
      const res = await axios.post('http://localhost:5000/api/admin/download-file', 
        { path, subject_id: currentSubject }, 
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setMessage({ type: 'error', text: 'Download failed' });
    }
  };

  const handleRebuild = async () => {
    if (!window.confirm('Rebuild vector database? This may take 1-2 minutes.')) return;

    setRebuilding(true);
    setMessage(null);

    try {
      const res = await axios.post('http://localhost:5000/api/admin/rebuild-vector-db', {
        subject_id: currentSubject
      });
      setMessage({ type: 'success', text: 'Vector database rebuilt successfully' });
      loadStats();
    } catch (err) {
      setMessage({ type: 'error', text: 'Rebuild failed' });
    }
    setRebuilding(false);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: 260,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: 260, boxSizing: 'border-box', bgcolor: '#1976D2', color: 'white' }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>Admin Panel</Typography>
          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <Select
              value={currentSubject}
              onChange={(e) => setCurrentSubject(e.target.value)}
              sx={{ bgcolor: 'white', borderRadius: 1 }}
            >
              {subjects.map(subject => (
                <MenuItem key={subject.id} value={subject.id}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    <span>{subject.name}</span>
                    {!subject.model_trained && (
                      <Chip 
                        label="Training" 
                        size="small" 
                        sx={{ 
                          ml: 1, 
                          bgcolor: '#FFC107', 
                          color: 'white',
                          height: 20,
                          fontSize: '0.7rem'
                        }} 
                      />
                    )}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
        <List>
          <ListItemButton onClick={() => onSwitchTab(0)} sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
            <DashboardIcon sx={{ mr: 2 }} />
            <ListItemText primary="Home" />
          </ListItemButton>
          <ListItemButton selected sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}>
            <Folder sx={{ mr: 2 }} />
            <ListItemText primary="Manage Subject" />
          </ListItemButton>
          <ListItemButton onClick={() => onSwitchTab(1)} sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
            <Assessment sx={{ mr: 2 }} />
            <ListItemText primary="Metrics" />
          </ListItemButton>
          <ListItemButton onClick={() => onSwitchTab(2)} sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
            <Add sx={{ mr: 2 }} />
            <ListItemText primary="Add Subject" />
          </ListItemButton>
        </List>
        <Box sx={{ flexGrow: 1 }} />
        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
        <List>
          <ListItemButton onClick={onLogout} sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
            <Logout sx={{ mr: 2 }} />
            <ListItemText primary="Logout" />
          </ListItemButton>
        </List>
      </Drawer>

      {/* Main Content */}
      <Box sx={{ flex: 1, bgcolor: '#F5F5F5' }}>
        <Box sx={{ bgcolor: 'white', p: 2, borderBottom: '1px solid #E0E0E0' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h5">Dashboard - {subjects.find(s => s.id === currentSubject)?.name || 'Loading...'}</Typography>
            {subjects.find(s => s.id === currentSubject && !s.model_trained) && (
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1, 
                px: 2, 
                py: 0.75,
                bgcolor: '#FFF3E0',
                border: '1px solid #FFB74D',
                borderRadius: 2,
                boxShadow: '0 2px 4px rgba(255,152,0,0.1)'
              }}>
                <Box sx={{ 
                  width: 16, 
                  height: 16, 
                  border: '2px solid #FF9800', 
                  borderTop: '2px solid transparent', 
                  borderRadius: '50%', 
                  animation: 'spin 1s linear infinite',
                  '@keyframes spin': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' }
                  }
                }} />
                <Typography variant="body2" sx={{ color: '#E65100', fontWeight: 600 }}>
                  Training Model
                </Typography>
                <Typography variant="caption" sx={{ color: '#F57C00' }}>
                  (~5-10 min)
                </Typography>
              </Box>
            )}
            {subjects.find(s => s.id === currentSubject && s.model_trained) && (
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1, 
                px: 2, 
                py: 0.75,
                bgcolor: '#E8F5E9',
                border: '1px solid #81C784',
                borderRadius: 2,
                boxShadow: '0 2px 4px rgba(76,175,80,0.1)'
              }}>
                <CheckCircle sx={{ fontSize: 18, color: '#4CAF50' }} />
                <Typography variant="body2" sx={{ color: '#2E7D32', fontWeight: 600 }}>
                  Ready
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
        {message && <Alert severity={message.type} sx={{ mb: 2 }}>{message.text}</Alert>}

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6">Files Uploaded</Typography>
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
                <FormControl component="fieldset" sx={{ mb: 1 }}>
                  <RadioGroup row value={createNew ? 'new' : 'existing'} onChange={(e) => setCreateNew(e.target.value === 'new')}>
                    <FormControlLabel value="existing" control={<Radio size="small" />} label="Existing Folder" />
                    <FormControlLabel value="new" control={<Radio size="small" />} label="New Folder" />
                  </RadioGroup>
                </FormControl>
                
                {createNew ? (
                  <TextField
                    size="small"
                    placeholder="New folder name"
                    value={newFolderName}
                    onChange={(e) => setNewFolderName(e.target.value)}
                    sx={{ mb: 1, width: '100%' }}
                  />
                ) : (
                  <FormControl size="small" fullWidth sx={{ mb: 1 }}>
                    <InputLabel>Select Folder</InputLabel>
                    <Select
                      value={selectedFolder}
                      label="Select Folder"
                      onChange={(e) => setSelectedFolder(e.target.value)}
                    >
                      <MenuItem value="">Root (ClassNotes)</MenuItem>
                      {Object.keys(folders)
                        .filter(f => f.startsWith('ClassNotes/'))
                        .map(f => f.replace('ClassNotes/', ''))
                        .filter((v, i, a) => a.indexOf(v) === i)
                        .map(folder => (
                          <MenuItem key={folder} value={folder}>{folder}</MenuItem>
                        ))}
                    </Select>
                  </FormControl>
                )}
                
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    component="label"
                    startIcon={<CloudUpload />}
                    disabled={uploading}
                    size="small"
                  >
                    Upload
                    <input type="file" hidden accept=".pdf,.doc,.docx,.ppt,.pptx" multiple onChange={handleUpload} />
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
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Uploaded Files by Folder</Typography>
            <TextField
              size="small"
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'gray' }} />
              }}
              sx={{ width: 300 }}
            />
          </Box>
          {Object.keys(folders).length === 0 ? (
            <Typography color="textSecondary">No files uploaded yet</Typography>
          ) : (
            Object.entries(folders)
              .filter(([folderName, files]) => 
                searchQuery === '' || 
                folderName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                files.some(f => f.filename.toLowerCase().includes(searchQuery.toLowerCase()))
              )
              .map(([folderName, files]) => (
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
                    {files
                      .filter(pdf => searchQuery === '' || pdf.filename.toLowerCase().includes(searchQuery.toLowerCase()))
                      .map((pdf) => (
                      <ListItem
                        key={pdf.path}
                        secondaryAction={
                          <Box>
                            <IconButton edge="end" onClick={() => handleDownload(pdf.path, pdf.filename)}>
                              <Download />
                            </IconButton>
                            <IconButton edge="end" onClick={() => handleDelete(pdf.path)}>
                              <Delete />
                            </IconButton>
                          </Box>
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
