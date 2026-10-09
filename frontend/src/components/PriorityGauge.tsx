import React from 'react';

interface PriorityGaugeProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
}

export const PriorityGauge: React.FC<PriorityGaugeProps> = ({
  score,
  size = 90,
  strokeWidth = 8,
  showLabel = true
}) => {
  const safeScore = Math.max(0, Math.min(100, score));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (safeScore / 100) * circumference;

  const getColor = (s: number) => {
    if (s >= 90) return '#ef4444'; // Red (Critical)
    if (s >= 75) return '#f97316'; // Orange (High)
    if (s >= 50) return '#eab308'; // Amber (Medium)
    return '#22c55e'; // Green (Low)
  };

  const color = getColor(safeScore);

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="rotate-[-90deg]">
          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#e2e8f0"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Animated Progress Ring */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-xl font-bold tracking-tight text-slate-800">
            {Math.round(safeScore)}
          </span>
          <span className="text-[10px] uppercase font-semibold text-slate-400 -mt-1">
            Score
          </span>
        </div>
      </div>
      {showLabel && (
        <span
          className="mt-2 text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded"
          style={{ color: color, backgroundColor: `${color}15` }}
        >
          {safeScore >= 90 ? 'Critical' : safeScore >= 75 ? 'High' : safeScore >= 50 ? 'Medium' : 'Low'}
        </span>
      )}
    </div>
  );
};
