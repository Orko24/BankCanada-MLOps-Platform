/**
 * Model Monitoring Dashboard - Placeholder Component
 */

import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Alert,
  Grid,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import { Assessment as AssessmentIcon } from '@mui/icons-material';

const ModelMonitoring = () => {
  const mockModels = [
    { name: 'Inflation Forecast Model', status: 'Active', accuracy: '94.2%' },
    { name: 'GDP Growth Model', status: 'Training', accuracy: '91.8%' },
    { name: 'Exchange Rate Model', status: 'Active', accuracy: '89.5%' }
  ];

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={4}>
        <AssessmentIcon sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Model Monitoring
          </Typography>
          <Typography variant="body1" color="text.secondary">
            MLflow model registry and performance tracking
          </Typography>
        </Box>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        This dashboard will show real MLflow data when connected to your Databricks workspace.
      </Alert>

      <Grid container spacing={3}>
        {mockModels.map((model, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {model.name}
                </Typography>
                <Box display="flex" justifyContent="between" alignItems="center">
                  <Chip 
                    label={model.status}
                    color={model.status === 'Active' ? 'success' : 'warning'}
                    size="small"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Accuracy: {model.accuracy}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ModelMonitoring;
