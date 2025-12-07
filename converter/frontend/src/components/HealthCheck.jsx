import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, WifiOff } from 'lucide-react';
import './HealthCheck.css';

function HealthCheck({ status }) {
  const getStatusInfo = () => {
    switch (status) {
      case 'connected':
        return {
          icon: CheckCircle,
          text: 'Backend Connected',
          className: 'connected',
          color: '#28a745'
        };
      case 'disconnected':
        return {
          icon: WifiOff,
          text: 'Backend Disconnected',
          className: 'disconnected',
          color: '#dc3545'
        };
      case 'unknown':
      default:
        return {
          icon: AlertCircle,
          text: 'Checking Backend...',
          className: 'checking',
          color: '#ffc107'
        };
    }
  };

  const statusInfo = getStatusInfo();
  const Icon = statusInfo.icon;

  return (
    <div className={`health-check ${statusInfo.className}`}>
      <Icon size={16} color={statusInfo.color} />
      <span>{statusInfo.text}</span>
    </div>
  );
}

export default HealthCheck;
