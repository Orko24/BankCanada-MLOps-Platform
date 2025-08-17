/**
 * Data Quality Dashboard - Placeholder Component
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
  Alert
} from '@mui/material';
import { DataUsage as DataUsageIcon } from '@mui/icons-material';

const DataQuality = () => {
  const qualityMetrics = [
    { indicator: 'Inflation Data', completeness: 98.5, timeliness: 95.0, accuracy: 99.2 },
    { indicator: 'GDP Data', completeness: 96.8, timeliness: 88.5, accuracy: 97.8 },
    { indicator: 'Employment Data', completeness: 99.1, timeliness: 92.3, accuracy: 98.5 }
  ];

  const getQualityColor = (score) => {
    if (score >= 95) return 'success';
    if (score >= 85) return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={4}>
        <DataUsageIcon sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Data Quality Monitor
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Economic data validation and quality assessment
          </Typography>
        </Box>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        Real data quality metrics will be calculated from Bank of Canada API ingestion.
      </Alert>

      <Grid container spacing={3}>
        {qualityMetrics.map((metric, index) => (
          <Grid item xs={12} key={index}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {metric.indicator}
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Box display="flex" justifyContent="between" alignItems="center">
                      <Typography variant="body2">Completeness</Typography>
                      <Chip 
                        label={`${metric.completeness}%`}
                        color={getQualityColor(metric.completeness)}
                        size="small"
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Box display="flex" justifyContent="between" alignItems="center">
                      <Typography variant="body2">Timeliness</Typography>
                      <Chip 
                        label={`${metric.timeliness}%`}
                        color={getQualityColor(metric.timeliness)}
                        size="small"
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Box display="flex" justifyContent="between" alignItems="center">
                      <Typography variant="body2">Accuracy</Typography>
                      <Chip 
                        label={`${metric.accuracy}%`}
                        color={getQualityColor(metric.accuracy)}
                        size="small"
                      />
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default DataQuality;
