/**
 * AI Agent Service for DeepSeek integration
 * 
 * Handles dynamic API key management and AI agent interactions
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class AIAgentService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add session ID to all requests
    this.sessionId = this.generateSessionId();
    this.api.interceptors.request.use((config) => {
      config.headers['X-Session-ID'] = this.sessionId;
      return config;
    });
  }

  generateSessionId() {
    // Generate a simple session ID for the browser session
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // API Key Management
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

  // AI Agent Interactions
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

  async getCapabilities() {
    try {
      const response = await this.api.get('/api/ai-agents/capabilities');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get capabilities');
    }
  }

  // Utility Methods
  isApiKeyRequired(error) {
    return error.message === 'API_KEY_REQUIRED';
  }

  formatError(error) {
    if (this.isApiKeyRequired(error)) {
      return 'Please configure your DeepSeek API key to use AI features.';
    }
    return error.message || 'An unexpected error occurred.';
  }
}

// Create and export a singleton instance
export const aiAgentService = new AIAgentService();
export default aiAgentService;
