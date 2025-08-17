/**
 * Settings Dashboard - Placeholder Component
 */

import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Button,
  Alert
} from '@mui/material';
import { Settings as SettingsIcon } from '@mui/icons-material';

const Settings = () => {
  return (
    <Box>
      <Box display="flex" alignItems="center" mb={4}>
        <SettingsIcon sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Platform Settings
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Configure your MLOps platform preferences
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Data Settings
              </Typography>
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Enable real-time data updates"
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Auto-refresh economic indicators"
              />
              <FormControlLabel
                control={<Switch />}
                label="Enable data quality alerts"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                ML Model Settings
              </Typography>
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Enable model monitoring"
              />
              <FormControlLabel
                control={<Switch />}
                label="Auto-retrain on drift detection"
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Performance notifications"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              API Configuration
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              API keys and credentials are managed securely. Use the AI Research Assistant settings to configure your DeepSeek API key.
            </Alert>
            <Button variant="outlined" sx={{ mr: 2 }}>
              Test Bank of Canada API
            </Button>
            <Button variant="outlined">
              Validate MLflow Connection
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Settings;
