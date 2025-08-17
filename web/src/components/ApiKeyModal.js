/**
 * API Key Configuration Modal
 * 
 * Allows users to enter their DeepSeek API key dynamically
 * without needing to restart the application
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Link,
  Chip,
  Card,
  CardContent
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon
} from '@mui/icons-material';

import { apiService } from '../services/apiService';

const ApiKeyModal = ({ open, onClose, onSuccess }) => {
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [keyStatus, setKeyStatus] = useState(null);
  const [testingKey, setTestingKey] = useState(false);

  // Check existing key status when modal opens
  useEffect(() => {
    if (open) {
      checkExistingKey();
    }
  }, [open]);

  const checkExistingKey = async () => {
    try {
      const status = await apiService.checkApiKeyStatus();
      setKeyStatus(status);
      if (status.hasKey) {
        setApiKey('••••••••••••••••'); // Masked display
      }
    } catch (error) {
      console.error('Failed to check API key status:', error);
    }
  };

  const handleTestKey = async () => {
    if (!apiKey || apiKey.includes('•')) return;

    setTestingKey(true);
    setError('');

    try {
      const result = await apiService.testApiKey(apiKey);
      if (result.valid) {
        setKeyStatus({ hasKey: true, valid: true, provider: 'DeepSeek' });
        setError('');
      } else {
        setError('API key is invalid. Please check your key and try again.');
        setKeyStatus({ hasKey: false, valid: false });
      }
    } catch (error) {
      setError('Failed to test API key. Please check your connection.');
      setKeyStatus({ hasKey: false, valid: false });
    } finally {
      setTestingKey(false);
    }
  };

  const handleSaveKey = async () => {
    if (!apiKey || apiKey.includes('•')) {
      setError('Please enter a valid API key');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await apiService.setApiKey(apiKey);
      
      // Test the key after saving
      const testResult = await apiService.testApiKey(apiKey);
      if (testResult.valid) {
        onSuccess();
        onClose();
      } else {
        setError('API key was saved but failed validation test');
      }
    } catch (error) {
      setError('Failed to save API key: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveKey = async () => {
    setLoading(true);
    try {
      await apiService.removeApiKey();
      setApiKey('');
      setKeyStatus({ hasKey: false, valid: false });
      setError('');
    } catch (error) {
      setError('Failed to remove API key');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setApiKey('');
    setError('');
    setKeyStatus(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <PsychologyIcon color="primary" />
          <Typography variant="h6">
            AI Research Agent Configuration
          </Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              To enable the AI Research Agent, you need a DeepSeek API key. 
              DeepSeek offers excellent performance at a fraction of the cost of other providers.
            </Typography>
          </Alert>

          {/* Current Status */}
          {keyStatus && (
            <Card sx={{ mb: 3, bgcolor: keyStatus.valid ? 'success.light' : 'warning.light' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  {keyStatus.valid ? (
                    <CheckCircleIcon color="success" />
                  ) : (
                    <SecurityIcon color="warning" />
                  )}
                  <Typography variant="h6">
                    {keyStatus.hasKey ? 'API Key Configured' : 'No API Key'}
                  </Typography>
                </Box>
                
                {keyStatus.hasKey && (
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip 
                      label={keyStatus.provider || 'DeepSeek'} 
                      size="small" 
                      color={keyStatus.valid ? 'success' : 'warning'}
                    />
                    <Typography variant="body2" color="text.secondary">
                      Status: {keyStatus.valid ? 'Active' : 'Invalid'}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          )}

          {/* API Key Input */}
          <TextField
            fullWidth
            label="DeepSeek API Key"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-..."
            helperText="Your API key is stored securely in your session and never saved permanently"
            sx={{ mb: 2 }}
            InputProps={{
              endAdornment: testingKey && <CircularProgress size={20} />
            }}
          />

          {/* Test Button */}
          <Button
            variant="outlined"
            onClick={handleTestKey}
            disabled={!apiKey || apiKey.includes('•') || testingKey}
            sx={{ mb: 2, mr: 1 }}
          >
            {testingKey ? 'Testing...' : 'Test Key'}
          </Button>

          {/* Error Display */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Instructions */}
          <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="h6" gutterBottom>
              <InfoIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              How to get your DeepSeek API Key:
            </Typography>
            <Typography variant="body2" paragraph>
              1. Visit <Link href="https://platform.deepseek.com" target="_blank" rel="noopener">platform.deepseek.com</Link>
            </Typography>
            <Typography variant="body2" paragraph>
              2. Sign up or log in to your account
            </Typography>
            <Typography variant="body2" paragraph>
              3. Go to API Keys section and create a new key
            </Typography>
            <Typography variant="body2" paragraph>
              4. Add credits (usually $5 lasts for months)
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
              💰 Cost: ~$0.14 per 1M tokens (100x cheaper than other providers!)
            </Typography>
          </Box>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>
          Cancel
        </Button>
        
        {keyStatus?.hasKey && (
          <Button 
            onClick={handleRemoveKey} 
            color="warning"
            disabled={loading}
          >
            Remove Key
          </Button>
        )}
        
        <Button
          onClick={handleSaveKey}
          variant="contained"
          disabled={!apiKey || apiKey.includes('•') || loading}
        >
          {loading ? <CircularProgress size={20} /> : 'Save & Enable AI Agent'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ApiKeyModal;
