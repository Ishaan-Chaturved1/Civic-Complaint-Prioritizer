import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { Complaint } from '../types';
import { SeverityBadge, StatusBadge } from '../components/StatusBadge';
import { Clock, Building2, CheckCircle2, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';

export const OfficerDashboardPage: React.FC = () => {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  const fetchComplaints = async () => {
    try {
      const data = await api.getOfficerComplaints();
      setComplaints(data);
    } catch (err) {
      console.error('Failed to load officer complaints:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, []);

  const handleQuickStatusChange = async (id: string, newStatus: string) => {
    try {
      await api.updateOfficerStatus(id, newStatus, `Updated via Officer Quick Console`);
      fetchComplaints();
    } catch (err: any) {
      alert('Failed to update status: ' + (err.response?.data?.detail || err.message));
    }
  };

  const filtered = complaints.filter(c => !statusFilter || c.status === statusFilter);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2.5">
          <ShieldCheck className="w-7 h-7 text-blue-600" />
          Field Officer Operations Console
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Review complaints routed to your department, triage by AI priority, update live progress, and close resolved tickets.
        </p>
      </div>

      {/* Filter / Summary Tabs */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-wrap gap-4 items-center justify-between">
        <div className="flex gap-2">
          {['', 'SUBMITTED', 'IN_PROGRESS', 'RESOLVED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                statusFilter === st
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {st === '' ? 'All Assigned' : st.replace('_', ' ')}
            </button>
          ))}
        </div>

        <span className="text-xs text-slate-400 font-medium">
          Showing {filtered.length} tasks
        </span>
      </div>

      {/* Complaints Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-100">
              <tr>
                <th className="py-3.5 px-4">Complaint ID</th>
                <th className="py-3.5 px-4">Issue Title</th>
                <th className="py-3.5 px-4">Severity & Priority</th>
                <th className="py-3.5 px-4">Target SLA</th>
                <th className="py-3.5 px-4">Current Status</th>
                <th className="py-3.5 px-4 text-right">Quick Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {filtered.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50/60 transition">
                  <td className="py-3.5 px-4 font-mono font-bold text-slate-900">{c.id}</td>
                  <td className="py-3.5 px-4">
                    <Link to={`/complaints/${c.id}`} className="font-semibold text-slate-900 hover:text-blue-600">
                      {c.title}
                    </Link>
                    <div className="text-[11px] text-slate-400">{c.category}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      <SeverityBadge severity={c.severity} size="sm" />
                      <span className="font-bold text-slate-800">{Math.round(c.priority_score)}/100</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-medium text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded">
                      {c.sla_hours}h
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <StatusBadge status={c.status} size="sm" />
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="inline-flex items-center gap-1.5">
                      {c.status !== 'IN_PROGRESS' && c.status !== 'RESOLVED' && (
                        <button
                          onClick={() => handleQuickStatusChange(c.id, 'IN_PROGRESS')}
                          className="px-2.5 py-1 bg-cyan-50 border border-cyan-200 text-cyan-700 hover:bg-cyan-100 font-semibold rounded-lg text-[11px] transition"
                        >
                          Start Work
                        </button>
                      )}
                      {c.status !== 'RESOLVED' && (
                        <button
                          onClick={() => handleQuickStatusChange(c.id, 'RESOLVED')}
                          className="px-2.5 py-1 bg-emerald-50 border border-emerald-200 text-emerald-700 hover:bg-emerald-100 font-semibold rounded-lg text-[11px] transition"
                        >
                          Mark Resolved
                        </button>
                      )}
                      <Link
                        to={`/complaints/${c.id}`}
                        className="p-1 text-slate-400 hover:text-blue-600 transition"
                        title="View Full Details"
                      >
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
