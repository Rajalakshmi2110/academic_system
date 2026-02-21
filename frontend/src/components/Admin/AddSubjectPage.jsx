import React, { useState } from 'react';
import { Box, Button, Paper, Typography, TextField, Alert, LinearProgress, Drawer, List, ListItemButton, ListItemText, Divider, Card, CardContent, FormControlLabel, Checkbox } from '@mui/material';
import { CloudUpload, Dashboard as DashboardIcon, Assessment, Add, Logout, Description, Folder } from '@mui/icons-material';
import axios from 'axios';

const AddSubjectPage = ({ onLogout, onSwitchTab }) => {
  const [formData, setFormData] = useState({
    name: '',
    code: ''
  });
  const [syllabusFile, setSyllabusFile] = useState(null);
  const [documentFiles, setDocumentFiles] = useState([]);
  const [autoTrain, setAutoTrain] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSyllabusUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.name.endsWith('.json')) {
      setSyllabusFile(file);
      setMessage(null);
    } else {
      setMessage({ type: 'error', text: 'Please upload a valid JSON file' });
    }
  };

  const handleDocumentsUpload = (e) => {
    const files = Array.from(e.target.files);
    setDocumentFiles(files);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.code) {
      setMessage({ type: 'error', text: 'Subject name and course code are required' });
      return;
    }

    if (!syllabusFile) {
      setMessage({ type: 'error', text: 'Syllabus file is required' });
      return;
    }

    setUploading(true);
    setMessage(null);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('code', formData.code);
      formDataToSend.append('id', formData.code.toLowerCase());
      formDataToSend.append('syllabus', syllabusFile);
      formDataToSend.append('auto_train', autoTrain);
      
      documentFiles.forEach(file => {
        formDataToSend.append('documents', file);
      });

      const res = await axios.post('http://localhost:5000/api/subjects/add', formDataToSend, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setMessage({ 
        type: 'success', 
        text: autoTrain 
          ? 'Subject created! Training started in background (may take 5-10 minutes).' 
          : 'Subject created successfully!'
      });
      
      // Reset form
      setFormData({ name: '', code: '' });
      setSyllabusFile(null);
      setDocumentFiles([]);
      
    } catch (err) {
      setMessage({ 
        type: 'error', 
        text: err.response?.data?.error || 'Failed to create subject' 
      });
    }
    
    setUploading(false);
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
        </Box>
        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
        <List>
          <ListItemButton onClick={() => onSwitchTab(0)} sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
            <DashboardIcon sx={{ mr: 2 }} />
            <ListItemText primary="Dashboard" />
          </ListItemButton>
          <ListItemButton onClick={() => onSwitchTab(1)} sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
            <Assessment sx={{ mr: 2 }} />
            <ListItemText primary="Metrics" />
          </ListItemButton>
          <ListItemButton selected sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}>
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
      <Box sx={{ flex: 1, bgcolor: '#F5F5F5', p: 4 }}>
        <Box sx={{ bgcolor: 'white', p: 2, borderBottom: '1px solid #E0E0E0', mb: 3 }}>
          <Typography variant="h5">Add New Subject</Typography>
        </Box>

        {message && <Alert severity={message.type} sx={{ mb: 3 }}>{message.text}</Alert>}

        <Paper sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
          <form onSubmit={handleSubmit}>
            <Typography variant="h6" sx={{ mb: 3 }}>Subject Information</Typography>
            
            <TextField
              fullWidth
              label="Subject Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
              placeholder="e.g., Data Structures"
            />
            
            <TextField
              fullWidth
              label="Course Code"
              name="code"
              value={formData.code}
              onChange={handleInputChange}
              required
              sx={{ mb: 3 }}
              placeholder="e.g., OS3101"
              helperText="Will be used as subject ID (e.g., os3101)"
            />

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" sx={{ mb: 2 }}>Upload Files</Typography>
            
            <Card sx={{ mb: 2, bgcolor: '#F9F9F9' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Description sx={{ mr: 1, color: '#1976D2' }} />
                  <Typography variant="subtitle1">Syllabus (Required)</Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Upload syllabus.json file containing course units and topics
                </Typography>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUpload />}
                  size="small"
                >
                  Choose Syllabus JSON
                  <input type="file" hidden accept=".json" onChange={handleSyllabusUpload} />
                </Button>
                {syllabusFile && (
                  <Typography variant="body2" sx={{ mt: 1, color: 'green' }}>
                    ✓ {syllabusFile.name}
                  </Typography>
                )}
              </CardContent>
            </Card>

            <Card sx={{ mb: 3, bgcolor: '#F9F9F9' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Folder sx={{ mr: 1, color: '#1976D2' }} />
                  <Typography variant="subtitle1">Course Documents (Optional)</Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Upload PDFs, PPTs, or Word documents (ClassNotes, Textbooks, etc.)
                </Typography>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUpload />}
                  size="small"
                >
                  Choose Documents
                  <input type="file" hidden multiple accept=".pdf,.doc,.docx,.ppt,.pptx" onChange={handleDocumentsUpload} />
                </Button>
                {documentFiles.length > 0 && (
                  <Typography variant="body2" sx={{ mt: 1, color: 'green' }}>
                    ✓ {documentFiles.length} file(s) selected
                  </Typography>
                )}
              </CardContent>
            </Card>

            <FormControlLabel
              control={
                <Checkbox
                  checked={autoTrain}
                  onChange={(e) => setAutoTrain(e.target.checked)}
                  color="primary"
                />
              }
              label="Auto-train model after creation (recommended)"
              sx={{ mb: 3 }}
            />

            {autoTrain && (
              <Alert severity="info" sx={{ mb: 3 }}>
                Training will generate 2000+ samples and train Layer 1 model automatically. 
                This may take 5-10 minutes. You can continue using the dashboard while training runs in background.
              </Alert>
            )}

            {uploading && <LinearProgress sx={{ mb: 2 }} />}

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={uploading}
                startIcon={<Add />}
              >
                {uploading ? 'Creating Subject...' : 'Create Subject'}
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => onSwitchTab(0)}
                disabled={uploading}
              >
                Cancel
              </Button>
            </Box>
          </form>
        </Paper>
      </Box>
    </Box>
  );
};

export default AddSubjectPage;
