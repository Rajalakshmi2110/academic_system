import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Paper, Typography, Chip, Accordion, AccordionSummary, AccordionDetails, Switch, FormControlLabel, IconButton, Snackbar, Drawer, List, ListItem, ListItemText, ListItemButton, Divider, Dialog, DialogTitle, DialogContent, DialogActions, Collapse } from '@mui/material';
import { Send, ThumbUp, ThumbDown, ExpandMore, CheckCircle, Warning, Cancel, Block, ContentCopy, Add, Delete, Chat, Menu, School, ExpandLess, VolumeUp, Mic, MicOff } from '@mui/icons-material';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const ChatInterface = ({ onBackToHome, openSubjectModal = false }) => {
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const inputRef = React.useRef('');
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [showSteps, setShowSteps] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [comparisonMode, setComparisonMode] = useState(false);
  const [voiceLoading, setVoiceLoading] = useState(null);
  const [playingAudio, setPlayingAudio] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [subjects, setSubjects] = useState([]);
  const [subjectModalOpen, setSubjectModalOpen] = useState(openSubjectModal);
  const [expandedSubjects, setExpandedSubjects] = useState({});

  useEffect(() => {
    axios.get('http://localhost:5001/api/subjects/active')
      .then(res => {
        const activeSubjects = res.data.subjects || [];
        setSubjects(activeSubjects);
        const expanded = {};
        activeSubjects.forEach(s => expanded[s.id] = true);
        setExpandedSubjects(expanded);
      })
      .catch(err => console.error('Failed to load subjects:', err));

    const saved = localStorage.getItem('conversations');
    
    if (saved) {
      const convs = JSON.parse(saved);
      setConversations(convs);
      
      if (convs.length > 0) {
        setCurrentConvId(convs[0].id);
        setMessages(convs[0].messages);
      }
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

  const subjectSuggestions = {
    data_structures: [
      'What is a binary search tree?',
      'Explain heap sort algorithm',
      'Compare stack and queue',
      'How does hashing work?'
    ],
    operating_system: [
      'What is process scheduling?',
      'Explain deadlock prevention',
      'Compare paging and segmentation',
      'How does virtual memory work?'
    ]
  };

  const createNewConversation = (subjectId, subjectName) => {
    const suggestions = subjectSuggestions[subjectId] || [
      `What are the key topics in ${subjectName}?`,
      `Explain a core concept in ${subjectName}`,
      'Give me an example with explanation'
    ];
    const newConv = {
      id: Date.now(),
      title: 'New Conversation',
      subjectId: subjectId,
      subjectName: subjectName,
      messages: [{
        type: 'welcome',
        data: {
          status: 'welcome',
          final_status: 'VALID',
          title: `Welcome to ${subjectName}`,
          subtitle: 'Ask me anything covered in your syllabus',
          suggestions: suggestions
        }
      }],
      createdAt: Date.now(),
      updatedAt: Date.now()
    };
    setConversations(prev => [newConv, ...prev]);
    setCurrentConvId(newConv.id);
    setMessages(newConv.messages);
    setSubjectModalOpen(false);
  };

  const switchConversation = (convId) => {
    const conv = conversations.find(c => c.id === convId);
    if (conv) {
      setCurrentConvId(convId);
      setMessages(conv.messages);
    }
  };

  const toggleSubjectExpand = (subjectId) => {
    setExpandedSubjects(prev => ({ ...prev, [subjectId]: !prev[subjectId] }));
  };

  const getConversationsBySubject = () => {
    const grouped = {};
    subjects.forEach(subject => {
      grouped[subject.id] = conversations.filter(c => c.subjectId === subject.id);
    });
    return grouped;
  };

  const getCurrentSubject = () => {
    const conv = conversations.find(c => c.id === currentConvId);
    return conv ? { id: conv.subjectId, name: conv.subjectName } : null;
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
      conv.id === convId && conv.title === 'New Conversation' 
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
    const currentInput = inputRef.current || input;
    if (!currentInput.trim()) return;
    const userMsg = { type: 'user', text: currentInput };
    
    if (messages.length === 0) {
      updateConversationTitle(currentConvId, currentInput);
    }
    
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    inputRef.current = '';
    setLoading(true);
    setLoadingStage('Validating question...');

    try {
      const currentSubject = getCurrentSubject();
      const trimmedHistory = messages
        .filter(m => (m.type === 'user' && m.text) || (m.type === 'bot' && m.data?.answer && typeof m.data.answer === 'string'))
        .slice(-6)
        .map(m => {
          if (m.type === 'user') return { type: 'user', text: String(m.text || '') };
          return { type: 'bot', data: { answer: String(m.data.answer).slice(0, 300) } };
        });
      if (comparisonMode) {
        setLoadingStage('Processing both modes...');
        const [validatedRes, directRes] = await Promise.all([
          axios.post('http://localhost:5001/api/chat', { 
            question: currentInput, 
            show_steps: showSteps, 
            force_answer: forceAnswer,
            history: trimmedHistory,
            subject_id: currentSubject?.id
          }),
          axios.post('http://localhost:5001/api/chat/direct', { 
            question: currentInput,
            history: trimmedHistory,
            subject_id: currentSubject?.id
          })
        ]);
        setMessages(prev => [...prev, { type: 'bot', data: validatedRes.data, comparison: directRes.data }]);
      } else {
        setTimeout(() => setLoadingStage('Checking syllabus...'), 100);
        setTimeout(() => setLoadingStage('Generating answer...'), 1500);
        const res = await axios.post('http://localhost:5001/api/chat', { 
          question: currentInput, 
          show_steps: showSteps, 
          force_answer: forceAnswer,
          history: trimmedHistory,
          format: 'structured',
          subject_id: currentSubject?.id
        });
        setMessages(prev => [...prev, { type: 'bot', data: res.data }]);
      }
    } catch (error) {
      console.error('Chat error:', error?.response?.status, error?.message, error);
      const errMsg = error?.response?.data?.message || error?.message || 'Failed to connect to backend';
      setMessages(prev => [...prev, { type: 'bot', data: { final_status: 'ERROR', explanation: errMsg } }]);
    }
    setLoading(false);
    setLoadingStage('');
  };

  const handleAnswerAnyway = async (question) => {
    const userMsg = { type: 'user', text: question };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const currentSubject = getCurrentSubject();
      const res = await axios.post('http://localhost:5001/api/chat', { 
        question: question,
        show_steps: showSteps,
        force_answer: true,
        history: messages,
        format: 'structured',
        subject_id: currentSubject?.id
      });
      setMessages(prev => [...prev, { type: 'bot', data: res.data }]);
    } catch (error) {
      setMessages(prev => [...prev, { type: 'bot', data: { final_status: 'ERROR', explanation: 'Failed to connect to backend' } }]);
    }
    setLoading(false);
    setLoadingStage('');
  };

  const handleRetryWithContext = async (rejectedQuestion) => {
    setLoading(true);

    try {
      const currentSubject = getCurrentSubject();
      const res = await axios.post('http://localhost:5001/api/chat/direct', { 
        question: rejectedQuestion,
        history: messages,
        subject_id: currentSubject?.id
      });
      setMessages(prev => [...prev, { type: 'bot', data: { 
        status: 'success',
        answer: res.data.answer,
        final_status: 'VALID',
        retried: true
      } }]);
    } catch (error) {
      setMessages(prev => [...prev, { type: 'bot', data: { final_status: 'ERROR', explanation: 'Failed to connect to backend' } }]);
    }
    setLoading(false);
    setLoadingStage('');
  };

  const handleFeedback = async (question, answer, feedback) => {
    try {
      await axios.post('http://localhost:5001/api/feedback', {
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

  const handleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition not supported in this browser. Use Chrome.');
      return;
    }

    if (isListening) return;

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      setInput(prev => {
        const newVal = prev ? prev + ' ' + transcript : transcript;
        inputRef.current = newVal;
        return newVal;
      });
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  const handleVoiceExplain = async (question, answer, msgIdx) => {
    if (playingAudio) {
      playingAudio.pause();
      playingAudio.currentTime = 0;
      setPlayingAudio(null);
      setVoiceLoading(null);
      return;
    }

    setVoiceLoading(msgIdx);
    try {
      const res = await axios.post('http://localhost:5001/api/voice/explain', {
        question,
        answer
      }, { responseType: 'blob' });

      const audioUrl = URL.createObjectURL(res.data);
      const audio = new Audio(audioUrl);
      audio.onended = () => {
        setPlayingAudio(null);
        setVoiceLoading(null);
        URL.revokeObjectURL(audioUrl);
      };
      setPlayingAudio(audio);
      audio.play();
    } catch (error) {
      console.error('Voice generation failed:', error);
    }
    setVoiceLoading(null);
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
      <Dialog open={subjectModalOpen} maxWidth="sm" fullWidth>
        <DialogTitle>Choose a Subject</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2, color: '#666' }}>
            Select a subject to start your chat. Each conversation is locked to one subject.
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {subjects.map(subject => (
              <Button
                key={subject.id}
                variant="outlined"
                onClick={() => createNewConversation(subject.id, subject.name)}
                sx={{ 
                  justifyContent: 'flex-start',
                  p: 2,
                  textAlign: 'left',
                  '&:hover': { bgcolor: '#E3F2FD' }
                }}
              >
                <School sx={{ mr: 2, color: '#1976D2' }} />
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                    {subject.name}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#666' }}>
                    {subject.course_code}
                  </Typography>
                </Box>
              </Button>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSubjectModalOpen(false)} color="inherit">
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      <Drawer
        variant="persistent"
        open={sidebarOpen}
        sx={{
          width: sidebarOpen ? 260 : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: 260, boxSizing: 'border-box', bgcolor: 'white', color: '#333', borderRight: '1px solid #E0E0E0' }
        }}
      >
        <Box sx={{ p: 2, bgcolor: '#1976D2' }}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<Add />}
            onClick={() => setSubjectModalOpen(true)}
            sx={{ color: 'white', borderColor: 'white', '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' } }}
          >
            Select Subject
          </Button>
        </Box>
        <Divider />
        <List sx={{ flex: 1, overflow: 'auto', px: 1 }}>
          {subjects.map(subject => {
            const subjectConvs = getConversationsBySubject()[subject.id] || [];
            if (subjectConvs.length === 0) return null;
            return (
              <Box key={subject.id}>
                <ListItemButton
                  onClick={() => toggleSubjectExpand(subject.id)}
                  sx={{ borderRadius: 1, mb: 0.5 }}
                >
                  <School sx={{ mr: 1, fontSize: 18, color: '#1976D2' }} />
                  <ListItemText
                    primary={subject.name}
                    primaryTypographyProps={{ fontSize: 13, fontWeight: 'bold', noWrap: true }}
                  />
                  {expandedSubjects[subject.id] ? <ExpandLess /> : <ExpandMore />}
                </ListItemButton>
                <Collapse in={expandedSubjects[subject.id]} timeout="auto" unmountOnExit>
                  <List component="div" disablePadding>
                    {subjectConvs.map(conv => (
                      <ListItem
                        key={conv.id}
                        disablePadding
                        secondaryAction={
                          <IconButton
                            edge="end"
                            size="small"
                            onClick={() => deleteConversation(conv.id)}
                            sx={{ color: '#666', '&:hover': { color: '#F44336' } }}
                          >
                            <Delete fontSize="small" />
                          </IconButton>
                        }
                        sx={{ pl: 2 }}
                      >
                        <ListItemButton
                          selected={conv.id === currentConvId}
                          onClick={() => switchConversation(conv.id)}
                          sx={{
                            borderRadius: 1,
                            mb: 0.5,
                            border: '1px solid transparent',
                            '&.Mui-selected': { 
                              bgcolor: 'white',
                              border: '1px solid #1976D2',
                              '&:hover': { bgcolor: 'white' }
                            },
                            '&:hover': { bgcolor: '#F5F5F5' }
                          }}
                        >
                          <Chat sx={{ mr: 1, fontSize: 16, color: '#666' }} />
                          <ListItemText
                            primary={conv.title}
                            primaryTypographyProps={{ fontSize: 13, noWrap: true }}
                          />
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </List>
                </Collapse>
              </Box>
            );
          })}
        </List>
      </Drawer>

      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', bgcolor: '#F5F5F5' }}>
        <Box sx={{ bgcolor: '#1976D2', color: 'white', p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton onClick={() => setSidebarOpen(!sidebarOpen)} sx={{ color: 'white' }}>
              <Menu />
            </IconButton>
            <Typography variant="h6" sx={{ cursor: 'pointer' }} onClick={onBackToHome}>Academic Doubt Clarification</Typography>
            {getCurrentSubject() && (
              <Chip
                icon={<School />}
                label={getCurrentSubject().name}
                sx={{ bgcolor: 'white', color: '#1976D2', fontWeight: 'bold' }}
              />
            )}
          </Box>
          <Box sx={{ display: 'flex', gap: 3, alignItems: 'center' }}>
            <FormControlLabel
              control={<Switch checked={showSteps} onChange={(e) => setShowSteps(e.target.checked)} sx={{ '& .MuiSwitch-switchBase.Mui-checked': { color: 'white' } }} />}
              label="Show Steps"
              sx={{ color: 'white', m: 0 }}
            />
            <FormControlLabel
              control={<Switch checked={comparisonMode} onChange={(e) => setComparisonMode(e.target.checked)} sx={{ '& .MuiSwitch-switchBase.Mui-checked': { color: 'white' } }} />}
              label="Compare Mode"
              sx={{ color: 'white', m: 0 }}
            />
            <Button
              variant="contained"
              size="small"
              component="a"
              href="/?admin=true"
              sx={{ bgcolor: 'white', color: '#1976D2', '&:hover': { bgcolor: '#E3F2FD' }, textDecoration: 'none' }}
            >
              Admin Panel
            </Button>
          </Box>
        </Box>
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {messages.map((msg, idx) => (
            <Box key={idx} sx={{ display: 'flex', justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start', mb: 2 }}>
              {msg.type === 'user' ? (
                <Paper sx={{ p: 2, maxWidth: '70%', bgcolor: '#E3F2FD', borderRadius: 2 }}>
                  <Typography>{msg.text}</Typography>
                </Paper>
              ) : msg.type === 'welcome' ? (
                <Box sx={{ width: '100%', textAlign: 'center', py: 4 }}>
                  <Paper sx={{ p: 4, maxWidth: 600, mx: 'auto', bgcolor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: 3, boxShadow: 3 }}>
                    <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#1976D2', mb: 1 }}>
                      {msg.data.title}
                    </Typography>
                    <Typography variant="body1" sx={{ color: '#666', mb: 3 }}>
                      {msg.data.subtitle}
                    </Typography>
                    <Typography variant="subtitle2" sx={{ color: '#888', mb: 2, fontWeight: 500 }}>
                      Try asking:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, justifyContent: 'center' }}>
                      {msg.data.suggestions.map((suggestion, i) => (
                        <Chip
                          key={i}
                          label={suggestion}
                          onClick={() => setInput(suggestion)}
                          sx={{ 
                            cursor: 'pointer',
                            bgcolor: 'white',
                            border: '1px solid #E0E0E0',
                            '&:hover': { bgcolor: '#E3F2FD', borderColor: '#1976D2' },
                            transition: 'all 0.2s'
                          }}
                        />
                      ))}
                    </Box>
                  </Paper>
                </Box>
              ) : msg.comparison ? (
                <Box sx={{ display: 'flex', gap: 2, width: '100%' }}>
                  <Paper sx={{ p: 2, flex: 1, bgcolor: '#FFF3E0', borderRadius: 2, border: '2px solid #FF9800' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1, color: '#E65100' }}>Basic RAG (No Validation)</Typography>
                    <Box sx={{ mb: 2, '& p': { mb: 1, lineHeight: 1.7 }, '& ol, & ul': { pl: 3 }, '& li': { mb: 0.5 }, '& strong': { fontWeight: 600 } }}>
                      <ReactMarkdown>{String(msg.comparison.answer || '')}</ReactMarkdown>
                    </Box>
                    <Typography variant="caption" sx={{ color: '#666', display: 'block', mt: 1 }}>Latency: {msg.comparison.latency_ms?.toFixed(0)}ms</Typography>
                  </Paper>
                  <Paper sx={{ p: 2, flex: 1, bgcolor: '#E8F5E9', borderRadius: 2, border: '2px solid #4CAF50' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1, color: '#2E7D32' }}>3-Layer Validated System</Typography>
                    <Chip label={msg.data.final_status} sx={{ bgcolor: getStatusColor(msg.data.final_status), color: 'white', mb: 1 }} size="small" />
                    <Box sx={{ mb: 2, '& p': { mb: 1, lineHeight: 1.7 }, '& ol, & ul': { pl: 3 }, '& li': { mb: 0.5 }, '& strong': { fontWeight: 600 } }}>
                      <ReactMarkdown>{String(msg.data.answer || msg.data.explanation || msg.data.message || '')}</ReactMarkdown>
                    </Box>
                    {msg.data.answer && (
                      <Button
                        size="small"
                        startIcon={voiceLoading === idx ? null : <VolumeUp />}
                        onClick={() => handleVoiceExplain(msg.data.question || '', msg.data.answer, idx)}
                        sx={{ mb: 1, color: '#2E7D32' }}
                      >
                        {voiceLoading === idx ? 'Generating...' : playingAudio ? 'Stop' : '🔊 Explain'}
                      </Button>
                    )}
                    {msg.data.sources && msg.data.sources.length > 0 && (
                      <Box sx={{ mt: 2, p: 1.5, bgcolor: '#F1F8E9', borderRadius: 1 }}>
                        <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block', mb: 1, color: '#2E7D32' }}>📚 Sources:</Typography>
                        {msg.data.sources.map((source, idx) => (
                          <Typography key={idx} variant="caption" sx={{ display: 'block', color: '#666', mb: 0.5 }}>
                            • {typeof source === 'string' ? source : source.source || source.path || JSON.stringify(source)}
                          </Typography>
                        ))}
                      </Box>
                    )}
                    {msg.data.warning && (
                      <Box sx={{ mb: 1, p: 1, bgcolor: '#FFF3E0', borderRadius: 1 }}>
                        <Typography variant="caption" sx={{ color: '#E65100' }}>⚠️ {msg.data.warning}</Typography>
                      </Box>
                    )}
                  </Paper>
                </Box>
              ) : (
                <Paper sx={{ p: 2, maxWidth: '70%', bgcolor: 'white', borderRadius: 2 }}>
                  <>
                    <Chip 
                      label={msg.data.status || msg.data.final_status} 
                      sx={{ bgcolor: getStatusColor(msg.data.status || msg.data.final_status), color: 'white', mb: 1 }} 
                      size="small" 
                    />
                    
                    {msg.data.intermediate_steps && (
                      <Accordion sx={{ mb: 2, boxShadow: 'none', border: '1px solid #E0E0E0' }}>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Intermediate Steps</Typography>
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
                            <Box sx={{ mb: 2, p: 1.5, bgcolor: '#F5F5F5', borderRadius: 1 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                {getStepIcon(msg.data.intermediate_steps.layer3.status)}
                                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                  Layer 3 - {msg.data.intermediate_steps.layer3.name || 'RAG Pipeline'}
                                </Typography>
                                {msg.data.confidence_score !== undefined && (
                                  <Box sx={{ ml: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 0.5 }}>
                                    <Box sx={{ display: 'flex', gap: 0.3 }}>
                                      {[1, 2, 3, 4, 5].map((block) => {
                                        const score = msg.data.confidence_score;
                                        const filled = score > ((block - 1) * 0.2);
                                        let color = '#E0E0E0';
                                        if (filled) {
                                          if (score >= 0.8) color = '#4CAF50';
                                          else if (score >= 0.6) color = '#FF9800';
                                          else color = '#F44336';
                                        }
                                        return (
                                          <Box
                                            key={block}
                                            sx={{
                                              width: 12,
                                              height: 24,
                                              bgcolor: color,
                                              borderRadius: 0.5,
                                              transition: 'all 0.3s'
                                            }}
                                          />
                                        );
                                      })}
                                    </Box>
                                    <Typography variant="caption" sx={{ fontSize: '0.65rem', color: '#666', fontWeight: 'bold' }}>
                                      {msg.data.confidence_score >= 0.8 ? 'High' : msg.data.confidence_score >= 0.6 ? 'Medium' : 'Low'} Confidence
                                    </Typography>
                                  </Box>
                                )}
                              </Box>
                              <Typography variant="caption" sx={{ display: 'block', color: '#666' }}>
                                {msg.data.intermediate_steps.layer3.description}
                              </Typography>
                              <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                                Status: {msg.data.intermediate_steps.layer3.status} | 
                                Latency: {msg.data.intermediate_steps.layer3.latency_ms?.toFixed(2)}ms
                              </Typography>
                              {msg.data.confidence_score !== undefined && msg.data.confidence_score < 0.6 && (
                                <Box sx={{ mt: 1, p: 1, bgcolor: '#FFEBEE', borderRadius: 1, border: '1px solid #F44336' }}>
                                  <Typography variant="caption" sx={{ color: '#C62828', fontWeight: 'bold' }}>
                                    ⚠️ Low confidence - Please verify with professor or textbook
                                  </Typography>
                                </Box>
                              )}
                            </Box>
                          )}
                          
                          {msg.data.context && (
                            <Box sx={{ mb: 2, p: 1.5, bgcolor: '#E3F2FD', borderRadius: 1, border: '1px solid #BBDEFB' }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1, color: '#1565C0' }}>
                                📄 Retrieved Context from PDFs
                              </Typography>
                              <Typography variant="caption" sx={{ color: '#666', mb: 1, display: 'block', fontStyle: 'italic' }}>
                                Actual text from course materials used to generate the answer:
                              </Typography>
                              <Box sx={{ bgcolor: 'white', p: 1.5, borderRadius: 1, maxHeight: 250, overflow: 'auto', border: '1px solid #BBDEFB' }}>
                                <Typography variant="caption" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.7rem', lineHeight: 1.5 }}>
                                  {msg.data.context}
                                </Typography>
                              </Box>
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
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ '& p': { mb: 1.5, lineHeight: 1.7 }, '& ol, & ul': { pl: 3, mb: 1.5 }, '& li': { mb: 0.5 }, '& strong': { fontWeight: 600 }, '& code': { bgcolor: '#F5F5F5', px: 0.5, borderRadius: 0.5, fontFamily: 'monospace', fontSize: '0.85em' }, '& pre': { bgcolor: '#F5F5F5', p: 2, borderRadius: 1, fontFamily: 'monospace', whiteSpace: 'pre-wrap', overflowX: 'auto', my: 1.5 } }}>
                          <ReactMarkdown>
                            {String(msg.data.answer || msg.data.explanation || msg.data.message || '')}
                          </ReactMarkdown>
                        </Box>
                        {msg.data.sources && msg.data.sources.length > 0 && (
                          <Box sx={{ mt: 2, p: 1.5, bgcolor: '#F0F0F0', borderRadius: 1 }}>
                            <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block', mb: 1, color: '#1976D2' }}>📚 Sources:</Typography>
                            {msg.data.sources.map((source, idx) => (
                              <Typography key={idx} variant="caption" sx={{ display: 'block', color: '#666', mb: 0.5 }}>
                                • {typeof source === 'string' ? source : source.source || source.path || JSON.stringify(source)}
                              </Typography>
                            ))}
                          </Box>
                        )}
                      </Box>
                      {(msg.data.answer || msg.data.explanation) && (
                        <Box sx={{ display: 'flex', flexDirection: 'column', ml: 1, gap: 0.5 }}>
                          <IconButton 
                            size="small" 
                            onClick={() => copyToClipboard(msg.data.answer || msg.data.explanation)}
                          >
                            <ContentCopy fontSize="small" />
                          </IconButton>
                          {(msg.data.status === 'success' || msg.data.final_status === 'VALID') && msg.data.answer && (
                            <IconButton
                              size="small"
                              onClick={() => handleVoiceExplain(msg.data.question || '', msg.data.answer, idx)}
                              sx={{ color: playingAudio && voiceLoading === null && idx === messages.indexOf(msg) ? '#4CAF50' : '#1976D2' }}
                            >
                              {voiceLoading === idx ? (
                                <Box sx={{ width: 18, height: 18, border: '2px solid #BBDEFB', borderTop: '2px solid #1976D2', borderRadius: '50%', animation: 'spin 0.8s linear infinite', '@keyframes spin': { '0%': { transform: 'rotate(0deg)' }, '100%': { transform: 'rotate(360deg)' } } }} />
                              ) : (
                                <VolumeUp fontSize="small" />
                              )}
                            </IconButton>
                          )}
                        </Box>
                      )}
                    </Box>
                    
                    {msg.data.suggestions && msg.data.suggestions.length > 0 && (
                      <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {msg.data.suggestions.map((suggestion, idx) => (
                          <Chip
                            key={idx}
                            label={suggestion}
                            onClick={() => setInput(suggestion)}
                            sx={{ 
                              cursor: 'pointer',
                              '&:hover': { bgcolor: '#E3F2FD' }
                            }}
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    )}
                    
                    {msg.data.final_status === 'OUT_OF_SYLLABUS' && (
                      <Box sx={{ mt: 2 }}>
                        <Button 
                          variant="outlined" 
                          size="small" 
                          onClick={() => handleAnswerAnyway(msg.data.question)}
                          sx={{ borderColor: '#FF9800', color: '#FF9800' }}
                        >
                          Answer Anyway (Not in {getCurrentSubject()?.name || 'course'} syllabus)
                        </Button>
                      </Box>
                    )}
                    

                    
                    {msg.data.warning && (
                      <Box sx={{ mt: 1, p: 1, bgcolor: '#FFF3E0', borderRadius: 1, borderLeft: '4px solid #FF9800' }}>
                        <Typography variant="caption" sx={{ color: '#E65100', fontWeight: 'bold' }}>
                          Warning: {msg.data.warning}
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
                </Paper>
              )}
            </Box>
          ))}
        </Box>
        <Box sx={{ p: 2, bgcolor: 'white', borderTop: '1px solid #E0E0E0' }}>
          <Box sx={{ mb: 1.5, p: 1, bgcolor: '#FFF3E0', borderRadius: 1, border: '1px solid #FFE0B2' }}>
            <Typography variant="caption" sx={{ color: '#E65100', display: 'flex', alignItems: 'center', gap: 0.5 }}>
              ⚠️ AI-generated answers are based on uploaded course materials. Always verify important concepts with your professor or textbook.
            </Typography>
          </Box>
          {loading && loadingStage && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5, p: 1.5, bgcolor: '#E3F2FD', borderRadius: 2, border: '1px solid #BBDEFB' }}>
              <Box sx={{ 
                width: 20, 
                height: 20, 
                border: '3px solid #BBDEFB', 
                borderTop: '3px solid #1976D2', 
                borderRadius: '50%', 
                animation: 'spin 0.8s linear infinite',
                '@keyframes spin': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' }
                }
              }} />
              <Typography variant="body2" sx={{ color: '#1565C0', fontWeight: 500 }}>{loadingStage}</Typography>
            </Box>
          )}
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField fullWidth value={input} onChange={(e) => { setInput(e.target.value); inputRef.current = e.target.value; }} onKeyPress={(e) => e.key === 'Enter' && sendMessage()} placeholder="Ask your doubt..." disabled={loading} sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
            <IconButton onClick={handleVoiceInput} disabled={loading} sx={{ color: isListening ? '#F44336' : '#1976D2', animation: isListening ? 'pulse 1s infinite' : 'none', '@keyframes pulse': { '0%': { transform: 'scale(1)' }, '50%': { transform: 'scale(1.2)' }, '100%': { transform: 'scale(1)' } } }}>
              {isListening ? <MicOff /> : <Mic />}
            </IconButton>
            <Button variant="contained" onClick={() => sendMessage()} disabled={loading} sx={{ borderRadius: 2, bgcolor: '#1976D2' }}><Send /></Button>
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
