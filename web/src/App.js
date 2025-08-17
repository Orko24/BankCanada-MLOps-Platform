import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
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
  DataUsage as DataUsageIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { SnackbarProvider } from 'notistack';

// Import page components
import EconomicDashboard from './components/EconomicDashboard';
import ForecastingDashboard from './components/ForecastingDashboard';
import ModelMonitoring from './components/ModelMonitoring';
import SystemMonitoring from './components/SystemMonitoring';
import DataQuality from './components/DataQuality';
import AIAgentDashboard from './components/AIAgentDashboard';
import Settings from './components/Settings';

// Custom hook for notifications
import { useNotifications } from './hooks/useNotifications';

// Bank of Canada theme
const bankCanadaTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#C41E3A', // Bank of Canada red
      light: '#E53E5A',
      dark: '#8B1429',
      contrastText: '#FFFFFF'
    },
    secondary: {
      main: '#1976D2',
      light: '#42A5F5',
      dark: '#1565C0'
    },
    background: {
      default: '#F7FAFC',
      paper: '#FFFFFF'
    }
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  }
});

// Navigation items with HTML pages
const navigationItems = [
  { id: 'dashboard', label: 'Economic Dashboard', icon: DashboardIcon, href: './index.html' },
  { id: 'forecasting', label: 'ML Forecasting', icon: TrendingUpIcon, href: './forecasting.html' },
  { id: 'research_assistant', label: 'AI Research Assistant', icon: PsychologyIcon, href: './research_assistant.html' },
  { id: 'model_monitoring', label: 'Model Monitoring', icon: AssessmentIcon, href: './model_monitoring.html' },
  { id: 'system_health', label: 'System Health', icon: SpeedIcon, href: './system_health.html' },
  { id: 'data_quality', label: 'Data Quality', icon: DataUsageIcon, href: './data_quality.html' },
  { id: 'settings', label: 'Settings', icon: SettingsIcon, href: './settings.html' }
];

function App() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);

  // Get current page from window variable
  const currentPage = window.CURRENT_PAGE || 'dashboard';

  // Custom hooks
  const { showNotification } = useNotifications();

  // Get current page info
  const getCurrentPage = () => {
    const current = navigationItems.find(item => item.id === currentPage);
    return current || navigationItems[0];
  };

  // Fetch system status
  useEffect(() => {
    const fetchSystemStatus = async () => {
      try {
        const response = await fetch('/api/system/info');
        if (response.ok) {
          const data = await response.json();
          setSystemStatus(data);
        }
      } catch (error) {
        console.error('Failed to fetch system status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSystemStatus();
  }, []);

  // Render the appropriate component based on current page
  const renderCurrentComponent = () => {
    switch (currentPage) {
      case 'forecasting':
        return <ForecastingDashboard />;
      case 'research_assistant':
        return <AIAgentDashboard />;
      case 'model_monitoring':
        return <ModelMonitoring />;
      case 'system_health':
        return <SystemMonitoring systemStatus={systemStatus} />;
      case 'data_quality':
        return <DataQuality />;
      case 'settings':
        return <Settings />;
      case 'dashboard':
      default:
        return <EconomicDashboard />;
    }
  };

  return (
    <ThemeProvider theme={bankCanadaTheme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3}>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          
          {/* App Bar */}
          <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar>
              <IconButton
                edge="start"
                color="inherit"
                aria-label="menu"
                onClick={() => setDrawerOpen(true)}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
              
              <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
                {getCurrentPage().label} - Bank of Canada MLOps
              </Typography>

              {/* Status indicator */}
              {systemStatus && (
                <Chip
                  label={systemStatus.status || 'Unknown'}
                  color={systemStatus.status === 'healthy' ? 'success' : 'warning'}
                  size="small"
                  sx={{ mr: 2 }}
                />
              )}

              {/* Notifications */}
              <IconButton color="inherit">
                <Badge badgeContent={notifications.length} color="secondary">
                  <NotificationsIcon />
                </Badge>
              </IconButton>

              {/* User menu */}
              <IconButton color="inherit">
                <AccountCircleIcon />
              </IconButton>
            </Toolbar>
          </AppBar>

          {/* Navigation Drawer */}
          <Drawer
            anchor="left"
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
            sx={{
              width: 280,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: 280,
                boxSizing: 'border-box',
                pt: 8
              }
            }}
          >
            <Box sx={{ p: 2 }}>
              <Typography variant="h6" color="primary" fontWeight={600}>
                MLOps Platform
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Bank of Canada
              </Typography>
            </Box>
            
            <Divider />
            
            <List>
              {navigationItems.map((item) => (
                <ListItem key={item.id} disablePadding>
                  <ListItemButton
                    component="a"
                    href={item.href}
                    selected={currentPage === item.id}
                    sx={{
                      '&.Mui-selected': {
                        backgroundColor: 'primary.light',
                        '&:hover': {
                          backgroundColor: 'primary.light',
                        },
                      },
                      textDecoration: 'none',
                      color: 'inherit'
                    }}
                  >
                    <ListItemIcon>
                      <item.icon color={currentPage === item.id ? 'primary' : 'inherit'} />
                    </ListItemIcon>
                    <ListItemText 
                      primary={item.label}
                      primaryTypographyProps={{
                        fontWeight: currentPage === item.id ? 600 : 400
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
            <Container maxWidth="xl">
              {renderCurrentComponent()}
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
              © 2024 Bank of Canada - Economic ML Operations Platform
            </Typography>
          </Box>
        </Box>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;