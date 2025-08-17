/**
 * Bank of Canada Economic Indicators MLOps Dashboard
 * 
 * Main application component featuring:
 * - Real-time economic indicator monitoring
 * - ML model performance tracking
 * - Interactive forecasting visualizations
 * - Professional central banking interface
 */

import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Box,
  Tab,
  Tabs,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Badge
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  Psychology as PsychologyIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  Security as SecurityIcon,
  DataUsage as DataUsageIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { SnackbarProvider } from 'notistack';

// Import dashboard components
import EconomicDashboard from './components/EconomicDashboard';
import ForecastingDashboard from './components/ForecastingDashboard';
import ModelMonitoring from './components/ModelMonitoring';
import SystemMonitoring from './components/SystemMonitoring';
import DataQuality from './components/DataQuality';
import AIAgentDashboard from './components/AIAgentDashboard';
import Settings from './components/Settings';

// Import services
import { apiService } from './services/apiService';
import { useNotifications } from './hooks/useNotifications';

// Bank of Canada theme
const bankCanadaTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#C41E3A', // Bank of Canada red
      light: '#E53E3E',
      dark: '#9B1C32',
      contrastText: '#FFFFFF'
    },
    secondary: {
      main: '#2B6CB0', // Professional blue
      light: '#4299E1',
      dark: '#2A69AC'
    },
    background: {
      default: '#F7FAFC',
      paper: '#FFFFFF'
    },
    success: {
      main: '#38A169',
      light: '#68D391',
      dark: '#2F855A'
    },
    warning: {
      main: '#D69E2E',
      light: '#F6E05E',
      dark: '#B7791F'
    },
    error: {
      main: '#E53E3E',
      light: '#FC8181',
      dark: '#C53030'
    },
    info: {
      main: '#3182CE',
      light: '#63B3ED',
      dark: '#2C5282'
    }
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      lineHeight: 1.2
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.4
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.5
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
      lineHeight: 1.5
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.6
    }
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#C41E3A',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          borderRadius: 8
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          borderRadius: 12,
          '&:hover': {
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          }
        }
      }
    }
  }
});

// Navigation items
const navigationItems = [
  { id: 'dashboard', label: 'Economic Dashboard', icon: DashboardIcon },
  { id: 'forecasting', label: 'ML Forecasting', icon: TrendingUpIcon },
  { id: 'ai-agent', label: 'AI Research Assistant', icon: PsychologyIcon },
  { id: 'models', label: 'Model Monitoring', icon: AssessmentIcon },
  { id: 'system', label: 'System Health', icon: SpeedIcon },
  { id: 'data-quality', label: 'Data Quality', icon: DataUsageIcon },
  { id: 'settings', label: 'Settings', icon: SettingsIcon }
];

