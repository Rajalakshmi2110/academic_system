import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Paper, Typography, Chip, Accordion, AccordionSummary, AccordionDetails, Switch, FormControlLabel } from '@mui/material';
import { Send, ThumbUp, ThumbDown, ExpandMore, CheckCircle, Warning, Cancel, Block } from '@mui/icons-material';
import axios from 'axios';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSteps, setShowSteps] = useState(false);

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
    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
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
      // Show success message
      alert('Thank you for your feedback!');
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const getStepIcon = (status) => {
    if (status === 'PASS' || status === 'IN_SYLLABUS' || status === 'SUCCESS') return <CheckCircle sx={{ color: '#4CAF50' }} />;
    if (status === 'WARNING') return <Warning sx={{ color: '#FFC107' }} />;
    if (status === 'FAIL' || status === 'ERROR') return <Cancel sx={{ color: '#F44336' }} />;
    if (status === 'OUT_OF_SYLLABUS') return <Block sx={{ color: '#9E9E9E' }} />;
    return null;
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#F5F5F5' }}>
      <Box sx={{ bgcolor: '#1976D2', color: 'white', p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">Data Structures Doubt Clarification</Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
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
                  
                  <Typography>
                    {typeof (msg.data.answer || msg.data.explanation || msg.data.message) === 'string' 
                      ? (msg.data.answer || msg.data.explanation || msg.data.message)
                      : JSON.stringify(msg.data.answer || msg.data.explanation || msg.data.message)}
                  </Typography>
                  
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
    </Box>
  );
};

export default ChatInterface;
