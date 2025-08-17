/**
 * AI Agent Dashboard - DeepSeek Economic Research
 * 
 * Interactive interface for AI-powered economic research and analysis
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardHeader,
  Button,
  TextField,
  Chip,
  Alert,
  CircularProgress,
  IconButton,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Avatar,
  Fab
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  Send as SendIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  AccountBalance as AccountBalanceIcon,
  Clear as ClearIcon,
  SmartToy as SmartToyIcon,
  Person as PersonIcon,
  AutoAwesome as AutoAwesomeIcon
} from '@mui/icons-material';

import ApiKeyModal from './ApiKeyModal';
import { apiService } from '../services/apiService';
import { useNotifications } from '../hooks/useNotifications';

const AIAgentDashboard = () => {
  // State management
  const [apiKeyModalOpen, setApiKeyModalOpen] = useState(false);
  const [hasApiKey, setHasApiKey] = useState(false);
  const [loading, setLoading] = useState(true);
  const [currentTab, setCurrentTab] = useState(0);
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sending, setSending] = useState(false);
  
  // Research state
  const [researchQuestion, setResearchQuestion] = useState('');
  const [researchContext, setResearchContext] = useState('');
  const [researchResult, setResearchResult] = useState(null);
  const [researching, setResearching] = useState(false);
  
  // Capabilities
  const [capabilities, setCapabilities] = useState({});
  
  const { showNotification } = useNotifications();
  const messagesEndRef = useRef(null);

  // Load initial data
  useEffect(() => {
    checkApiKeyStatus();
    loadCapabilities();
    addWelcomeMessage();
  }, []);

  // Auto-scroll chat to bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkApiKeyStatus = async () => {
    try {
      setLoading(true);
      const status = await apiService.checkApiKeyStatus();
      setHasApiKey(status.hasKey && status.valid);
    } catch (error) {
      console.error('Failed to check API key status:', error);
      setHasApiKey(false);
    } finally {
      setLoading(false);
    }
  };

  const loadCapabilities = async () => {
    try {
      const caps = await apiService.getAgentCapabilities();
      setCapabilities(caps.capabilities || {});
    } catch (error) {
      console.error('Failed to load capabilities:', error);
    }
  };

  const addWelcomeMessage = () => {
    setMessages([{
      id: 1,
      type: 'ai',
      content: `Welcome to the Bank of Canada AI Research Assistant! 🏦

I'm powered by DeepSeek AI and specialized in economic analysis. I can help you with:

• Economic indicator analysis and trends
• Monetary policy research and implications  
• Financial stability assessments
• International economic comparisons
• Central banking operations

To get started, please configure your DeepSeek API key using the settings button above, then ask me any economic question!`,
      timestamp: new Date()
    }]);
  };

  const handleApiKeySuccess = () => {
    setHasApiKey(true);
    loadCapabilities();
    showNotification('DeepSeek API key configured successfully!', 'success');
    
    // Add confirmation message
    addMessage('ai', '✅ API key configured! I\'m now ready to assist with economic research. What would you like to explore?');
  };

  const addMessage = (type, content, metadata = {}) => {
    const message = {
      id: Date.now() + Math.random(),
      type,
      content,
      timestamp: new Date(),
      ...metadata
    };
    setMessages(prev => [...prev, message]);
    return message;
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || sending) return;
    
    if (!hasApiKey) {
      setApiKeyModalOpen(true);
      return;
    }

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setSending(true);

    // Add user message
    addMessage('user', userMessage);

    try {
      const response = await apiService.chatWithAgent(userMessage);
      addMessage('ai', response.response, { 
        timestamp: new Date(response.timestamp) 
      });
    } catch (error) {
      if (apiService.isApiKeyRequired(error)) {
        setApiKeyModalOpen(true);
        addMessage('ai', '🔑 Please configure your DeepSeek API key to continue our conversation.');
      } else {
        addMessage('ai', `I apologize, but I encountered an error: ${error.message}`, {
          isError: true
        });
        showNotification('Failed to send message', 'error');
      }
    } finally {
      setSending(false);
    }
  };

  const handleResearch = async () => {
    if (!researchQuestion.trim() || researching) return;
    
    if (!hasApiKey) {
      setApiKeyModalOpen(true);
      return;
    }

    setResearching(true);
    
    try {
      const result = await apiService.conductResearch(
        researchQuestion,
        researchContext || null,
        [] // indicators - could be enhanced
      );
      setResearchResult(result);
      showNotification('Research completed successfully!', 'success');
    } catch (error) {
      if (apiService.isApiKeyRequired(error)) {
        setApiKeyModalOpen(true);
      } else {
        showNotification(apiService.formatError(error), 'error');
      }
    } finally {
      setResearching(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    addWelcomeMessage();
  };

  const renderMessage = (message) => (
    <Box 
      key={message.id}
      sx={{ 
        display: 'flex', 
        mb: 2,
        justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-start', maxWidth: '80%' }}>
        {message.type === 'ai' && (
          <Avatar sx={{ bgcolor: 'primary.main', mr: 1, mt: 0.5 }}>
            <SmartToyIcon />
          </Avatar>
        )}
        
        <Paper
          sx={{
            p: 2,
            bgcolor: message.type === 'user' ? 'primary.light' : 'grey.100',
            color: message.type === 'user' ? 'white' : 'text.primary',
            borderRadius: 2,
            ...(message.isError && { bgcolor: 'error.light' })
          }}
        >
          <Typography 
            variant="body1" 
            sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
          >
            {message.content}
          </Typography>
          <Typography 
            variant="caption" 
            sx={{ 
              opacity: 0.7, 
              mt: 1, 
              display: 'block',
              color: message.type === 'user' ? 'white' : 'text.secondary'
            }}
          >
            {message.timestamp?.toLocaleTimeString()}
          </Typography>
        </Paper>
        
        {message.type === 'user' && (
          <Avatar sx={{ bgcolor: 'secondary.main', ml: 1, mt: 0.5 }}>
            <PersonIcon />
          </Avatar>
        )}
      </Box>
    </Box>
  );

  const renderCapabilities = () => (
    <Grid container spacing={2}>
      {Object.entries(capabilities).map(([key, capability]) => (
        <Grid item xs={12} md={6} key={key}>
          <Card 
            sx={{ 
              opacity: capability.available ? 1 : 0.6,
              border: capability.available ? '1px solid' : 'none',
              borderColor: 'primary.light'
            }}
          >
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <AutoAwesomeIcon 
                  color={capability.available ? 'primary' : 'disabled'} 
                  sx={{ mr: 1 }} 
                />
                <Typography variant="h6">
                  {capability.name}
                </Typography>
                <Chip 
                  label={capability.available ? 'Available' : 'API Key Required'}
                  size="small"
                  color={capability.available ? 'success' : 'warning'}
                  sx={{ ml: 'auto' }}
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                {capability.description}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Initializing AI Research Assistant...
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
            AI Research Assistant
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Economic analysis powered by DeepSeek AI
          </Typography>
        </Box>
        
        <Box display="flex" gap={2} alignItems="center">
          <Chip
            icon={<PsychologyIcon />}
            label={hasApiKey ? 'AI Enabled' : 'Configure API Key'}
            color={hasApiKey ? 'success' : 'warning'}
            variant={hasApiKey ? 'filled' : 'outlined'}
          />
          <Button
            variant="outlined"
            startIcon={<SettingsIcon />}
            onClick={() => setApiKeyModalOpen(true)}
          >
            Settings
          </Button>
        </Box>
      </Box>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Chat Interface */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ height: 600, display: 'flex', flexDirection: 'column' }}>
            {/* Chat Header */}
            <Box 
              sx={{ 
                p: 2, 
                borderBottom: 1, 
                borderColor: 'divider',
                display: 'flex',
                justifyContent: 'between',
                alignItems: 'center'
              }}
            >
              <Typography variant="h6" fontWeight={600}>
                Chat with AI Research Assistant
              </Typography>
              <IconButton onClick={handleClearChat} size="small">
                <ClearIcon />
              </IconButton>
            </Box>

            {/* Messages */}
            <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto' }}>
              {messages.map(renderMessage)}
              {sending && (
                <Box display="flex" alignItems="center" mb={2}>
                  <Avatar sx={{ bgcolor: 'primary.main', mr: 1 }}>
                    <SmartToyIcon />
                  </Avatar>
                  <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    <Typography variant="body2" component="span">
                      AI is thinking...
                    </Typography>
                  </Paper>
                </Box>
              )}
              <div ref={messagesEndRef} />
            </Box>

            {/* Input */}
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Box display="flex" gap={1}>
                <TextField
                  fullWidth
                  placeholder="Ask me about economic indicators, policy analysis, or market trends..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                  multiline
                  maxRows={3}
                />
                <IconButton
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || sending || !hasApiKey}
                  color="primary"
                >
                  <SendIcon />
                </IconButton>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Quick Actions */}
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={600} mb={2}>
                Quick Research Topics
              </Typography>
              <List dense>
                {[
                  'Current inflation outlook for Canada',
                  'Impact of interest rate changes on housing',
                  'Unemployment trends and labor market',
                  'Exchange rate volatility analysis',
                  'Global economic risks and opportunities'
                ].map((topic, index) => (
                  <ListItem 
                    key={index}
                    button
                    onClick={() => setInputMessage(topic)}
                  >
                    <ListItemIcon>
                      <TrendingUpIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={topic}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>

            {/* Capabilities */}
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={600} mb={2}>
                AI Capabilities
              </Typography>
              {renderCapabilities()}
            </Paper>
          </Box>
        </Grid>
      </Grid>

      {/* API Key Modal */}
      <ApiKeyModal
        open={apiKeyModalOpen}
        onClose={() => setApiKeyModalOpen(false)}
        onSuccess={handleApiKeySuccess}
      />
    </Box>
  );
};

export default AIAgentDashboard;
