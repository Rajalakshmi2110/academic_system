import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Grid, Card, CardContent, Button, Drawer, List, ListItemButton, ListItemText, FormControl, Select, MenuItem, Divider, LinearProgress } from '@mui/material';
import { TrendingUp, Assessment, Speed, Logout, Dashboard as DashboardIcon, Add, FilterDrama, CheckCircle, Warning, Block, Cancel } from '@mui/icons-material';
import axios from 'axios';

const MetricsPage = ({ onSwitchTab, onLogout, selectedSubject }) => {
  const [metrics, setMetrics] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [currentSubject, setCurrentSubject] = useState(selectedSubject || 'overall');

  useEffect(() => { loadSubjects(); }, []);
  useEffect(() => { if (currentSubject) fetchMetrics(); }, [currentSubject]);

  const loadSubjects = async () => {
    try {
      const res = await axios.get('http://localhost:5001/api/subjects/list');
      setSubjects(res.data.subjects || []);
    } catch (err) { console.error('Failed to load subjects:', err); }
  };

  const fetchMetrics = async () => {
    try {
      const res = await axios.get(`http://localhost:5001/api/metrics?subject_id=${currentSubject}`);
      setMetrics(res.data);
    } catch (error) { console.error('Failed to fetch metrics:', error); setMetrics(null); }
  };

  const StatCard = ({ value, label, color, bgColor, borderColor, icon }) => (
    <Card elevation={0} sx={{ bgcolor: bgColor, border: `1px solid ${borderColor}`, borderRadius: 2, textAlign: 'center', height: '100%' }}>
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        {icon && <Box sx={{ mb: 0.5 }}>{icon}</Box>}
        <Typography variant="h3" sx={{ color, fontWeight: 700, lineHeight: 1.2 }}>{value}</Typography>
        <Typography variant="caption" sx={{ color, fontWeight: 600, textTransform: 'uppercase', opacity: 0.8 }}>{label}</Typography>
      </CardContent>
    </Card>
  );

  const LatencyBar = ({ label, ms, color, maxMs }) => {
    const pct = ms && maxMs ? Math.max((ms / maxMs) * 100, 3) : 0;
    const display = ms ? (ms < 1000 ? ms.toFixed(0) + 'ms' : (ms / 1000).toFixed(2) + 's') : '—';
    return (
      <Box sx={{ mb: 1.5 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="body2" sx={{ fontWeight: 600, color: '#334155' }}>{label}</Typography>
          <Typography variant="body2" sx={{ fontWeight: 700, color }}>{display}</Typography>
        </Box>
        <Box sx={{ height: 10, bgcolor: '#F1F5F9', borderRadius: 5, overflow: 'hidden' }}>
          <Box sx={{ height: 10, width: `${pct}%`, bgcolor: color, borderRadius: 5, transition: 'width 0.6s ease' }} />
        </Box>
      </Box>
    );
  };

  if (!metrics) return <Box sx={{ p: 4 }}><Typography>Loading metrics...</Typography></Box>;

  const maxLatency = Math.max(metrics.layer1?.avg_latency_ms || 0, metrics.layer2?.avg_latency_ms || 0, metrics.layer3?.avg_latency_ms || 1);
  const totalQuestions = metrics.usage?.total_questions || 0;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Drawer variant="permanent" sx={{ width: 260, flexShrink: 0, '& .MuiDrawer-paper': { width: 260, boxSizing: 'border-box', bgcolor: '#1976D2', color: 'white' } }}>
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>Admin Panel</Typography>
          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <Select value={currentSubject} onChange={(e) => setCurrentSubject(e.target.value)} sx={{ bgcolor: 'white', borderRadius: 1 }}>
              <MenuItem value="overall"><strong>Overall</strong></MenuItem>
              {subjects.map(s => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
            </Select>
          </FormControl>
        </Box>
        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
        <List>
          <ListItemButton onClick={() => onSwitchTab(0)} sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}><DashboardIcon sx={{ mr: 2 }} /><ListItemText primary="Dashboard" /></ListItemButton>
          <ListItemButton selected sx={{ color: 'white', bgcolor: 'rgba(255,255,255,0.15)', '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' } }}><Assessment sx={{ mr: 2 }} /><ListItemText primary="Metrics" /></ListItemButton>
          <ListItemButton onClick={() => onSwitchTab(2)} sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}><Add sx={{ mr: 2 }} /><ListItemText primary="Add Subject" /></ListItemButton>
        </List>
        <Box sx={{ flexGrow: 1 }} />
        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
        <List><ListItemButton onClick={onLogout} sx={{ color: 'white' }}><Logout sx={{ mr: 2 }} /><ListItemText primary="Logout" /></ListItemButton></List>
      </Drawer>

      <Box sx={{ flex: 1, bgcolor: '#F5F7FA' }}>
        <Box sx={{ bgcolor: 'white', p: 2, borderBottom: '1px solid #E0E0E0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            {currentSubject === 'overall' ? 'Overall Metrics' : `Metrics — ${subjects.find(s => s.id === currentSubject)?.name || ''}`}
          </Typography>
          <Button variant="outlined" size="small" onClick={fetchMetrics}>Refresh</Button>
        </Box>

        <Box sx={{ p: 3 }}>
          {/* Row 1: Usage Stats */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={2.4}><StatCard value={totalQuestions} label="Total Questions" color="#3B82F6" bgColor="#EFF6FF" borderColor="#DBEAFE" /></Grid>
            <Grid item xs={2.4}><StatCard value={metrics.usage?.today || 0} label="Today" color="#10B981" bgColor="#ECFDF5" borderColor="#D1FAE5" /></Grid>
            <Grid item xs={2.4}><StatCard value={metrics.usage?.this_week || 0} label="This Week" color="#F59E0B" bgColor="#FEF3C7" borderColor="#FDE68A" /></Grid>
            <Grid item xs={2.4}><StatCard value={metrics.usage?.avg_confidence ? (metrics.usage.avg_confidence * 100).toFixed(0) + '%' : '—'} label="Avg Confidence" color="#8B5CF6" bgColor="#F5F3FF" borderColor="#E9D5FF" /></Grid>
            <Grid item xs={2.4}><StatCard value={metrics.usage?.avg_latency_ms ? (metrics.usage.avg_latency_ms / 1000).toFixed(1) + 's' : '—'} label="Avg Response" color="#EC4899" bgColor="#FDF2F8" borderColor="#FCE7F3" /></Grid>
          </Grid>

          {/* Row 2: Pipeline Performance (All 3 Layers + Latency) */}
          <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 3, border: '1px solid #E2E8F0' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
              <Box sx={{ bgcolor: '#6366F1', p: 1, borderRadius: 1.5 }}><Speed sx={{ color: 'white', fontSize: 22 }} /></Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Pipeline Performance</Typography>
            </Box>

            <Grid container spacing={3}>
              {/* Layer 1 */}
              <Grid item xs={4}>
                <Box sx={{ p: 2.5, bgcolor: '#F0FDF4', borderRadius: 2, border: '1px solid #BBF7D0', height: '100%' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#166534', mb: 2 }}>Layer 1 — Subject Classifier</Typography>
                  <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                    <Box sx={{ textAlign: 'center', flex: 1 }}>
                      <Typography variant="h3" sx={{ color: '#16A34A', fontWeight: 700 }}>{metrics.layer1?.pass || 0}</Typography>
                      <Typography variant="caption" sx={{ color: '#166534' }}>✓ Passed</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center', flex: 1 }}>
                      <Typography variant="h3" sx={{ color: '#94A3B8', fontWeight: 700 }}>{metrics.layer1?.fail || 0}</Typography>
                      <Typography variant="caption" sx={{ color: '#64748B' }}>✕ Filtered</Typography>
                    </Box>
                  </Box>
                  <Box sx={{ p: 1.5, bgcolor: 'white', borderRadius: 1.5, textAlign: 'center' }}>
                    <Typography variant="h5" sx={{ color: '#16A34A', fontWeight: 700 }}>{metrics.layer1?.pass_rate || 0}%</Typography>
                    <Typography variant="caption" sx={{ color: '#64748B' }}>Pass Rate</Typography>
                  </Box>
                </Box>
              </Grid>

              {/* Layer 2 */}
              <Grid item xs={4}>
                <Box sx={{ p: 2.5, bgcolor: '#FFFBEB', borderRadius: 2, border: '1px solid #FDE68A', height: '100%' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#92400E', mb: 2 }}>Layer 2 — Syllabus Validator</Typography>
                  <Grid container spacing={1} sx={{ mb: 2 }}>
                    {[
                      { val: metrics.layer2?.valid || 0, label: 'Valid', color: '#16A34A', icon: <CheckCircle sx={{ fontSize: 14, color: '#16A34A' }} /> },
                      { val: metrics.layer2?.warning || 0, label: 'Warn', color: '#F59E0B', icon: <Warning sx={{ fontSize: 14, color: '#F59E0B' }} /> },
                      { val: metrics.layer2?.out_of_syllabus || 0, label: 'Out', color: '#94A3B8', icon: <Block sx={{ fontSize: 14, color: '#94A3B8' }} /> },
                      { val: metrics.layer2?.rejected || 0, label: 'Reject', color: '#EF4444', icon: <Cancel sx={{ fontSize: 14, color: '#EF4444' }} /> },
                    ].map((item, i) => (
                      <Grid item xs={6} key={i}>
                        <Box sx={{ p: 1, bgcolor: 'white', borderRadius: 1.5, textAlign: 'center' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                            {item.icon}
                            <Typography variant="h5" sx={{ color: item.color, fontWeight: 700 }}>{item.val}</Typography>
                          </Box>
                          <Typography variant="caption" sx={{ color: '#64748B', fontSize: '0.65rem' }}>{item.label}</Typography>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              </Grid>

              {/* Layer 3 */}
              <Grid item xs={4}>
                <Box sx={{ p: 2.5, bgcolor: '#F5F3FF', borderRadius: 2, border: '1px solid #DDD6FE', height: '100%' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#5B21B6', mb: 2 }}>Layer 3 — RAG Pipeline</Typography>
                  <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                    <Box sx={{ textAlign: 'center', flex: 1 }}>
                      <Typography variant="h3" sx={{ color: '#16A34A', fontWeight: 700 }}>{metrics.layer3?.success || 0}</Typography>
                      <Typography variant="caption" sx={{ color: '#166534' }}>Generated</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center', flex: 1 }}>
                      <Typography variant="h3" sx={{ color: '#EF4444', fontWeight: 700 }}>{metrics.layer3?.error || 0}</Typography>
                      <Typography variant="caption" sx={{ color: '#991B1B' }}>Errors</Typography>
                    </Box>
                  </Box>
                  <Box sx={{ p: 1.5, bgcolor: 'white', borderRadius: 1.5, textAlign: 'center' }}>
                    <Typography variant="h5" sx={{ color: '#7C3AED', fontWeight: 700 }}>{metrics.layer3?.success_rate || 0}%</Typography>
                    <Typography variant="caption" sx={{ color: '#64748B' }}>Success Rate</Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>

            {/* Latency Breakdown */}
            <Box sx={{ mt: 3, p: 2.5, bgcolor: '#F8FAFC', borderRadius: 2, border: '1px solid #E2E8F0' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: '#334155' }}>Latency Breakdown</Typography>
              <LatencyBar label="Layer 1 — Classifier" ms={metrics.layer1?.avg_latency_ms} color="#16A34A" maxMs={maxLatency} />
              <LatencyBar label="Layer 2 — Validator" ms={metrics.layer2?.avg_latency_ms} color="#F59E0B" maxMs={maxLatency} />
              <LatencyBar label="Layer 3 — RAG" ms={metrics.layer3?.avg_latency_ms} color="#7C3AED" maxMs={maxLatency} />
            </Box>
          </Paper>

          {/* Row 3: Feedback + Hourly side by side */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            {/* Feedback */}
            <Grid item xs={5}>
              <Paper elevation={0} sx={{ p: 3, borderRadius: 3, border: '1px solid #E2E8F0', height: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box sx={{ bgcolor: '#3B82F6', p: 1, borderRadius: 1.5 }}><Assessment sx={{ color: 'white', fontSize: 22 }} /></Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>Student Feedback</Typography>
                </Box>
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <Typography variant="h2" sx={{ color: '#10B981', fontWeight: 700 }}>{metrics.feedback?.helpful_rate || 0}%</Typography>
                  <Typography variant="body2" sx={{ color: '#64748B' }}>Helpful Rate</Typography>
                </Box>
                <Grid container spacing={1}>
                  <Grid item xs={4}>
                    <Box sx={{ p: 1.5, bgcolor: '#ECFDF5', borderRadius: 1.5, textAlign: 'center' }}>
                      <Typography variant="h5" sx={{ color: '#10B981', fontWeight: 700 }}>{metrics.feedback?.helpful || 0}</Typography>
                      <Typography variant="caption" sx={{ color: '#065F46' }}>Helpful</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box sx={{ p: 1.5, bgcolor: '#FEE2E2', borderRadius: 1.5, textAlign: 'center' }}>
                      <Typography variant="h5" sx={{ color: '#EF4444', fontWeight: 700 }}>{metrics.feedback?.not_helpful || 0}</Typography>
                      <Typography variant="caption" sx={{ color: '#991B1B' }}>Not Helpful</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box sx={{ p: 1.5, bgcolor: '#F1F5F9', borderRadius: 1.5, textAlign: 'center' }}>
                      <Typography variant="h5" sx={{ color: '#64748B', fontWeight: 700 }}>{metrics.feedback?.total || 0}</Typography>
                      <Typography variant="caption" sx={{ color: '#475569' }}>Total</Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>

            {/* Hourly Distribution */}
            <Grid item xs={7}>
              <Paper elevation={0} sx={{ p: 3, borderRadius: 3, border: '1px solid #E2E8F0', height: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box sx={{ bgcolor: '#EC4899', p: 1, borderRadius: 1.5 }}><TrendingUp sx={{ color: 'white', fontSize: 22 }} /></Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>Hourly Activity</Typography>
                </Box>
                {metrics.hourly_stats && Object.keys(metrics.hourly_stats).length > 0 ? (
                  <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: '2px', height: 140, pt: 2 }}>
                    {Array.from({ length: 24 }, (_, h) => {
                      const count = metrics.hourly_stats[String(h)] || 0;
                      const maxCount = Math.max(...Object.values(metrics.hourly_stats), 1);
                      const heightPct = count > 0 ? Math.max((count / maxCount) * 100, 8) : 3;
                      return (
                        <Box key={h} sx={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                          {count > 0 && <Typography sx={{ fontSize: '0.6rem', color: '#64748B', fontWeight: 600, mb: 0.3 }}>{count}</Typography>}
                          <Box sx={{ width: '70%', height: `${heightPct}%`, bgcolor: count > 0 ? '#6366F1' : '#E2E8F0', borderRadius: '3px 3px 0 0', transition: 'height 0.4s ease', minHeight: 3 }} />
                          <Typography sx={{ fontSize: '0.55rem', color: '#94A3B8', mt: 0.3 }}>{h}</Typography>
                        </Box>
                      );
                    })}
                  </Box>
                ) : (
                  <Box sx={{ height: 140, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography variant="body2" sx={{ color: '#94A3B8' }}>No activity data yet. Ask some questions first!</Typography>
                  </Box>
                )}
              </Paper>
            </Grid>
          </Grid>

          {/* Per-Subject Breakdown (Overall view only) */}
          {currentSubject === 'overall' && metrics.per_subject && (
            <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 3, border: '1px solid #E2E8F0' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                <Box sx={{ bgcolor: '#0EA5E9', p: 1, borderRadius: 1.5 }}><FilterDrama sx={{ color: 'white', fontSize: 22 }} /></Box>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>Per-Subject Breakdown</Typography>
              </Box>
              <Grid container spacing={2}>
                {Object.entries(metrics.per_subject).map(([sid, data]) => {
                  const name = subjects.find(s => s.id === sid)?.name || sid;
                  return (
                    <Grid item xs={6} key={sid}>
                      <Box onClick={() => setCurrentSubject(sid)} sx={{ p: 2.5, bgcolor: '#F8FAFC', borderRadius: 2, border: '1px solid #E2E8F0', cursor: 'pointer', transition: 'all 0.2s', '&:hover': { borderColor: '#6366F1', bgcolor: '#FAFAFE', transform: 'translateY(-2px)', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' } }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5, color: '#1E293B' }}>{name}</Typography>
                        <Box sx={{ display: 'flex', gap: 3 }}>
                          <Box>
                            <Typography variant="h4" sx={{ color: '#3B82F6', fontWeight: 700 }}>{data.total_questions}</Typography>
                            <Typography variant="caption" sx={{ color: '#64748B' }}>Questions</Typography>
                          </Box>
                          <Box>
                            <Typography variant="h4" sx={{ color: '#10B981', fontWeight: 700 }}>{data.layer3_success}</Typography>
                            <Typography variant="caption" sx={{ color: '#64748B' }}>Answered</Typography>
                          </Box>
                          <Box>
                            <Typography variant="h4" sx={{ color: '#8B5CF6', fontWeight: 700 }}>{data.avg_confidence ? (data.avg_confidence * 100).toFixed(0) + '%' : '—'}</Typography>
                            <Typography variant="caption" sx={{ color: '#64748B' }}>Confidence</Typography>
                          </Box>
                        </Box>
                      </Box>
                    </Grid>
                  );
                })}
              </Grid>
            </Paper>
          )}

          {metrics.last_updated && (
            <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', color: '#94A3B8', mt: 1 }}>
              Last updated: {new Date(metrics.last_updated).toLocaleString()}
            </Typography>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default MetricsPage;
