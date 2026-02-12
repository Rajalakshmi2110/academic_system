import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Paper, Typography, Chip, Accordion, AccordionSummary, AccordionDetails, Switch, FormControlLabel, Dialog, DialogTitle, DialogContent, IconButton, Grid, Card, CardContent } from '@mui/material';
import { Send, ThumbUp, ThumbDown, ExpandMore, CheckCircle, Warning, Cancel, Block, Assessment, Close } from '@mui/icons-material';
import axios from 'axios';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSteps, setShowSteps] = useState(false);
  const [metricsOpen, setMetricsOpen] = useState(false);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:5000/api/metrics')
      .then(res => setMetrics(res.data))
      .catch(err => console.error('Failed to load metrics:', err));
  }, []);

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

  const handleAnswerAnyway = (question) => {
    // Re-send the question with force_answer=true
    setInput(question);
    setTimeout(() => sendMessage(true), 100);
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
    if (status === 'DS_RELATED' || status === 'VALID' || status === 'SUCCESS') return <CheckCircle sx={{ color: '#4CAF50' }} />;
    if (status === 'WARNING') return <Warning sx={{ color: '#FFC107' }} />;
    if (status === 'REJECTED') return <Cancel sx={{ color: '#F44336' }} />;
    if (status === 'NOT_DS_RELATED' || status === 'NOT_IN_CA3101' || status === 'OUT_OF_SYLLABUS') return <Block sx={{ color: '#9E9E9E' }} />;
    return null;
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#F5F5F5' }}>
      <Box sx={{ bgcolor: '#1976D2', color: 'white', p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">Data Structures Doubt Clarification</Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button 
            startIcon={<Assessment />} 
            onClick={() => setMetricsOpen(true)}
            sx={{ color: 'white', border: '1px solid white' }}
          >
            Metrics
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
                              <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Layer 1 - Binary Classifier</Typography>
                            </Box>
                            <Typography variant="caption" sx={{ display: 'block', color: '#666' }}>
                              Checks if question is Data Structures related
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
                              <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Layer 2 - Rule Validator</Typography>
                            </Box>
                            <Typography variant="caption" sx={{ display: 'block', color: '#666' }}>
                              Checks if DS topic is in CA3101 syllabus
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
                              <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Layer 3</Typography>
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

      <Dialog open={metricsOpen} onClose={() => setMetricsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', bgcolor: '#1976D2', color: 'white' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Assessment />
            <Typography variant="h6">System Performance Metrics</Typography>
          </Box>
          <IconButton onClick={() => setMetricsOpen(false)} sx={{ color: 'white' }}>
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ mt: 2 }}>
          {metrics ? (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Card sx={{ bgcolor: '#E3F2FD' }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CheckCircle sx={{ color: '#4CAF50' }} /> Layer 1 - Binary Classifier (DistilBERT)
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="textSecondary">Accuracy</Typography>
                        <Typography variant="h5" sx={{ color: '#4CAF50', fontWeight: 'bold' }}>
                          {(metrics.layer1.accuracy * 100).toFixed(2)}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="textSecondary">Precision</Typography>
                        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                          {(metrics.layer1.precision * 100).toFixed(2)}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="textSecondary">Recall</Typography>
                        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                          {(metrics.layer1.recall * 100).toFixed(2)}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="textSecondary">Avg Latency</Typography>
                        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                          {metrics.layer1.avg_latency_ms.toFixed(1)}ms
                        </Typography>
                      </Grid>
                    </Grid>
                    <Typography variant="caption" sx={{ display: 'block', mt: 1, color: '#666' }}>
                      Tested on {metrics.layer1.total_samples} samples
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card sx={{ bgcolor: '#FFF3E0' }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Warning sx={{ color: '#FF9800' }} /> Layer 2 - Rule-Based Validator
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="textSecondary">Valid</Typography>
                        <Typography variant="h5" sx={{ color: '#4CAF50', fontWeight: 'bold' }}>
                          {metrics.layer2.valid}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="textSecondary">Rejected</Typography>
                        <Typography variant="h5" sx={{ color: '#F44336', fontWeight: 'bold' }}>
                          {metrics.layer2.rejected}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="textSecondary">Out of Syllabus</Typography>
                        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                          {metrics.layer2.out_of_syllabus}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="textSecondary">Avg Latency</Typography>
                        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                          {metrics.layer2.avg_latency_ms.toFixed(2)}ms
                        </Typography>
                      </Grid>
                    </Grid>
                    <Typography variant="caption" sx={{ display: 'block', mt: 1, color: '#666' }}>
                      Tested on {metrics.layer2.total_samples} samples
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card sx={{ bgcolor: '#F3E5F5' }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Assessment sx={{ color: '#9C27B0' }} /> End-to-End Performance
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={4}>
                        <Typography variant="caption" color="textSecondary">Avg Response Time</Typography>
                        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                          {(metrics.end_to_end.avg_latency_ms / 1000).toFixed(2)}s
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="caption" color="textSecondary">Min Response Time</Typography>
                        <Typography variant="h5" sx={{ color: '#4CAF50', fontWeight: 'bold' }}>
                          {(metrics.end_to_end.min_latency_ms / 1000).toFixed(2)}s
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="caption" color="textSecondary">Max Response Time</Typography>
                        <Typography variant="h5" sx={{ color: '#F44336', fontWeight: 'bold' }}>
                          {(metrics.end_to_end.max_latency_ms / 1000).toFixed(2)}s
                        </Typography>
                      </Grid>
                    </Grid>
                    <Typography variant="caption" sx={{ display: 'block', mt: 1, color: '#666' }}>
                      Tested on {metrics.end_to_end.total_samples} complete workflows
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          ) : (
            <Typography>Loading metrics...</Typography>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default ChatInterface;
