/**
 * Databricks Configuration Modal - Similar to DeepSeek API Key Modal
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Alert,
  Box,
  Typography,
  CircularProgress,
  IconButton
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { apiService } from '../services/apiService';

const DatabricksConfigModal = ({ open, onClose, onConfigured }) => {
  const [host, setHost] = useState('');
  const [token, setToken] = useState('');
  const [workspaceId, setWorkspaceId] = useState('');
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleTest = async () => {
    if (!host || !token) {
      setError('Host and token are required');
      return;
    }

    setTesting(true);
    setError(null);

    try {
      await apiService.testDatabricksConfig({ host, token, workspace_id: workspaceId });
      setSuccess(true);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to test Databricks connection');
      setSuccess(false);
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    if (!host || !token) {
      setError('Host and token are required');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await apiService.setDatabricksConfig({ host, token, workspace_id: workspaceId });
      onConfigured?.();
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to save Databricks configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    setHost('');
    setToken('');
    setWorkspaceId('');
    setError(null);
    setSuccess(false);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Configure Databricks Connection</Typography>
          <IconButton onClick={handleClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box display="flex" flexDirection="column" gap={3} mt={1}>
          <Alert severity="info">
            Configure your Databricks workspace connection to access real economic data.
            This configuration is saved per session for security.
          </Alert>
          
          <TextField
            label="Databricks Host URL"
            placeholder="https://your-workspace.cloud.databricks.com"
            value={host}
            onChange={(e) => setHost(e.target.value)}
            fullWidth
            required
            helperText="Your Databricks workspace URL"
          />
          
          <TextField
            label="Access Token"
            type="password"
            placeholder="dapi********************************"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            fullWidth
            required
            helperText="Personal Access Token from Databricks"
          />
          
          <TextField
            label="Workspace ID (Optional)"
            placeholder="1234567890123456"
            value={workspaceId}
            onChange={(e) => setWorkspaceId(e.target.value)}
            fullWidth
            helperText="Optional workspace identifier"
          />
          
          {error && (
            <Alert severity="error">
              {error}
            </Alert>
          )}
          
          {success && (
            <Alert severity="success">
              ✅ Databricks connection successful!
            </Alert>
          )}
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose} disabled={testing || saving}>
          Cancel
        </Button>
        
        <Button 
          onClick={handleTest} 
          disabled={!host || !token || testing || saving}
          variant="outlined"
        >
          {testing ? <CircularProgress size={20} /> : 'Test Connection'}
        </Button>
        
        <Button 
          onClick={handleSave} 
          disabled={!host || !token || testing || saving}
          variant="contained"
        >
          {saving ? <CircularProgress size={20} /> : 'Save Configuration'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DatabricksConfigModal;
