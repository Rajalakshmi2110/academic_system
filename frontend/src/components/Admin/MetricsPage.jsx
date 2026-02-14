import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Grid, Card, CardContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Divider, Chip, Button } from '@mui/material';
import { CheckCircle, Speed, Assessment, TrendingUp, Logout } from '@mui/icons-material';
import axios from 'axios';

const MetricsPage = ({ onSwitchTab, onLogout }) => {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/metrics');
      setMetrics(res.data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  if (!metrics) return <Box sx={{ p: 4 }}><Typography>Loading metrics...</Typography></Box>;

  return (
    <Box sx={{ p: 4, bgcolor: '#F5F7FA', minHeight: '100vh' }}>
      <Box sx={{ bgcolor: '#1976D2', color: 'white', p: 2, mb: 3, borderRadius: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">Evaluation Metrics</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" onClick={() => onSwitchTab(0)} sx={{ color: 'white', borderColor: 'white', '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' } }}>DASHBOARD</Button>
          <Button variant="outlined" onClick={() => onSwitchTab(1)} sx={{ color: 'white', borderColor: 'white', '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' } }}>METRICS</Button>
          <Button startIcon={<Logout />} onClick={onLogout} sx={{ color: 'white' }}>Logout</Button>
        </Box>
      </Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, color: '#1A202C', mb: 1 }}>System Performance Metrics</Typography>
        <Typography variant="body2" color="text.secondary">Real-time evaluation metrics for the 3-layer validation pipeline</Typography>
      </Box>

      {/* Layer 1 Metrics */}
      <Paper elevation={0} sx={{ p: 4, mb: 3, borderRadius: 3, border: '1px solid #E2E8F0' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ bgcolor: '#10B981', p: 1.5, borderRadius: 2 }}>
              <CheckCircle sx={{ color: 'white', fontSize: 28 }} />
            </Box>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#1A202C' }}>Layer 1: DS Classifier</Typography>
              <Typography variant="caption" color="text.secondary">DistilBERT Fine-tuned Model</Typography>
            </Box>
          </Box>
          <Chip label="Active" color="success" size="small" />
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#ECFDF5', border: '1px solid #D1FAE5', borderRadius: 2 }}>
              <CardContent>
                <Typography variant="caption" sx={{ color: '#065F46', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>Accuracy</Typography>
                <Typography variant="h3" sx={{ color: '#10B981', fontWeight: 700, mt: 1 }}>
                  {(metrics.layer1.accuracy * 100).toFixed(1)}%
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
                  <TrendingUp sx={{ fontSize: 16, color: '#10B981' }} />
                  <Typography variant="caption" sx={{ color: '#065F46' }}>Excellent</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#EFF6FF', border: '1px solid #DBEAFE', borderRadius: 2 }}>
              <CardContent>
                <Typography variant="caption" sx={{ color: '#1E40AF', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>Precision</Typography>
                <Typography variant="h3" sx={{ color: '#3B82F6', fontWeight: 700, mt: 1 }}>
                  {(metrics.layer1.precision * 100).toFixed(1)}%
                </Typography>
                <Typography variant="caption" sx={{ color: '#1E40AF', mt: 1, display: 'block' }}>True Positive Rate</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#FEF3C7', border: '1px solid #FDE68A', borderRadius: 2 }}>
              <CardContent>
                <Typography variant="caption" sx={{ color: '#92400E', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>Recall</Typography>
                <Typography variant="h3" sx={{ color: '#F59E0B', fontWeight: 700, mt: 1 }}>
                  {(metrics.layer1.recall * 100).toFixed(1)}%
                </Typography>
                <Typography variant="caption" sx={{ color: '#92400E', mt: 1, display: 'block' }}>Coverage Rate</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={3}>
            <Card elevation={0} sx={{ bgcolor: '#F5F3FF', border: '1px solid #E9D5FF', borderRadius: 2 }}>
              <CardContent>
                <Typography variant="caption" sx={{ color: '#5B21B6', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>Latency</Typography>
                <Typography variant="h3" sx={{ color: '#8B5CF6', fontWeight: 700, mt: 1 }}>
                  {metrics.layer1.avg_latency_ms.toFixed(0)}ms
                </Typography>
                <Typography variant="caption" sx={{ color: '#5B21B6', mt: 1, display: 'block' }}>Avg Response Time</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />
        
        <Box sx={{ display: 'flex', gap: 4 }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: '#1A202C' }}>Confusion Matrix</Typography>
            <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #E2E8F0', borderRadius: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ bgcolor: '#F8FAFC' }}>
                    <TableCell sx={{ fontWeight: 600 }}></TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600 }}>Predicted: Out</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600 }}>Predicted: In</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Actual: Out</TableCell>
                    <TableCell align="center" sx={{ bgcolor: '#ECFDF5', fontWeight: 600, color: '#10B981' }}>{metrics.layer1.confusion_matrix[0][0]}</TableCell>
                    <TableCell align="center" sx={{ bgcolor: '#FEE2E2', fontWeight: 600, color: '#EF4444' }}>{metrics.layer1.confusion_matrix[0][1]}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Actual: In</TableCell>
                    <TableCell align="center" sx={{ bgcolor: '#FEE2E2', fontWeight: 600, color: '#EF4444' }}>{metrics.layer1.confusion_matrix[1][0]}</TableCell>
                    <TableCell align="center" sx={{ bgcolor: '#ECFDF5', fontWeight: 600, color: '#10B981' }}>{metrics.layer1.confusion_matrix[1][1]}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: '#1A202C' }}>Performance Summary</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ p: 2, bgcolor: '#F8FAFC', borderRadius: 2, border: '1px solid #E2E8F0' }}>
                <Typography variant="caption" color="text.secondary">F1 Score</Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, color: '#1A202C' }}>{(metrics.layer1.f1_score * 100).toFixed(2)}%</Typography>
              </Box>
              <Box sx={{ p: 2, bgcolor: '#F8FAFC', borderRadius: 2, border: '1px solid #E2E8F0' }}>
                <Typography variant="caption" color="text.secondary">Total Samples Evaluated</Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, color: '#1A202C' }}>{metrics.layer1.total_samples}</Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </Paper>

      {/* Layer 2 Metrics */}
      <Paper elevation={0} sx={{ p: 4, mb: 3, borderRadius: 3, border: '1px solid #E2E8F0' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ bgcolor: '#3B82F6', p: 1.5, borderRadius: 2 }}>
              <Assessment sx={{ color: 'white', fontSize: 28 }} />
            </Box>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#1A202C' }}>Layer 2: Syllabus Checker</Typography>
              <Typography variant="caption" color="text.secondary">Groq Llama 3.3 70B with MCP</Typography>
            </Box>
          </Box>
          <Chip label="Active" color="primary" size="small" />
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={2.4}>
            <Card elevation={0} sx={{ bgcolor: '#ECFDF5', border: '1px solid #D1FAE5', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#10B981', fontWeight: 700 }}>{metrics.layer2.valid}</Typography>
                <Typography variant="caption" sx={{ color: '#065F46', fontWeight: 600, textTransform: 'uppercase' }}>Valid</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={2.4}>
            <Card elevation={0} sx={{ bgcolor: '#FEF3C7', border: '1px solid #FDE68A', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#F59E0B', fontWeight: 700 }}>{metrics.layer2.warnings}</Typography>
                <Typography variant="caption" sx={{ color: '#92400E', fontWeight: 600, textTransform: 'uppercase' }}>Warnings</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={2.4}>
            <Card elevation={0} sx={{ bgcolor: '#F1F5F9', border: '1px solid #E2E8F0', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#64748B', fontWeight: 700 }}>{metrics.layer2.out_of_syllabus}</Typography>
                <Typography variant="caption" sx={{ color: '#475569', fontWeight: 600, textTransform: 'uppercase' }}>Out of Syllabus</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={2.4}>
            <Card elevation={0} sx={{ bgcolor: '#FEE2E2', border: '1px solid #FECACA', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#EF4444', fontWeight: 700 }}>{metrics.layer2.rejected}</Typography>
                <Typography variant="caption" sx={{ color: '#991B1B', fontWeight: 600, textTransform: 'uppercase' }}>Rejected</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={2.4}>
            <Card elevation={0} sx={{ bgcolor: '#EFF6FF', border: '1px solid #DBEAFE', borderRadius: 2, textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h2" sx={{ color: '#3B82F6', fontWeight: 700 }}>{metrics.layer2.avg_latency_ms.toFixed(0)}</Typography>
                <Typography variant="caption" sx={{ color: '#1E40AF', fontWeight: 600, textTransform: 'uppercase' }}>Avg Latency (ms)</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        <Typography variant="caption" sx={{ mt: 3, display: 'block', color: 'text.secondary' }}>
          Total Samples Evaluated: {metrics.layer2.total_samples}
        </Typography>
      </Paper>

      {/* End-to-End Metrics */}
      <Paper elevation={0} sx={{ p: 4, borderRadius: 3, border: '1px solid #E2E8F0' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Box sx={{ bgcolor: '#F59E0B', p: 1.5, borderRadius: 2 }}>
            <Speed sx={{ color: 'white', fontSize: 28 }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1A202C' }}>End-to-End Performance</Typography>
            <Typography variant="caption" color="text.secondary">Full Pipeline (Layer 1 + Layer 2 + Layer 3 RAG)</Typography>
          </Box>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={4}>
            <Card elevation={0} sx={{ bgcolor: '#EFF6FF', border: '1px solid #DBEAFE', borderRadius: 2 }}>
              <CardContent>
                <Typography variant="caption" sx={{ color: '#1E40AF', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>Average Response</Typography>
                <Typography variant="h3" sx={{ color: '#3B82F6', fontWeight: 700, mt: 1 }}>
                  {(metrics.end_to_end.avg_latency_ms / 1000).toFixed(2)}s
                </Typography>
                <Typography variant="caption" sx={{ color: '#1E40AF', mt: 1, display: 'block' }}>Mean processing time</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={4}>
            <Card elevation={0} sx={{ bgcolor: '#ECFDF5', border: '1px solid #D1FAE5', borderRadius: 2 }}>
              <CardContent>
                <Typography variant="caption" sx={{ color: '#065F46', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>Fastest Response</Typography>
                <Typography variant="h3" sx={{ color: '#10B981', fontWeight: 700, mt: 1 }}>
                  {(metrics.end_to_end.min_latency_ms / 1000).toFixed(2)}s
                </Typography>
                <Typography variant="caption" sx={{ color: '#065F46', mt: 1, display: 'block' }}>Best case scenario</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={4}>
            <Card elevation={0} sx={{ bgcolor: '#FEE2E2', border: '1px solid #FECACA', borderRadius: 2 }}>
              <CardContent>
                <Typography variant="caption" sx={{ color: '#991B1B', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>Slowest Response</Typography>
                <Typography variant="h3" sx={{ color: '#EF4444', fontWeight: 700, mt: 1 }}>
                  {(metrics.end_to_end.max_latency_ms / 1000).toFixed(2)}s
                </Typography>
                <Typography variant="caption" sx={{ color: '#991B1B', mt: 1, display: 'block' }}>Worst case scenario</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        <Typography variant="caption" sx={{ mt: 3, display: 'block', color: 'text.secondary' }}>
          Total Samples Evaluated: {metrics.end_to_end.total_samples}
        </Typography>
      </Paper>
    </Box>
  );
};

export default MetricsPage;
