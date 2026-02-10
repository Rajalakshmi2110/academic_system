import React, { useState } from 'react';
import { Box, TextField, Button, Paper, Typography, Chip } from '@mui/material';
import { Send, ThumbUp, ThumbDown } from '@mui/icons-material';
import axios from 'axios';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

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

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { type: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('http://localhost:5000/api/chat', { question: input });
      setMessages(prev => [...prev, { type: 'bot', data: res.data }]);
    } catch (error) {
      setMessages(prev => [...prev, { type: 'bot', data: { final_status: 'ERROR', explanation: 'Failed to connect to backend' } }]);
    }
    setLoading(false);
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#F5F5F5' }}>
      <Box sx={{ bgcolor: '#1976D2', color: 'white', p: 2 }}>
        <Typography variant="h5">Data Structures Doubt Clarification</Typography>
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
                  <Typography>{msg.data.answer || msg.data.explanation || msg.data.message}</Typography>
                  {(msg.data.status === 'success' || msg.data.final_status === 'VALID') && (
                    <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                      <Button size="small" startIcon={<ThumbUp />}>Helpful</Button>
                      <Button size="small" startIcon={<ThumbDown />}>Not Helpful</Button>
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
