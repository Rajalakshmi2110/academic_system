import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Paper, Typography, Chip, Accordion, AccordionSummary, AccordionDetails, Switch, FormControlLabel, IconButton, Snackbar, Drawer, List, ListItem, ListItemText, ListItemButton, Divider } from '@mui/material';
import { Send, ThumbUp, ThumbDown, ExpandMore, CheckCircle, Warning, Cancel, Block, ContentCopy, Add, Delete, Chat } from '@mui/icons-material';
import axios from 'axios';

const ChatInterface = () => {
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSteps, setShowSteps] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('conversations');
    if (saved) {
      const convs = JSON.parse(saved);
      setConversations(convs);
      if (convs.length > 0) {
        setCurrentConvId(convs[0].id);
        setMessages(convs[0].messages);
      }
    } else {
      createNewConversation();
    }
  }, []);

  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('conversations', JSON.stringify(conversations));
    }
  }, [conversations]);

  useEffect(() => {
    if (currentConvId && messages.length > 0) {
      setConversations(prev => prev.map(conv => 
        conv.id === currentConvId ? { ...conv, messages, updatedAt: Date.now() } : conv
      ));
    }
  }, [messages, currentConvId]);

  const createNewConversation = () => {
    const newConv = {
      id: Date.now(),
      title: 'New Chat',
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now()
    };
    setConversations(prev => [newConv, ...prev]);
    setCurrentConvId(newConv.id);
    setMessages([]);
  };

  const switchConversation = (convId) => {
    const conv = conversations.find(c => c.id === convId);
    if (conv) {
      setCurrentConvId(convId);
      setMessages(conv.messages);
    }
  };

  const deleteConversation = (convId) => {
    if (window.confirm('Delete this conversation?')) {
      const newConvs = conversations.filter(c => c.id !== convId);
      setConversations(newConvs);
      if (currentConvId === convId) {
        if (newConvs.length > 0) {
          setCurrentConvId(newConvs[0].id);
          setMessages(newConvs[0].messages);
        } else {
          createNewConversation();
        }
      }
    }
  };

  const updateConversationTitle = (convId, firstQuestion) => {
    setConversations(prev => prev.map(conv => 
      conv.id === convId && conv.title === 'New Chat' 
        ? { ...conv, title: firstQuestion.slice(0, 30) + (firstQuestion.length > 30 ? '...' : '') }
        : conv
    ));
  };

  const getStatusColor = (status) => {
    const colors = {
      'success': '#4CAF50',
      'VALID': '#4CAF50',
      'WARNING': '#FFC107',
      'REJECTED': '#F44336',
      'OUT_OF_SYLLABUS': '#9E9E9E'
    };
    return colors[status] || '#9E9E9E';
  };

  const sendMessage = async (forceAnswer = false) => {
    if (!input.trim()) return;
    const userMsg = { type: 'user', text: input };
    const currentInput = input;
    
    if (messages.length === 0) {
      updateConversationTitle(currentConvId, currentInput);
    }
    
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('http://localhost:5000/api/chat', { 
        question: currentInput,
        show_steps: showSteps,
        force_answer: forceAnswer
      });
      setMessages(prev => [...prev, { type: 'bot', data: res.data }]);
    } catch (error) {
      setMessages(prev => [...prev, { type: 'bot', data: { final_status: 'ERROR', explanation: 'Failed to connect to backend' } }]);
    }
    setLoading(false);
  };

  const handleAnswerAnyway = async (question) => {
    const userMsg = { type: 'user', text: question };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await axios.post('http://localhost:5000/api/chat', { 
        question: question,
        show_steps: showSteps,
        force_answer: true
      });
      setMessages(prev => [...prev, { type: 'bot', data: res.data }]);
    } catch (error) {
      setMessages(prev => [...prev, { type: 'bot', data: { final_status: 'ERROR', explanation: 'Failed to connect to backend' } }]);
    }
    setLoading(false);
  };

  const handleFeedback = async (question, answer, feedback) => {
    try {
      await axios.post('http://localhost:5000/api/feedback', {
        question,
        answer,
        feedback
      });
      alert('Thank you for your feedback!');
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopySuccess(true);
    }).catch(err => {
      console.error('Failed to copy:', err);
    });
  };

  const getStepIcon = (status) => {
    if (status === 'PASS' || status === 'IN_SYLLABUS' || status === 'SUCCESS') return <CheckCircle sx={{ color: '#4CAF50' }} />;
    if (status === 'WARNING') return <Warning sx={{ color: '#FFC107' }} />;
    if (status === 'FAIL' || status === 'ERROR') return <Cancel sx={{ color: '#F44336' }} />;
    if (status === 'OUT_OF_SYLLABUS') return <Block sx={{ color: '#9E9E9E' }} />;
    return null;
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex' }}>
      <Drawer
        variant="permanent"
        sx={{
          width: 260,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: 260, boxSizing: 'border-box', bgcolor: '#202123', color: 'white' }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<Add />}
            onClick={createNewConversation}
            sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)', '&:hover': { borderColor: 'white' } }}
          >
            New Chat
          </Button>
        </Box>
        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.1)' }} />
        <List sx={{ flex: 1, overflow: 'auto', px: 1 }}>
          {conversations.map(conv => (
            <ListItem
              key={conv.id}
              disablePadding
              secondaryAction={
                <IconButton
                  edge="end"
                  size="small"
                  onClick={() => deleteConversation(conv.id)}
                  sx={{ color: 'rgba(255,255,255,0.5)', '&:hover': { color: 'white' } }}
                >
                  <Delete fontSize="small" />
                </IconButton>
              }
            >
              <ListItemButton
                selected={conv.id === currentConvId}
                onClick={() => switchConversation(conv.id)}
                sx={{
                  borderRadius: 1,
                  mb: 0.5,
                  '&.Mui-selected': { bgcolor: 'rgba(255,255,255,0.1)' },
                  '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' }
                }}
              >
                <Chat sx={{ mr: 1, fontSize: 18 }} />
                <ListItemText
                  primary={conv.title}
                  primaryTypographyProps={{ fontSize: 14, noWrap: true }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>

      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', bgcolor: '#F5F5F5' }}>
        <Box sx={{ bgcolor: '#1976D2', color: 'white', p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5">Data Structures Doubt Clarification</Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Button
              variant="outlined"
              size="small"
              onClick={() => window.location.href = '/?admin=true'}
              sx={{ color: 'white', borderColor: 'white', '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' } }}
            >
              Admin
            </Button>
            <FormControlLabel
              control={<Switch checked={showSteps} onChange={(e) => setShowSteps(e.target.checked)} sx={{ '& .MuiSwitch-switchBase.Mui-checked': { color: 'white' } }} />}
              label="Show Steps"
              sx={{ color: 'white' }}
            />
          </Box>
        </Box>
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {messages.map((msg, idx) => (
            <Box key={idx} sx={{ display: 'flex', justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start', mb: 2 }}>
              <Paper sx={{ p: 2, maxWidth: '70%', bgcolor: msg.type === 'user' ? '#E3F2FD' : 'white', borderRadius: 2 }}>
                {msg.type === 'user' ? (
                  <Typography>{msg.text}</Typography>
                ) : (
                  <>
                    <Chip 
                      label={msg.data.status || msg.data.final_status} 
                      sx={{ bgcolor: getStatusColor(msg.data.status || msg.data.final_status), color: 'white', mb: 1 }} 
                      size="small" 
                    />
                    
                    {msg.data.intermediate_steps && (
                      <Accordion sx={{ mb: 2, boxShadow: 'none', border: '1px solid #E0E0E0' }}>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>🔍 Intermediate Steps</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          {msg.data.intermediate_steps.layer1 && (
                            <Box sx={{ mb: 2, p: 1.5, bgcolor: '#F5F5F5', borderRadius: 1 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                {getStepIcon(msg.data.intermediate_steps.layer1.status)}
                                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                  Layer 1 - {msg.data.intermediate_steps.layer1.name || 'DS Classifier'}
                                </Typography>
                              </Box>
                              <Typography variant="caption" sx={{ display: 'block', color: '#666' }}>
                                {msg.data.intermediate_steps.layer1.description}
                              </Typography>
                              <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                                Status: {msg.data.intermediate_steps.layer1.status || 'N/A'} | 
                                Latency: {msg.data.intermediate_steps.layer1.latency_ms?.toFixed(2)}ms
                              </Typography>
                            </Box>
                          )}
                          
                          {msg.data.intermediate_steps.layer2 && (
                            <Box sx={{ mb: 2, p: 1.5, bgcolor: '#F5F5F5', borderRadius: 1 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                {getStepIcon(msg.data.intermediate_steps.layer2.status)}
                                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                  Layer 2 - {msg.data.intermediate_steps.layer2.name || 'Syllabus Checker'}
                                </Typography>
                              </Box>
                              <Typography variant="caption" sx={{ display: 'block', color: '#666' }}>
                                {msg.data.intermediate_steps.layer2.description}
                              </Typography>
                              <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                                Status: {msg.data.intermediate_steps.layer2.status} | 
                                Latency: {msg.data.intermediate_steps.layer2.latency_ms?.toFixed(2)}ms
                              </Typography>
                            </Box>
                          )}
                          
                          {msg.data.intermediate_steps.layer3 && (
                            <Box sx={{ p: 1.5, bgcolor: '#F5F5F5', borderRadius: 1 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                {getStepIcon(msg.data.intermediate_steps.layer3.status)}
                                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                  Layer 3 - {msg.data.intermediate_steps.layer3.name || 'RAG Pipeline'}
                                </Typography>
                              </Box>
                              <Typography variant="caption" sx={{ display: 'block', color: '#666' }}>
                                {msg.data.intermediate_steps.layer3.description}
                              </Typography>
                              <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                                Status: {msg.data.intermediate_steps.layer3.status} | 
                                Latency: {msg.data.intermediate_steps.layer3.latency_ms?.toFixed(2)}ms
                              </Typography>
                            </Box>
                          )}
                          
                          {msg.data.total_latency_ms && (
                            <Typography variant="caption" sx={{ display: 'block', mt: 2, fontWeight: 'bold', textAlign: 'right' }}>
                              Total: {msg.data.total_latency_ms.toFixed(2)}ms
                            </Typography>
                          )}
                        </AccordionDetails>
                      </Accordion>
                    )}
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Typography sx={{ flex: 1 }}>
                        {typeof (msg.data.answer || msg.data.explanation || msg.data.message) === 'string' 
                          ? (msg.data.answer || msg.data.explanation || msg.data.message)
                          : JSON.stringify(msg.data.answer || msg.data.explanation || msg.data.message)}
                      </Typography>
                      {(msg.data.answer || msg.data.explanation) && (
                        <IconButton 
                          size="small" 
                          onClick={() => copyToClipboard(msg.data.answer || msg.data.explanation)}
                          sx={{ ml: 1 }}
                        >
                          <ContentCopy fontSize="small" />
                        </IconButton>
                      )}
                    </Box>
                    
                    {msg.data.final_status === 'OUT_OF_SYLLABUS' && (
                      <Box sx={{ mt: 2 }}>
                        <Button 
                          variant="outlined" 
                          size="small" 
                          onClick={() => handleAnswerAnyway(msg.data.question)}
                          sx={{ borderColor: '#FF9800', color: '#FF9800' }}
                        >
                          📚 Answer Anyway (Not in CA3101 syllabus)
                        </Button>
                      </Box>
                    )}
                    
                    {msg.data.warning && (
                      <Box sx={{ mt: 1, p: 1, bgcolor: '#FFF3E0', borderRadius: 1, borderLeft: '4px solid #FF9800' }}>
                        <Typography variant="caption" sx={{ color: '#E65100', fontWeight: 'bold' }}>
                          ⚠️ Warning: {msg.data.warning}
                        </Typography>
                      </Box>
                    )}
                    {(msg.data.status === 'success' || msg.data.final_status === 'VALID') && (
                      <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                        <Button 
                          size="small" 
                          startIcon={<ThumbUp />}
                          onClick={() => handleFeedback(msg.data.question, msg.data.answer, 'helpful')}
                        >
                          Helpful
                        </Button>
                        <Button 
                          size="small" 
                          startIcon={<ThumbDown />}
                          onClick={() => handleFeedback(msg.data.question, msg.data.answer, 'not_helpful')}
                        >
                          Not Helpful
                        </Button>
                      </Box>
                    )}
                  </>
                )}
              </Paper>
            </Box>
          ))}
        </Box>
        <Box sx={{ p: 2, bgcolor: 'white', borderTop: '1px solid #E0E0E0' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField fullWidth value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && sendMessage()} placeholder="Ask your doubt..." disabled={loading} sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
            <Button variant="contained" onClick={sendMessage} disabled={loading} sx={{ borderRadius: 2, bgcolor: '#1976D2' }}><Send /></Button>
          </Box>
        </Box>
        <Snackbar
          open={copySuccess}
          autoHideDuration={2000}
          onClose={() => setCopySuccess(false)}
          message="Copied to clipboard!"
        />
      </Box>
    </Box>
  );
};

export default ChatInterface;
