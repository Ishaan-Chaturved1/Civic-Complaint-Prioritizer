import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Complaint } from '../types';
import { AIAnalysisCard } from '../components/AIAnalysisCard';
import { SeverityBadge, StatusBadge } from '../components/StatusBadge';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, Clock, MapPin, Building2, Calendar, UserCheck, ShieldAlert, CheckCircle, MessageSquare } from 'lucide-react';

export const ComplaintDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [complaint, setComplaint] = useState<Complaint | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Status update for officers/admins
  const { isOfficer, isAdmin } = useAuth();
  const [newStatus, setNewStatus] = useState<string>('');
  const [officerNote, setOfficerNote] = useState<string>('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    const fetchDetail = async () => {
      if (!id) return;
      try {
        const data = await api.getComplaintById(id);
        setComplaint(data);
        setNewStatus(data.status);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to retrieve complaint.');
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id]);

  const handleStatusUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!complaint || !newStatus) return;
    setUpdating(true);
    try {
      const updated = await api.updateComplaint(complaint.id, {
        status: newStatus,
        comment: officerNote
      });
      setComplaint(updated);
      setOfficerNote('');
      alert('Status updated successfully!');
    } catch (err: any) {
      alert('Failed to update status: ' + (err.response?.data?.detail || err.message));
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-20 text-center text-slate-400">
        <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        Loading complaint dossier...
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="p-6 bg-red-50 border border-red-200 rounded-2xl text-red-700">
          <p className="font-semibold">{error || 'Complaint record not found.'}</p>
          <Link to="/my-complaints" className="mt-4 inline-block text-xs font-bold text-blue-600 underline">
            Return to complaints list
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Top back nav */}
      <div>
        <Link
          to={isOfficer ? "/officer/dashboard" : isAdmin ? "/admin/dashboard" : "/my-complaints"}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Dashboard
        </Link>
      </div>

      {/* Header Banner */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-8 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="font-mono text-sm font-bold bg-slate-100 text-slate-700 px-3 py-1 rounded-lg">
              {complaint.id}
            </span>
            <SeverityBadge severity={complaint.severity} size="md" />
            <StatusBadge status={complaint.status} size="md" />
          </div>

          <div className="text-xs text-slate-400 flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" />
            Registered on {new Date(complaint.created_at).toLocaleString()}
          </div>
        </div>

        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          {complaint.title}
        </h1>

        <p className="text-sm text-slate-600 leading-relaxed font-normal">
          {complaint.description}
        </p>

        <div className="pt-4 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-slate-600">
          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-blue-600" />
            <span>Assigned: <strong>{complaint.department}</strong></span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-500" />
            <span>SLA: <strong>{complaint.sla_hours} Hours Target</strong></span>
          </div>
          {complaint.address && (
            <div className="flex items-center gap-2 truncate">
              <MapPin className="w-4 h-4 text-emerald-500 shrink-0" />
              <span className="truncate">Location: <strong>{complaint.address}</strong></span>
            </div>
          )}
        </div>
      </div>

      {/* Multimodal AI Card */}
      <AIAnalysisCard complaint={complaint} />

      {/* Evidence Visual Preview (if uploaded) */}
      {complaint.image_url && (
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 mb-4">
            Visual Damage Inspection Photo
          </h3>
          <div className="max-w-2xl mx-auto rounded-xl overflow-hidden border border-slate-200 shadow-sm bg-slate-900">
            <img
              src={complaint.image_url.startsWith('http') ? complaint.image_url : `http://localhost:8000${complaint.image_url}`}
              alt="Visual Evidence"
              className="w-full max-h-[500px] object-contain mx-auto"
            />
          </div>
          <p className="text-xs text-slate-400 text-center mt-2">
            Annotated detection boxes generated via YOLO Computer Vision model.
          </p>
        </div>
      )}

      {/* Officer / Admin Action Panel */}
      {(isOfficer || isAdmin) && (
        <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-blue-400" />
            <h3 className="font-bold text-base">Officer Grievance Resolution Action</h3>
          </div>
          <form onSubmit={handleStatusUpdate} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Update Status</label>
              <select
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white outline-none"
              >
                <option value="SUBMITTED">Submitted</option>
                <option value="IN_REVIEW">In Review</option>
                <option value="ASSIGNED">Assigned</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="RESOLVED">Resolved</option>
                <option value="REJECTED">Rejected</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs text-slate-400 mb-1">Resolution / Progress Notes</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g. Work order issued to zonal road contractor..."
                  value={officerNote}
                  onChange={(e) => setOfficerNote(e.target.value)}
                  className="flex-1 px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white outline-none"
                />
                <button
                  type="submit"
                  disabled={updating}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 font-semibold rounded-xl text-xs transition disabled:opacity-50"
                >
                  {updating ? 'Saving...' : 'Apply Update'}
                </button>
              </div>
            </div>
          </form>
        </div>
      )}

      {/* Audit History Timeline */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 mb-6 flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-blue-600" />
          Complaint Lifecycle Audit Trail
        </h3>

        <div className="relative border-l-2 border-slate-200 ml-4 space-y-6 pb-2">
          {complaint.history && complaint.history.length > 0 ? (
            complaint.history.map((h, i) => (
              <div key={i} className="relative pl-6">
                <span className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-blue-600 border-2 border-white ring-2 ring-blue-100" />
                <div className="flex flex-wrap items-center justify-between text-xs gap-2">
                  <span className="font-bold text-slate-800">
                    Status Transition: <span className="text-blue-600">{h.new_status}</span>
                  </span>
                  <span className="text-slate-400">{new Date(h.timestamp).toLocaleString()}</span>
                </div>
                {h.comment && (
                  <p className="text-xs text-slate-600 mt-1 bg-slate-50 border border-slate-100 p-2.5 rounded-lg">
                    {h.comment}
                  </p>
                )}
              </div>
            ))
          ) : (
            <div className="pl-6 text-xs text-slate-400">No previous state changes.</div>
          )}
        </div>
      </div>
    </div>
  );
};
