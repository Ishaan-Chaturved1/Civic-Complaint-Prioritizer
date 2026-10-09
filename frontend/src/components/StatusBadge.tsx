import React from 'react';
import { SeverityLevel, ComplaintStatus } from '../types';

interface SeverityBadgeProps {
  severity: SeverityLevel;
  size?: 'sm' | 'md' | 'lg';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, size = 'md' }) => {
  const styles = {
    CRITICAL: 'bg-red-50 text-red-700 border-red-200 ring-red-500/20',
    HIGH: 'bg-orange-50 text-orange-700 border-orange-200 ring-orange-500/20',
    MEDIUM: 'bg-amber-50 text-amber-700 border-amber-200 ring-amber-500/20',
    LOW: 'bg-emerald-50 text-emerald-700 border-emerald-200 ring-emerald-500/20'
  };

  const dotColors = {
    CRITICAL: 'bg-red-500 animate-pulse',
    HIGH: 'bg-orange-500',
    MEDIUM: 'bg-amber-500',
    LOW: 'bg-emerald-500'
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3.5 py-1.5 font-semibold'
  };

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium border rounded-full ring-1 ${styles[severity] || styles.LOW} ${sizeClasses[size]}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotColors[severity] || dotColors.LOW}`} />
      {severity}
    </span>
  );
};

interface StatusBadgeProps {
  status: ComplaintStatus | string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const statusStyles: Record<string, string> = {
    SUBMITTED: 'bg-blue-50 text-blue-700 border-blue-200',
    IN_REVIEW: 'bg-purple-50 text-purple-700 border-purple-200',
    ASSIGNED: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    IN_PROGRESS: 'bg-cyan-50 text-cyan-700 border-cyan-200',
    RESOLVED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    REJECTED: 'bg-slate-100 text-slate-700 border-slate-200'
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1 font-medium'
  };

  const formatText = (text: string) => {
    return text.replace('_', ' ').toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
  };

  return (
    <span className={`inline-flex items-center border rounded-md ${statusStyles[status] || 'bg-slate-50 text-slate-700 border-slate-200'} ${sizeClasses[size]}`}>
      {formatText(status)}
    </span>
  );
};
