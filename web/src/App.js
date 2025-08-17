import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, Link } from 'react-router-dom';
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

// Bank of Canada theme
const bankCanadaTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#C41E3A',
      light: '#E53E3E',
      dark: '#9B1C32',
      contrastText: '#FFFFFF'
    },
    secondary: {
      main: '#2B6CB0',
      light: '#4299E1',
      dark: '#2A69AC'
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

// Navigation items
const navigationItems = [
  { id: 'dashboard', label: 'Economic Dashboard', icon: DashboardIcon, path: '/' },
  { id: 'forecasting', label: 'ML Forecasting', icon: TrendingUpIcon, path: '/forecasting' },
  { id: 'research_assistant', label: 'AI Research Assistant', icon: PsychologyIcon, path: '/research_assistant' },
  { id: 'model_monitoring', label: 'Model Monitoring', icon: AssessmentIcon, path: '/model_monitoring' },
  { id: 'system_health', label: 'System Health', icon: SpeedIcon, path: '/system_health' },
  { id: 'data_quality', label: 'Data Quality', icon: DataUsageIcon, path: '/data_quality' },
  { id: 'settings', label: 'Settings', icon: SettingsIcon, path: '/settings' }
];

// Layout Component
function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Get current page info
  const getCurrentPage = () => {
    return navigationItems.find(item => item.path === location.pathname) || navigationItems[0];
  };

  const currentPage = getCurrentPage();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            onClick={() => setDrawerOpen(true)}
            edge="start"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            {currentPage.label} - Bank of Canada MLOps
          </Typography>

          <IconButton color="inherit" sx={{ mr: 1 }}>
            <Badge badgeContent={0} color="secondary">
              <NotificationsIcon />
            </Badge>
          </IconButton>

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
        ModalProps={{ keepMounted: true }}
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
                selected={location.pathname === item.path}
                onClick={() => {
                  navigate(item.path);
                  setDrawerOpen(false);
                }}
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
                  <item.icon color={location.pathname === item.path ? 'primary' : 'inherit'} />
                </ListItemIcon>
                <ListItemText 
                  primary={item.label}
                  primaryTypographyProps={{
                    fontWeight: location.pathname === item.path ? 600 : 400
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
          {children}
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
  );
}

// Main App with Routes
function App() {
  return (
    <Router>
      <ThemeProvider theme={bankCanadaTheme}>
        <CssBaseline />
        <SnackbarProvider maxSnack={3}>
          <Layout>
            <Routes>
              <Route path="/" element={<EconomicDashboard />} />
              <Route path="/forecasting" element={<ForecastingDashboard />} />
              <Route path="/research_assistant" element={<AIAgentDashboard />} />
              <Route path="/model_monitoring" element={<ModelMonitoring />} />
              <Route path="/system_health" element={<SystemMonitoring />} />
              <Route path="/data_quality" element={<DataQuality />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
        </SnackbarProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;