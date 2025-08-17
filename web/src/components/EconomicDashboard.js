/**
 * Economic Dashboard - Bank of Canada
 * 
 * Main dashboard displaying real-time economic indicators,
 * trends, and key metrics for central banking operations.
 */

import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Avatar,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Stack
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Refresh,
  Download,
  Info,
  Assessment,
  Timeline,
  AccountBalance,
  Work,
  Home,
  AttachMoney,
  Speed,
  Settings
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { format, parseISO, subDays, subMonths, subYears } from 'date-fns';
import numeral from 'numeral';

import { apiService } from '../services/apiService';
import { useNotifications } from '../hooks/useNotifications';
import DatabricksConfigModal from './DatabricksConfigModal';

// Key economic indicators configuration
const ECONOMIC_INDICATORS = [
  {
    id: 'inflation',
    name: 'Inflation Rate',
    icon: TrendingUp,
    color: '#E53E3E',
    unit: '%',
    description: 'Consumer Price Index year-over-year change'
  },
  {
    id: 'unemployment',
    name: 'Unemployment Rate',
    icon: Work,
    color: '#3182CE',
    unit: '%',
    description: 'Unemployment rate (seasonally adjusted)'
  },
  {
    id: 'gdp',
    name: 'GDP Growth',
    icon: Assessment,
    color: '#38A169',
    unit: '%',
    description: 'Real GDP growth rate (annualized)'
  },
  {
    id: 'interest_rates',
    name: 'Policy Rate',
    icon: AccountBalance,
    color: '#D69E2E',
    unit: '%',
    description: 'Bank of Canada overnight rate'
  },
  {
    id: 'exchange_rates',
    name: 'CAD/USD',
    icon: AttachMoney,
    color: '#9F7AEA',
    unit: '',
    description: 'Canadian Dollar vs US Dollar exchange rate'
  },
  {
    id: 'housing',
    name: 'Housing Price Index',
    icon: Home,
    color: '#F56500',
    unit: 'Index',
    description: 'New Housing Price Index'
  }
];

// Chart colors
const CHART_COLORS = ['#C41E3A', '#2B6CB0', '#38A169', '#D69E2E', '#9F7AEA', '#F56500'];

