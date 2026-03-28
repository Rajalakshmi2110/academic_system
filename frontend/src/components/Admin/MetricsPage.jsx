import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Grid, Card, CardContent, Button, Drawer, List, ListItemButton, ListItemText, FormControl, Select, MenuItem, Divider } from '@mui/material';
import { TrendingUp, Assessment, Speed, Logout, Dashboard as DashboardIcon, Add } from '@mui/icons-material';
import axios from 'axios';

const MetricsPage = ({ onSwitchTab, onLogout, selectedSubject }) => {
  const [metrics, setMetrics] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [currentSubject, setCurrentSubject] = useState(selectedSubject || 'data_structures');

  useEffect(() => {
    loadSubjects();
  }, []);

  useEffect(() => {
    if (currentSubject) {
      fetchMetrics();
    }
  }, [currentSubject]);

  const loadSubjects = async () => {
    try {
      const res = await axios.get('http://localhost:5001/api/subjects/list');
      setSubjects(res.data.subjects || []);
      if (res.data.subjects.length > 0 && !currentSubject) {
        setCurrentSubject(res.data.subjects[0].id);
      }
    } catch (err) {
      console.error('Failed to load subjects:', err);
    }
  };

  const fetchMetrics = async () => {
    try {
      const res = await axios.get(`http://localhost:5001/api/metrics?subject_id=${currentSubject}`);
      setMetrics(res.data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      setMetrics(null);
    }
  };

  if (!metrics) return <Box sx={{ p: 4 }}><Typography>Loading metrics...</Typography></Box>;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
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
                  {subject.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
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

      <Box sx={{ flex: 1, bgcolor: '#F5F7FA' }}>
        <Box sx={{ bgcolor: 'white', p: 2, borderBottom: '1px solid #E0E0E0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5">Metrics - {subjects.find(s => s.id === currentSubject)?.name || 'Loading...'}</Typography>
          <Button variant="outlined" size="small" onClick={fetchMetrics}>Refresh</Button>
        </Box>
        <Box sx={{ p: 4 }}>

      {/* Usage Metrics (Real-time) */}
      <Paper elevation={0} sx={{ p: 4, mb: 3, borderRadius: 3, border: '1px solid #E2E8F0' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Box sx={{ bgcolor: '#10B981', p: 1.5, borderRadius: 2 }}>
            <TrendingUp sx={{ color: 'white', fontSize: 28 }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1A202C' }}>Usage Metrics</Typography>
            <Typography variant="caption" color="text.secondary">Real-time student activity</Typography>
          </Box>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={2.4}>
            <Card elevation={0} sx={{ bgcolor: '#EFF6FF', border: '1px solid #DBEAFE', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#3B82F6', fontWeight: 700 }}>{metrics.usage?.total_questions || 0}</Typography>
                <Typography variant="caption" sx={{ color: '#1E40AF', fontWeight: 600, textTransform: 'uppercase' }}>Total Questions</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={2.4}>
            <Card elevation={0} sx={{ bgcolor: '#ECFDF5', border: '1px solid #D1FAE5', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#10B981', fontWeight: 700 }}>{metrics.usage?.today || 0}</Typography>
                <Typography variant="caption" sx={{ color: '#065F46', fontWeight: 600, textTransform: 'uppercase' }}>Today</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={2.4}>
            <Card elevation={0} sx={{ bgcolor: '#FEF3C7', border: '1px solid #FDE68A', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#F59E0B', fontWeight: 700 }}>{metrics.usage?.this_week || 0}</Typography>
                <Typography variant="caption" sx={{ color: '#92400E', fontWeight: 600, textTransform: 'uppercase' }}>This Week</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={2.4}>
            <Card elevation={0} sx={{ bgcolor: '#F5F3FF', border: '1px solid #E9D5FF', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#8B5CF6', fontWeight: 700 }}>{metrics.usage?.avg_confidence ? (metrics.usage.avg_confidence * 100).toFixed(0) + '%' : 'N/A'}</Typography>
                <Typography variant="caption" sx={{ color: '#5B21B6', fontWeight: 600, textTransform: 'uppercase' }}>Avg Confidence</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={2.4}>
            <Card elevation={0} sx={{ bgcolor: '#FEE2E2', border: '1px solid #FECACA', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#EF4444', fontWeight: 700 }}>{metrics.usage?.low_confidence_count || 0}</Typography>
                <Typography variant="caption" sx={{ color: '#991B1B', fontWeight: 600, textTransform: 'uppercase' }}>Low Confidence</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        <Typography variant="caption" sx={{ mt: 2, display: 'block', color: 'text.secondary' }}>
          Avg Response Time: {metrics.usage?.avg_latency_ms ? (metrics.usage.avg_latency_ms / 1000).toFixed(2) + 's' : 'N/A'}
        </Typography>
      </Paper>

      {/* Quality Metrics (Feedback) */}
      <Paper elevation={0} sx={{ p: 4, mb: 3, borderRadius: 3, border: '1px solid #E2E8F0' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Box sx={{ bgcolor: '#3B82F6', p: 1.5, borderRadius: 2 }}>
            <Assessment sx={{ color: 'white', fontSize: 28 }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1A202C' }}>Quality Metrics</Typography>
            <Typography variant="caption" color="text.secondary">Student feedback</Typography>
          </Box>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#ECFDF5', border: '1px solid #D1FAE5', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#10B981', fontWeight: 700 }}>{metrics.feedback?.helpful_rate || 0}%</Typography>
                <Typography variant="caption" sx={{ color: '#065F46', fontWeight: 600, textTransform: 'uppercase' }}>Helpful Rate</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#EFF6FF', border: '1px solid #DBEAFE', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#3B82F6', fontWeight: 700 }}>{metrics.feedback?.helpful || 0}</Typography>
                <Typography variant="caption" sx={{ color: '#1E40AF', fontWeight: 600, textTransform: 'uppercase' }}>👍 Helpful</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#FEE2E2', border: '1px solid #FECACA', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#EF4444', fontWeight: 700 }}>{metrics.feedback?.not_helpful || 0}</Typography>
                <Typography variant="caption" sx={{ color: '#991B1B', fontWeight: 600, textTransform: 'uppercase' }}>👎 Not Helpful</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#F1F5F9', border: '1px solid #E2E8F0', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#64748B', fontWeight: 700 }}>{metrics.feedback?.total || 0}</Typography>
                <Typography variant="caption" sx={{ color: '#475569', fontWeight: 600, textTransform: 'uppercase' }}>Total Feedback</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Layer Performance */}
      <Paper elevation={0} sx={{ p: 4, mb: 3, borderRadius: 3, border: '1px solid #E2E8F0' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Box sx={{ bgcolor: '#F59E0B', p: 1.5, borderRadius: 2 }}>
            <Speed sx={{ color: 'white', fontSize: 28 }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1A202C' }}>Layer Performance</Typography>
            <Typography variant="caption" color="text.secondary">Validation pipeline breakdown</Typography>
          </Box>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={6}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: '#1A202C' }}>Layer 1 - Subject Classifier</Typography>
            <Box sx={{ mb: 1, p: 2, bgcolor: '#F8FAFC', borderRadius: 2, border: '1px solid #E2E8F0' }}>
              <Typography variant="caption" sx={{ color: '#64748B', display: 'block', mb: 1 }}>Filters out irrelevant questions</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="h4" sx={{ color: '#10B981', fontWeight: 700 }}>{metrics.layer1?.pass || 0}</Typography>
                <Typography variant="body2" sx={{ color: '#065F46' }}>relevant questions passed</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                <Typography variant="h4" sx={{ color: '#64748B', fontWeight: 700 }}>{metrics.layer1?.fail || 0}</Typography>
                <Typography variant="body2" sx={{ color: '#475569' }}>off-topic questions filtered</Typography>
              </Box>
              <Box sx={{ mt: 2, p: 1.5, bgcolor: metrics.layer1?.pass_rate >= 50 ? '#ECFDF5' : '#FEF3C7', borderRadius: 1, border: `1px solid ${metrics.layer1?.pass_rate >= 50 ? '#D1FAE5' : '#FDE68A'}` }}>
                <Typography variant="h5" sx={{ color: metrics.layer1?.pass_rate >= 50 ? '#10B981' : '#F59E0B', fontWeight: 700, textAlign: 'center' }}>
                  {metrics.layer1?.pass_rate || 0}% Pass Rate
                </Typography>
              </Box>
              <Typography variant="caption" sx={{ mt: 1, display: 'block', color: '#64748B' }}>Avg Latency: {metrics.layer1?.avg_latency_ms || 0}ms</Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: '#1A202C' }}>Layer 2 - Syllabus Validator</Typography>
            <Box sx={{ mb: 1, p: 2, bgcolor: '#F8FAFC', borderRadius: 2, border: '1px solid #E2E8F0' }}>
              <Typography variant="caption" sx={{ color: '#64748B', display: 'block', mb: 1 }}>Validates syllabus alignment</Typography>
              <Grid container spacing={1}>
                <Grid item xs={6}>
                  <Box sx={{ p: 1.5, bgcolor: '#ECFDF5', borderRadius: 1, border: '1px solid #D1FAE5', textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: '#10B981', fontWeight: 700 }}>{metrics.layer2?.valid || 0}</Typography>
                    <Typography variant="caption" sx={{ color: '#065F46', fontWeight: 600 }}>✓ VALID</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ p: 1.5, bgcolor: '#FEF3C7', borderRadius: 1, border: '1px solid #FDE68A', textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: '#F59E0B', fontWeight: 700 }}>{metrics.layer2?.warning || 0}</Typography>
                    <Typography variant="caption" sx={{ color: '#92400E', fontWeight: 600 }}>⚠ WARNING</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ p: 1.5, bgcolor: '#F1F5F9', borderRadius: 1, border: '1px solid #E2E8F0', textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: '#64748B', fontWeight: 700 }}>{metrics.layer2?.out_of_syllabus || 0}</Typography>
                    <Typography variant="caption" sx={{ color: '#475569', fontWeight: 600 }}>○ OUT</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ p: 1.5, bgcolor: '#FEE2E2', borderRadius: 1, border: '1px solid #FECACA', textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: '#EF4444', fontWeight: 700 }}>{metrics.layer2?.rejected || 0}</Typography>
                    <Typography variant="caption" sx={{ color: '#991B1B', fontWeight: 600 }}>✕ REJECT</Typography>
                  </Box>
                </Grid>
              </Grid>
              <Typography variant="caption" sx={{ mt: 1, display: 'block', color: '#64748B' }}>Avg Latency: {metrics.layer2?.avg_latency_ms || 0}ms</Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Layer 3 + Latency Breakdown */}
      <Paper elevation={0} sx={{ p: 4, mb: 3, borderRadius: 3, border: '1px solid #E2E8F0' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Box sx={{ bgcolor: '#8B5CF6', p: 1.5, borderRadius: 2 }}>
            <Speed sx={{ color: 'white', fontSize: 28 }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1A202C' }}>Layer 3 - RAG Pipeline</Typography>
            <Typography variant="caption" color="text.secondary">Answer generation performance</Typography>
          </Box>
        </Box>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#ECFDF5', border: '1px solid #D1FAE5', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#10B981', fontWeight: 700 }}>{metrics.layer3?.success || 0}</Typography>
                <Typography variant="caption" sx={{ color: '#065F46', fontWeight: 600, textTransform: 'uppercase' }}>Answers Generated</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#FEE2E2', border: '1px solid #FECACA', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#EF4444', fontWeight: 700 }}>{metrics.layer3?.error || 0}</Typography>
                <Typography variant="caption" sx={{ color: '#991B1B', fontWeight: 600, textTransform: 'uppercase' }}>Errors</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#F5F3FF', border: '1px solid #E9D5FF', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#8B5CF6', fontWeight: 700 }}>{metrics.layer3?.success_rate || 0}%</Typography>
                <Typography variant="caption" sx={{ color: '#5B21B6', fontWeight: 600, textTransform: 'uppercase' }}>Success Rate</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#EFF6FF', border: '1px solid #DBEAFE', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#3B82F6', fontWeight: 700 }}>{metrics.layer3?.avg_latency_ms ? (metrics.layer3.avg_latency_ms / 1000).toFixed(1) + 's' : 'N/A'}</Typography>
                <Typography variant="caption" sx={{ color: '#1E40AF', fontWeight: 600, textTransform: 'uppercase' }}>Avg Latency</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Latency Breakdown Bar */}
        <Box sx={{ mt: 3, p: 2, bgcolor: '#F8FAFC', borderRadius: 2, border: '1px solid #E2E8F0' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5 }}>Latency Breakdown (avg per layer)</Typography>
          {[{ label: 'Layer 1 - Classifier', ms: metrics.layer1?.avg_latency_ms, color: '#10B981' },
            { label: 'Layer 2 - Validator', ms: metrics.layer2?.avg_latency_ms, color: '#F59E0B' },
            { label: 'Layer 3 - RAG', ms: metrics.layer3?.avg_latency_ms, color: '#8B5CF6' }].map((layer, i) => {
            const maxMs = Math.max(metrics.layer1?.avg_latency_ms || 0, metrics.layer2?.avg_latency_ms || 0, metrics.layer3?.avg_latency_ms || 1);
            const pct = layer.ms ? Math.max((layer.ms / maxMs) * 100, 2) : 0;
            return (
              <Box key={i} sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="caption" sx={{ fontWeight: 600 }}>{layer.label}</Typography>
                  <Typography variant="caption" sx={{ color: '#64748B' }}>{layer.ms ? (layer.ms < 1000 ? layer.ms.toFixed(0) + 'ms' : (layer.ms / 1000).toFixed(2) + 's') : 'N/A'}</Typography>
                </Box>
                <Box sx={{ height: 8, bgcolor: '#E2E8F0', borderRadius: 4 }}>
                  <Box sx={{ height: 8, width: `${pct}%`, bgcolor: layer.color, borderRadius: 4, transition: 'width 0.5s' }} />
                </Box>
              </Box>
            );
          })}
        </Box>
      </Paper>

      {/* Hourly Distribution */}
      {metrics.hourly_stats && Object.keys(metrics.hourly_stats).length > 0 && (
        <Paper elevation={0} sx={{ p: 4, mb: 3, borderRadius: 3, border: '1px solid #E2E8F0' }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: '#1A202C' }}>Hourly Distribution</Typography>
          <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 0.5, height: 120 }}>
            {Array.from({ length: 24 }, (_, h) => {
              const count = metrics.hourly_stats[String(h)] || 0;
              const maxCount = Math.max(...Object.values(metrics.hourly_stats), 1);
              const heightPct = Math.max((count / maxCount) * 100, 2);
              return (
                <Box key={h} sx={{ flex: 1, textAlign: 'center' }}>
                  <Typography variant="caption" sx={{ fontSize: '0.6rem', color: '#64748B' }}>{count || ''}</Typography>
                  <Box sx={{ height: `${heightPct}%`, minHeight: 2, bgcolor: count > 0 ? '#3B82F6' : '#E2E8F0', borderRadius: '4px 4px 0 0', mx: 'auto', width: '80%' }} />
                  <Typography variant="caption" sx={{ fontSize: '0.55rem', color: '#94A3B8' }}>{h}</Typography>
                </Box>
              );
            })}
          </Box>
          <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', mt: 1, color: '#94A3B8' }}>Hour of day (0-23)</Typography>
        </Paper>
      )}

      {metrics.last_updated && (
        <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', color: 'text.secondary', mt: 2 }}>
          Last updated: {new Date(metrics.last_updated).toLocaleString()}
        </Typography>
      )}
        </Box>
      </Box>
    </Box>
  );
};

export default MetricsPage;
