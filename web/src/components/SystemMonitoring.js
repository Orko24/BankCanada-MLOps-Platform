/**
 * System Monitoring Dashboard - Placeholder Component
 */

import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  Chip,
  LinearProgress
} from '@mui/material';
import { Speed as SpeedIcon } from '@mui/icons-material';

const SystemMonitoring = ({ systemStatus }) => {
  return (
    <Box>
      <Box display="flex" alignItems="center" mb={4}>
        <SpeedIcon sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            System Health
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Infrastructure monitoring and performance metrics
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Status
              </Typography>
              <Chip label="Operational" color="success" />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Response time: 120ms
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Database
              </Typography>
              <Chip label="Healthy" color="success" />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Connections: 15/100
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                MLflow
              </Typography>
              <Chip label="Running" color="success" />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Experiments: 5 active
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cache
              </Typography>
              <Chip label="Redis Online" color="success" />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Memory: 45% used
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Resources
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" gutterBottom>
                  CPU Usage: 35%
                </Typography>
                <LinearProgress variant="determinate" value={35} />
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" gutterBottom>
                  Memory Usage: 60%
                </Typography>
                <LinearProgress variant="determinate" value={60} />
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" gutterBottom>
                  Disk Usage: 40%
                </Typography>
                <LinearProgress variant="determinate" value={40} />
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SystemMonitoring;
