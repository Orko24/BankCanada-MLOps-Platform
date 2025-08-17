/**
 * Notifications Hook for Bank of Canada MLOps Platform
 * 
 * Provides a consistent interface for showing notifications
 * using notistack throughout the application
 */

import { useSnackbar } from 'notistack';
import { useCallback } from 'react';

export const useNotifications = () => {
  const { enqueueSnackbar, closeSnackbar } = useSnackbar();

  const showNotification = useCallback((message, variant = 'default', options = {}) => {
    const defaultOptions = {
      variant,
      autoHideDuration: variant === 'error' ? 6000 : 4000,
      preventDuplicate: true,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right'
      },
      ...options
    };

    return enqueueSnackbar(message, defaultOptions);
  }, [enqueueSnackbar]);

  const showSuccess = useCallback((message, options = {}) => {
    return showNotification(message, 'success', options);
  }, [showNotification]);

  const showError = useCallback((message, options = {}) => {
    return showNotification(message, 'error', options);
  }, [showNotification]);

  const showWarning = useCallback((message, options = {}) => {
    return showNotification(message, 'warning', options);
  }, [showNotification]);

  const showInfo = useCallback((message, options = {}) => {
    return showNotification(message, 'info', options);
  }, [showNotification]);

  const dismissNotification = useCallback((key) => {
    closeSnackbar(key);
  }, [closeSnackbar]);

  const dismissAll = useCallback(() => {
    closeSnackbar();
  }, [closeSnackbar]);

  return {
    showNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    dismissNotification,
    dismissAll
  };
};