const EconomicDashboard = () => {
  // State management
  const [indicatorData, setIndicatorData] = useState({});
  const [selectedTimeRange, setSelectedTimeRange] = useState('1Y');
  const [selectedTab, setSelectedTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [databricksConfigOpen, setDatabricksConfigOpen] = useState(false);

  const { showNotification } = useNotifications();

  // Load economic data
  useEffect(() => {
    loadEconomicData();
  }, [selectedTimeRange]);

  const loadEconomicData = async (showRefreshIndicator = false) => {
    try {
      if (showRefreshIndicator) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      // Calculate date range
      const endDate = new Date();
      let startDate;
      
      switch (selectedTimeRange) {
        case '3M':
          startDate = subMonths(endDate, 3);
          break;
        case '6M':
          startDate = subMonths(endDate, 6);
          break;
        case '1Y':
          startDate = subYears(endDate, 1);
          break;
        case '2Y':
          startDate = subYears(endDate, 2);
          break;
        case '5Y':
          startDate = subYears(endDate, 5);
          break;
        default:
          startDate = subYears(endDate, 1);
      }

      // Load data for each indicator
      const indicatorPromises = ECONOMIC_INDICATORS.map(async (indicator) => {
        try {
          const data = await apiService.getIndicatorData(
            indicator.id,
            startDate.toISOString().split('T')[0],
            endDate.toISOString().split('T')[0]
          );
          return { id: indicator.id, data };
        } catch (error) {
          console.error(`Failed to load ${indicator.id} data:`, error);
          return { id: indicator.id, data: null, error: error.message };
        }
      });

      const results = await Promise.all(indicatorPromises);
      
      // Process results
      const processedData = {};
      results.forEach(({ id, data, error }) => {
        if (data) {
          processedData[id] = {
            timeSeries: data.data_points || [],
            statistics: data.statistics || {},
            metadata: data.metadata || {},
            error: null
          };
        } else {
          processedData[id] = {
            timeSeries: [],
            statistics: {},
            metadata: {},
            error: error || 'Failed to load data'
          };
        }
      });

      setIndicatorData(processedData);
      setLastUpdate(new Date());
      
      if (showRefreshIndicator) {
        showNotification('Economic data refreshed successfully', 'success');
      }

    } catch (error) {
      console.error('Failed to load economic data:', error);
      showNotification('Failed to load economic data', 'error');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Get trend direction for an indicator
  const getTrendDirection = (data) => {
    if (!data.timeSeries || data.timeSeries.length < 2) return 'flat';
    
    const recent = data.timeSeries.slice(-2);
    const current = recent[1]?.value;
    const previous = recent[0]?.value;
    
    if (current > previous) return 'up';
    if (current < previous) return 'down';
    return 'flat';
  };

  // Format value for display
  const formatValue = (value, unit) => {
    if (value === null || value === undefined) return 'N/A';
    
    if (unit === '%') {
      return `${numeral(value).format('0.0')}%`;
    } else if (unit === 'Index') {
      return numeral(value).format('0.0');
    } else {
      return numeral(value).format('0.00');
    }
  };

  // Get trend icon
  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'up':
        return <TrendingUp sx={{ color: '#38A169' }} />;
      case 'down':
        return <TrendingDown sx={{ color: '#E53E3E' }} />;
      default:
        return <TrendingFlat sx={{ color: '#A0AEC0' }} />;
    }
  };

  // Render indicator card
  const renderIndicatorCard = (indicator) => {
    const data = indicatorData[indicator.id];
    if (!data) return null;

    const trend = getTrendDirection(data);
    const latestValue = data.timeSeries.length > 0 ? 
      data.timeSeries[data.timeSeries.length - 1]?.value : null;
    const change = data.statistics.month_over_month_change;

    return (
      <Card key={indicator.id} elevation={2}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Box display="flex" alignItems="center">
              <Avatar sx={{ bgcolor: indicator.color, mr: 2 }}>
                <indicator.icon />
              </Avatar>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  {indicator.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {indicator.description}
                </Typography>
              </Box>
            </Box>
            <Tooltip title={`Trend: ${trend}`}>
              {getTrendIcon(trend)}
            </Tooltip>
          </Box>

          <Box display="flex" alignItems="baseline" gap={1} mb={1}>
            <Typography variant="h3" fontWeight={700} color={indicator.color}>
              {formatValue(latestValue, indicator.unit)}
            </Typography>
            {change && (
              <Chip
                label={`${change > 0 ? '+' : ''}${formatValue(change, '%')} MoM`}
                size="small"
                color={change > 0 ? 'success' : change < 0 ? 'error' : 'default'}
                variant="outlined"
              />
            )}
          </Box>

          {data.error ? (
            <Alert severity="warning" size="small">
              {data.error}
            </Alert>
          ) : (
            <Typography variant="body2" color="text.secondary">
              Last updated: {data.metadata.last_updated || 'Unknown'}
            </Typography>
          )}
        </CardContent>
      </Card>
    );
  };

  // Render time series chart
  const renderTimeSeriesChart = () => {
    const chartData = [];
    
    // Combine all indicator data by date
    const dateMap = new Map();
    
    ECONOMIC_INDICATORS.forEach((indicator) => {
      const data = indicatorData[indicator.id];
      if (data && data.timeSeries) {
        data.timeSeries.forEach((point) => {
          const date = point.date;
          if (!dateMap.has(date)) {
            dateMap.set(date, { date });
          }
          dateMap.get(date)[indicator.id] = point.value;
        });
      }
    });

    // Convert to array and sort by date
    const sortedData = Array.from(dateMap.values()).sort((a, b) => 
      new Date(a.date) - new Date(b.date)
    );

    return (
      <Paper sx={{ p: 3, height: 400 }}>
        <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
          <Typography variant="h6" fontWeight={600}>
            Economic Indicators Trends
          </Typography>
          <Box display="flex" gap={1}>
            {['3M', '6M', '1Y', '2Y', '5Y'].map((range) => (
              <Button
                key={range}
                size="small"
                variant={selectedTimeRange === range ? 'contained' : 'outlined'}
                onClick={() => setSelectedTimeRange(range)}
              >
                {range}
              </Button>
            ))}
          </Box>
        </Box>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={sortedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(date) => format(parseISO(date), 'MMM yy')}
            />
            <YAxis />
            <RechartsTooltip 
              labelFormatter={(date) => format(parseISO(date), 'MMM dd, yyyy')}
              formatter={(value, name) => [
                formatValue(value, ECONOMIC_INDICATORS.find(i => i.id === name)?.unit || ''),
                ECONOMIC_INDICATORS.find(i => i.id === name)?.name || name
              ]}
            />
            <Legend />
            {ECONOMIC_INDICATORS.map((indicator, index) => (
              <Line
                key={indicator.id}
                type="monotone"
                dataKey={indicator.id}
                stroke={CHART_COLORS[index % CHART_COLORS.length]}
                strokeWidth={2}
                dot={false}
                name={indicator.name}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </Paper>
    );
  };

  // Render correlation matrix
  const renderCorrelationMatrix = () => {
    // Calculate correlations between indicators
    const correlationData = [];
    
    for (let i = 0; i < ECONOMIC_INDICATORS.length; i++) {
      for (let j = i + 1; j < ECONOMIC_INDICATORS.length; j++) {
        const indicator1 = ECONOMIC_INDICATORS[i];
        const indicator2 = ECONOMIC_INDICATORS[j];
        
        // Mock correlation calculation (in real app, this would be calculated server-side)
        const correlation = Math.random() * 2 - 1; // Random between -1 and 1
        
        correlationData.push({
          indicator1: indicator1.name,
          indicator2: indicator2.name,
          correlation: correlation,
          strength: Math.abs(correlation)
        });
      }
    }

    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" fontWeight={600} mb={3}>
          Indicator Correlations
        </Typography>
        
        <Grid container spacing={2}>
          {correlationData.map((item, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Box 
                sx={{
                  p: 2,
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  backgroundColor: item.correlation > 0 ? 'success.light' : 'error.light',
                  opacity: 0.1 + item.strength * 0.9
                }}
              >
                <Typography variant="body2" fontWeight={600}>
                  {item.indicator1} vs {item.indicator2}
                </Typography>
                <Typography variant="h6" color={item.correlation > 0 ? 'success.main' : 'error.main'}>
                  {numeral(item.correlation).format('0.00')}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading economic indicators...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Economic Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time economic indicators and market intelligence
          </Typography>
        </Box>
        
        <Stack direction="row" spacing={2}>
          <Tooltip title="Configure Databricks">
            <IconButton 
              onClick={() => setDatabricksConfigOpen(true)}
              color="primary"
            >
              <Settings />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Refresh Data">
            <IconButton 
              onClick={() => loadEconomicData(true)}
              disabled={refreshing}
              color="primary"
            >
              {refreshing ? <CircularProgress size={20} /> : <Refresh />}
            </IconButton>
          </Tooltip>
          
          <Button variant="outlined" startIcon={<Download />}>
            Export Data
          </Button>
          
          
          {lastUpdate && (
            <Chip
              label={`Updated: ${format(lastUpdate, 'HH:mm')}`}
              variant="outlined"
              size="small"
            />
          )}
        </Stack>
      </Box>

      {/* Key Indicators Grid */}
      <Grid container spacing={3} mb={4}>
        {ECONOMIC_INDICATORS.map((indicator) => (
          <Grid item xs={12} sm={6} md={4} lg={2} key={indicator.id}>
            {renderIndicatorCard(indicator)}
          </Grid>
        ))}
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          {renderTimeSeriesChart()}
        </Grid>
        
        <Grid item xs={12} lg={4}>
          {renderCorrelationMatrix()}
        </Grid>
      </Grid>
      
      {/* Databricks Configuration Modal */}
      <DatabricksConfigModal
        open={databricksConfigOpen}
        onClose={() => setDatabricksConfigOpen(false)}
        onConfigured={() => {
          setDatabricksConfigOpen(false);
          showNotification('Databricks configured successfully!', 'success');
          // Optionally refresh data
          loadEconomicData(true);
        }}
      />
    </Box>
  );
};

export default EconomicDashboard;
