import React, { useState, useEffect } from 'react';
import { Box, Card, CardContent, Typography, Grid, Chip, Button, Drawer, List, ListItemButton, ListItemText, Divider, IconButton, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { Dashboard as DashboardIcon, Assessment, Add, Logout, CheckCircle, Folder, Description, AutorenewRounded, Menu, Delete } from '@mui/icons-material';
import axios from 'axios';

const AdminHome = ({ onLogout, onSwitchTab, onSelectSubject }) => {
  const [subjects, setSubjects] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [subjectToDelete, setSubjectToDelete] = useState(null);

  useEffect(() => {
    loadSubjects();
    const interval = setInterval(loadSubjects, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadSubjects = async () => {
    try {
      const res = await axios.get('http://localhost:5001/api/subjects/list');
      setSubjects(res.data.subjects || []);
    } catch (err) {
      console.error('Failed to load subjects:', err);
    }
  };

  const handleDeleteClick = (e, subject) => {
    e.stopPropagation();
    setSubjectToDelete(subject);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await axios.delete(`http://localhost:5001/api/subjects/delete/${subjectToDelete.id}?permanent=true`);
      setDeleteModalOpen(false);
      setSubjectToDelete(null);
      loadSubjects();
    } catch (err) {
      console.error('Failed to delete subject:', err);
      alert('Failed to delete subject');
    }
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Dialog open={deleteModalOpen} onClose={() => setDeleteModalOpen(false)}>
        <DialogTitle>Delete Subject?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete <strong>{subjectToDelete?.name}</strong>?
          </Typography>
          <Typography variant="body2" color="error" sx={{ mt: 2 }}>
            This will permanently delete all documents, models, and data. This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteModalOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete Permanently
          </Button>
        </DialogActions>
      </Dialog>

      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: sidebarOpen ? 260 : 70,
          flexShrink: 0,
          transition: 'width 0.3s',
          '& .MuiDrawer-paper': { 
            width: sidebarOpen ? 260 : 70, 
            boxSizing: 'border-box', 
            bgcolor: '#1976D2', 
            color: 'white',
            transition: 'width 0.3s',
            overflowX: 'hidden'
          }
        }}
      >
        <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {sidebarOpen && <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Admin Panel</Typography>}
          <IconButton onClick={() => setSidebarOpen(!sidebarOpen)} sx={{ color: 'white' }}>
            <Menu />
          </IconButton>
        </Box>
        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
        <List>
          <ListItemButton selected sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', justifyContent: sidebarOpen ? 'initial' : 'center' }}>
            <DashboardIcon sx={{ mr: sidebarOpen ? 2 : 0 }} />
            {sidebarOpen && <ListItemText primary="Home" />}
          </ListItemButton>
          <ListItemButton onClick={() => onSwitchTab(1)} sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' }, justifyContent: sidebarOpen ? 'initial' : 'center' }}>
            <Assessment sx={{ mr: sidebarOpen ? 2 : 0 }} />
            {sidebarOpen && <ListItemText primary="Metrics" />}
          </ListItemButton>
          <ListItemButton onClick={() => onSwitchTab(2)} sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' }, justifyContent: sidebarOpen ? 'initial' : 'center' }}>
            <Add sx={{ mr: sidebarOpen ? 2 : 0 }} />
            {sidebarOpen && <ListItemText primary="Add Subject" />}
          </ListItemButton>
        </List>
        <Box sx={{ flexGrow: 1 }} />
        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
        <List>
          <ListItemButton onClick={onLogout} sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' }, justifyContent: sidebarOpen ? 'initial' : 'center' }}>
            <Logout sx={{ mr: sidebarOpen ? 2 : 0 }} />
            {sidebarOpen && <ListItemText primary="Logout" />}
          </ListItemButton>
        </List>
      </Drawer>

      {/* Main Content */}
      <Box sx={{ flex: 1, bgcolor: '#F5F5F5' }}>
        <Box sx={{ bgcolor: 'white', p: 3, borderBottom: '1px solid #E0E0E0' }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Admin Dashboard</Typography>
          <Typography variant="body2" color="textSecondary">Manage subjects, upload documents, and monitor training</Typography>
        </Box>

        <Box sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5">All Subjects</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => onSwitchTab(2)}
              sx={{ bgcolor: '#1976D2' }}
            >
              Add New Subject
            </Button>
          </Box>

          {subjects.length === 0 ? (
            <Card sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="textSecondary" sx={{ mb: 2 }}>No subjects yet</Typography>
              <Button variant="contained" startIcon={<Add />} onClick={() => onSwitchTab(2)}>
                Add Your First Subject
              </Button>
            </Card>
          ) : (
            <Grid container spacing={3}>
              {subjects.map(subject => (
                <Grid item xs={12} md={6} lg={4} key={subject.id}>
                  <Card 
                    sx={{ 
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': { 
                        boxShadow: 6,
                        transform: 'translateY(-4px)'
                      }
                    }}
                    onClick={() => onSelectSubject(subject.id)}
                  >
                    <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold', lineHeight: 1.3, minHeight: '2.6em' }}>
                          {subject.name}
                        </Typography>
                        {subject.model_trained ? (
                          <Box sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            gap: 0.5,
                            px: 1.5,
                            py: 0.5,
                            bgcolor: '#E8F5E9',
                            borderRadius: 2,
                            border: '1px solid #81C784'
                          }}>
                            <CheckCircle sx={{ fontSize: 16, color: '#4CAF50' }} />
                            <Typography variant="caption" sx={{ fontWeight: 600, color: '#2E7D32' }}>
                              Ready
                            </Typography>
                          </Box>
                        ) : (
                          <Box sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            gap: 0.5,
                            px: 1.5,
                            py: 0.5,
                            bgcolor: '#FFF3E0',
                            borderRadius: 2,
                            border: '1px solid #FFB74D'
                          }}>
                            <AutorenewRounded sx={{ 
                              fontSize: 16, 
                              color: '#FF9800',
                              animation: 'spin 2s linear infinite',
                              '@keyframes spin': {
                                '0%': { transform: 'rotate(0deg)' },
                                '100%': { transform: 'rotate(360deg)' }
                              }
                            }} />
                            <Typography variant="caption" sx={{ fontWeight: 600, color: '#E65100' }}>
                              Training
                            </Typography>
                          </Box>
                        )}
                      </Box>
                      
                      <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                        Course Code: {subject.code || 'N/A'}
                      </Typography>

                      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Description sx={{ fontSize: 18, color: '#666' }} />
                          <Typography variant="body2" color="textSecondary">
                            {subject.document_count || 0} docs
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Folder sx={{ fontSize: 18, color: '#666' }} />
                          <Typography variant="body2" color="textSecondary">
                            {subject.id}
                          </Typography>
                        </Box>
                      </Box>

                      <Box sx={{ mt: 'auto', display: 'flex', gap: 1 }}>
                        <Button 
                          variant="outlined" 
                          size="small" 
                          fullWidth
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectSubject(subject.id);
                          }}
                        >
                          Manage
                        </Button>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => handleDeleteClick(e, subject)}
                          sx={{ border: '1px solid #F44336' }}
                        >
                          <Delete fontSize="small" />
                        </IconButton>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default AdminHome;
