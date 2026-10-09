import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Complaint } from '../types';
import { ComplaintMap } from '../components/ComplaintMap';
import { MapPin, Filter, Layers, Info } from 'lucide-react';

export const AdminMapPage: React.FC = () => {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  useEffect(() => {
    const fetchComplaints = async () => {
      try {
        const data = await api.getComplaints();
        setComplaints(data);
      } catch (err) {
        console.error('Failed to load map complaints:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchComplaints();
  }, []);

  const filtered = complaints.filter((c) => {
    const matchesSev = !severityFilter || c.severity === severityFilter;
    const matchesCat = !categoryFilter || c.category === categoryFilter;
    return matchesSev && matchesCat;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2.5">
            <MapPin className="w-7 h-7 text-red-500" />
            Geographic Civic Hotspot Map
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Visualizes civic complaints geographically. Pins are color-coded by AI priority severity.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 bg-white px-4 py-2 rounded-xl border border-slate-200 text-xs font-semibold shadow-sm">
          <span className="flex items-center gap-1.5 text-red-600">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500" /> Critical (≥90)
          </span>
          <span className="flex items-center gap-1.5 text-orange-600">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500" /> High (75-89)
          </span>
          <span className="flex items-center gap-1.5 text-amber-600">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Medium (50-74)
          </span>
          <span className="flex items-center gap-1.5 text-emerald-600">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Low (&lt;50)
          </span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
          <Filter className="w-4 h-4 text-blue-600" /> Filters:
        </div>

        <div className="flex flex-wrap gap-3">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-200 rounded-xl text-xs bg-white font-medium text-slate-700 outline-none"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-200 rounded-xl text-xs bg-white font-medium text-slate-700 outline-none"
          >
            <option value="">All Categories</option>
            <option value="Road Damage">Road Damage</option>
            <option value="Garbage">Garbage</option>
            <option value="Water Supply">Water Supply</option>
            <option value="Sewage">Sewage</option>
            <option value="Drainage">Drainage</option>
            <option value="Public Safety">Public Safety</option>
          </select>
        </div>
      </div>

      {/* Map */}
      <ComplaintMap complaints={filtered} height="650px" />
    </div>
  );
};
