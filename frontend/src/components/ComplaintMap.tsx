import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Complaint } from '../types';
import { SeverityBadge, StatusBadge } from './StatusBadge';
import { Link } from 'react-router-dom';

// Function to create custom SVG color-coded markers for Leaflet
const createPinIcon = (color: string) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36" width="28" height="38">
      <path fill="${color}" stroke="#ffffff" stroke-width="2" d="M12 0C5.373 0 0 5.373 0 12c0 9 12 24 12 24s12-15 12-24c0-6.627-5.373-12-12-12z"/>
      <circle cx="12" cy="12" r="5" fill="#ffffff"/>
    </svg>
  `;
  return L.divIcon({
    html: svg,
    className: 'custom-leaflet-pin',
    iconSize: [28, 38],
    iconAnchor: [14, 38],
    popupAnchor: [0, -34]
  });
};

const getPinColor = (severity: string) => {
  switch (severity) {
    case 'CRITICAL':
      return '#ef4444'; // Red
    case 'HIGH':
      return '#f97316'; // Orange
    case 'MEDIUM':
      return '#eab308'; // Yellow
    case 'LOW':
    default:
      return '#22c55e'; // Green
  }
};

interface ComplaintMapProps {
  complaints: Complaint[];
  height?: string;
  center?: [number, number];
  zoom?: number;
}

export const ComplaintMap: React.FC<ComplaintMapProps> = ({
  complaints,
  height = '500px',
  center = [12.9716, 77.5946], // Default center (e.g. Bangalore / metro civic coords)
  zoom = 12
}) => {
  const geoComplaints = complaints.filter(c => c.latitude && c.longitude);

  return (
    <div className="w-full rounded-2xl overflow-hidden border border-slate-200/80 shadow-sm relative z-0" style={{ height }}>
      <MapContainer
        center={geoComplaints.length > 0 ? [geoComplaints[0].latitude!, geoComplaints[0].longitude!] : center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {geoComplaints.map((c) => {
          const pinColor = getPinColor(c.severity);
          const icon = createPinIcon(pinColor);

          return (
            <Marker key={c.id} position={[c.latitude!, c.longitude!]} icon={icon}>
              <Popup>
                <div className="p-1 min-w-[200px]">
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="font-mono text-xs font-bold text-slate-800">{c.id}</span>
                    <SeverityBadge severity={c.severity} size="sm" />
                  </div>
                  <h4 className="font-semibold text-sm text-slate-900 mb-1">{c.title}</h4>
                  <div className="text-xs text-slate-500 mb-2">
                    <span>Category: <strong>{c.category}</strong></span>
                  </div>
                  <div className="flex items-center justify-between text-xs mb-3">
                    <StatusBadge status={c.status} size="sm" />
                    <span className="font-bold text-slate-700">Priority: {Math.round(c.priority_score)}/100</span>
                  </div>
                  {c.address && (
                    <p className="text-[11px] text-slate-400 mb-2 truncate">📍 {c.address}</p>
                  )}
                  <Link
                    to={`/complaints/${c.id}`}
                    className="block text-center text-xs font-semibold py-1.5 px-3 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
                  >
                    View Complaint Details
                  </Link>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};