function App() {
  // State management
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notifications, setNotifications] = useState([]);

  // Custom hooks
  const { showNotification } = useNotifications();

  // Load initial data
  useEffect(() => {
    const initializeApp = async () => {
      try {
        setLoading(true);
        
        // Load system status
        const status = await apiService.getSystemInfo();
        setSystemStatus(status);
        
        // Load recent notifications
        const recentNotifications = await apiService.getRecentAlerts();
        setNotifications(recentNotifications);
        
        setError(null);
      } catch (err) {
        console.error('Failed to initialize app:', err);
        setError('Failed to load system data. Please check your connection.');
        showNotification('Failed to connect to system', 'error');
      } finally {
        setLoading(false);
      }
    };

    initializeApp();
    
    // Set up periodic status updates
    const statusInterval = setInterval(async () => {
      try {
        const status = await apiService.getSystemInfo();
        setSystemStatus(status);
      } catch (err) {
        console.error('Failed to update system status:', err);
      }
    }, 30000); // Update every 30 seconds

    return () => clearInterval(statusInterval);
  }, [showNotification]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
    setDrawerOpen(false);
  };

  // Render current tab content
  const renderTabContent = () => {
    switch (currentTab) {
      case 'dashboard':
        return <EconomicDashboard />;
      case 'forecasting':
        return <ForecastingDashboard />;
      case 'ai-agent':
        return <AIAgentDashboard />;
      case 'models':
        return <ModelMonitoring />;
      case 'system':
        return <SystemMonitoring systemStatus={systemStatus} />;
      case 'data-quality':
        return <DataQuality />;
      case 'settings':
        return <Settings />;
      default:
        return <EconomicDashboard />;
    }
  };

  // Get system health indicator
  const getSystemHealthColor = () => {
    if (!systemStatus) return 'default';
    const health = systemStatus.system_resources?.cpu_usage || 0;
    if (health < 70) return 'success';
    if (health < 85) return 'warning';
    return 'error';
  };

  // Loading screen
  if (loading) {
    return (
      <ThemeProvider theme={bankCanadaTheme}>
        <CssBaseline />
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="100vh"
          flexDirection="column"
        >
          <CircularProgress size={60} sx={{ mb: 2 }} />
          <Typography variant="h6" color="textSecondary">
            Loading Bank of Canada MLOps Platform...
          </Typography>
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={bankCanadaTheme}>
      <CssBaseline />
      <SnackbarProvider 
        maxSnack={3}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          {/* Header */}
          <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                onClick={() => setDrawerOpen(true)}
                edge="start"
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
              
              <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
                Bank of Canada - Economic ML Operations Platform
              </Typography>

              {/* System Status Indicator */}
              {systemStatus && (
                <Chip
                  icon={<SpeedIcon />}
                  label={`System: ${systemStatus.uptime || 'Online'}`}
                  color={getSystemHealthColor()}
                  size="small"
                  sx={{ mr: 2 }}
                />
              )}

              {/* Notifications */}
              <IconButton color="inherit" sx={{ mr: 1 }}>
                <Badge badgeContent={notifications.length} color="secondary">
                  <NotificationsIcon />
                </Badge>
              </IconButton>

              {/* User Account */}
              <IconButton color="inherit">
                <AccountCircleIcon />
              </IconButton>
            </Toolbar>
          </AppBar>

          {/* Navigation Drawer */}
          <Drawer
            variant="temporary"
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
            ModalProps={{
              keepMounted: true, // Better open performance on mobile
            }}
            sx={{
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: 280,
                mt: 8
              },
            }}
          >
            <Box sx={{ p: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                Navigation
              </Typography>
            </Box>
            <Divider />
            
            <List>
              {navigationItems.map((item) => (
                <ListItem key={item.id} disablePadding>
                  <ListItemButton
                    selected={currentTab === item.id}
                    onClick={() => handleTabChange(null, item.id)}
                    sx={{
                      '&.Mui-selected': {
                        backgroundColor: 'primary.light',
                        '&:hover': {
                          backgroundColor: 'primary.light',
                        },
                      },
                    }}
                  >
                    <ListItemIcon>
                      <item.icon color={currentTab === item.id ? 'primary' : 'inherit'} />
                    </ListItemIcon>
                    <ListItemText 
                      primary={item.label}
                      primaryTypographyProps={{
                        fontWeight: currentTab === item.id ? 600 : 400
                      }}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Drawer>

          {/* Main Content */}
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              pt: 10,
              pb: 3,
              px: 3,
              backgroundColor: 'background.default'
            }}
          >
            {/* Error Display */}
            {error && (
              <Alert 
                severity="error" 
                sx={{ mb: 3 }}
                onClose={() => setError(null)}
              >
                {error}
              </Alert>
            )}

            {/* Tab Content */}
            <Container maxWidth="xl" sx={{ mt: 2 }}>
              {renderTabContent()}
            </Container>
          </Box>

          {/* Footer */}
          <Box
            component="footer"
            sx={{
              py: 2,
              px: 3,
              backgroundColor: 'background.paper',
              borderTop: '1px solid',
              borderColor: 'divider'
            }}
          >
            <Typography variant="body2" color="text.secondary" align="center">
              © 2024 Bank of Canada - Economic ML Operations Platform | 
              Build: {process.env.REACT_APP_VERSION || 'dev'} | 
              Environment: {process.env.NODE_ENV}
            </Typography>
          </Box>
        </Box>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;
