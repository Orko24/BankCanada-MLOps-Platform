/**
 * Main API Service for Bank of Canada MLOps Platform
 * 
 * Centralized service for all API communications
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds
    });

    // Generate session ID for AI agent features
    this.sessionId = this.generateSessionId();
    
    // Add interceptors
    this.setupInterceptors();
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  setupInterceptors() {
    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        // Add session ID for AI agent features
        config.headers['X-Session-ID'] = this.sessionId;
        
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
        
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle authentication errors
          localStorage.removeItem('auth_token');
          // Redirect to login if needed
        }
        return Promise.reject(error);
      }
    );
  }

  // System endpoints
  async getSystemInfo() {
    try {
      const response = await this.api.get('/api/system/info');
      return response.data;
    } catch (error) {
      console.error('Failed to get system info:', error);
      return null;
    }
  }

  async getHealthCheck() {
    try {
      const response = await this.api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      return null;
    }
  }

  // Economic data endpoints
  async getIndicators(category = null, isActive = true) {
    try {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      params.append('is_active', isActive);

      const response = await this.api.get(`/api/economic-data/indicators?${params}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch indicators');
    }
  }

  async getIndicatorData(indicatorCode, startDate = null, endDate = null) {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await this.api.get(
        `/api/economic-data/indicators/${indicatorCode}/data?${params}`
      );
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch indicator data');
    }
  }

  async getLatestIndicatorData(indicatorCode) {
    try {
      const response = await this.api.get(
        `/api/economic-data/indicators/${indicatorCode}/latest`
      );
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch latest data');
    }
  }

  async getDashboardSummary() {
    try {
      const response = await this.api.get('/api/economic-data/dashboard/summary');
      return response.data;
    } catch (error) {
      console.error('Failed to get dashboard summary:', error);
      return null;
    }
  }

  async getRecentAlerts() {
    try {
      // Mock implementation - replace with actual endpoint
      return [];
    } catch (error) {
      console.error('Failed to get recent alerts:', error);
      return [];
    }
  }

  // AI Agent endpoints
  async setApiKey(apiKey) {
    try {
      const response = await this.api.post('/api/ai-agents/api-key/set', {
        api_key: apiKey
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to set API key');
    }
  }

  async testApiKey(apiKey) {
    try {
      const response = await this.api.post('/api/ai-agents/api-key/test', {
        api_key: apiKey
      });
      return response.data.result;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to test API key');
    }
  }

  async checkApiKeyStatus() {
    try {
      const response = await this.api.get('/api/ai-agents/api-key/status');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to check API key status');
    }
  }

  async removeApiKey() {
    try {
      const response = await this.api.delete('/api/ai-agents/api-key');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to remove API key');
    }
  }

  async conductResearch(question, context = null, indicators = []) {
    try {
      const response = await this.api.post('/api/ai-agents/research', {
        question,
        context,
        indicators
      });
      return response.data.result;
    } catch (error) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('No API key')) {
        throw new Error('API_KEY_REQUIRED');
      }
      throw new Error(error.response?.data?.detail || 'Research failed');
    }
  }

  async chatWithAgent(message) {
    try {
      const response = await this.api.post('/api/ai-agents/chat', {
        message
      });
      return response.data;
    } catch (error) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('No API key')) {
        throw new Error('API_KEY_REQUIRED');
      }
      throw new Error(error.response?.data?.detail || 'Chat failed');
    }
  }

  async getAgentCapabilities() {
    try {
      const response = await this.api.get('/api/ai-agents/capabilities');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get capabilities');
    }
  }

  // ML model endpoints
  async getModels() {
    try {
      const response = await this.api.get('/api/models');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch models');
    }
  }

  async makePrediction(modelName, inputData) {
    try {
      const response = await this.api.post(`/api/predictions/predict/${modelName}`, {
        input_data: inputData,
        include_confidence: true
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Prediction failed');
    }
  }

  // Utility methods
  isApiKeyRequired(error) {
    return error.message === 'API_KEY_REQUIRED';
  }

  formatError(error) {
    if (this.isApiKeyRequired(error)) {
      return 'Please configure your DeepSeek API key to use AI features.';
    }
    return error.message || 'An unexpected error occurred.';
  }

  // Databricks Configuration endpoints
  async setDatabricksConfig(config) {
    try {
      const response = await this.api.post('/api/databricks-config/set', config);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to set Databricks configuration');
    }
  }

  async testDatabricksConfig(config) {
    try {
      const response = await this.api.post('/api/databricks-config/test', config);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to test Databricks configuration');
    }
  }

  async getDatabricksConfigStatus() {
    try {
      const response = await this.api.get('/api/databricks-config/status');
      return response.data;
    } catch (error) {
      return { has_config: false };
    }
  }

  async removeDatabricksConfig() {
    try {
      const response = await this.api.delete('/api/databricks-config/');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to remove Databricks configuration');
    }
  }
}

// Create and export singleton instance
export const apiService = new ApiService();
export default apiService;
