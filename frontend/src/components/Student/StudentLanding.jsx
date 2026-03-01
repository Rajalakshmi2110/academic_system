import React from 'react';
import { Box, Button, Typography, Container, Paper, Grid } from '@mui/material';
import { School, Chat, Speed, Security, CheckCircle } from '@mui/icons-material';

const StudentLanding = ({ onGetStarted }) => {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F5F5F5', py: 8 }}>
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <School sx={{ fontSize: 80, color: '#1976D2', mb: 2 }} />
          <Typography variant="h3" sx={{ fontWeight: 'bold', mb: 2, color: '#333' }}>
            Academic Doubt Clarification System
          </Typography>
          <Typography variant="h6" sx={{ color: '#666', mb: 4, maxWidth: 700, mx: 'auto' }}>
            Get instant, accurate answers to your academic questions with our 3-layer intelligent validation system
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={onGetStarted}
            sx={{ 
              px: 6, 
              py: 2, 
              fontSize: 18,
              borderRadius: 3,
              bgcolor: '#1976D2',
              '&:hover': { bgcolor: '#1565C0' }
            }}
          >
            Get Started
          </Button>
        </Box>

        <Grid container spacing={3} sx={{ mt: 4 }}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%', textAlign: 'center' }}>
              <Security sx={{ fontSize: 50, color: '#1976D2', mb: 2 }} />
              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                3-Layer Validation
              </Typography>
              <Typography variant="body2" sx={{ color: '#666' }}>
                Questions are validated through subject classifier, syllabus checker, and RAG pipeline
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%', textAlign: 'center' }}>
              <School sx={{ fontSize: 50, color: '#4CAF50', mb: 2 }} />
              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                Syllabus-Aligned
              </Typography>
              <Typography variant="body2" sx={{ color: '#666' }}>
                Answers are grounded in your course materials and syllabus content
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%', textAlign: 'center' }}>
              <Speed sx={{ fontSize: 50, color: '#FF9800', mb: 2 }} />
              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                Confidence Scoring
              </Typography>
              <Typography variant="body2" sx={{ color: '#666' }}>
                Every answer includes a confidence score based on context relevance
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        <Box sx={{ mt: 6, textAlign: 'center' }}>
          <Typography variant="body2" sx={{ color: '#999', fontStyle: 'italic' }}>
            Built with advanced AI models and retrieval-augmented generation
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default StudentLanding;
