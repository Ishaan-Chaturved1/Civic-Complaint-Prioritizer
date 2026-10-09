import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Brain, Eye, Cpu, ArrowRight, Activity, MapPin, CheckCircle2, AlertOctagon } from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { isAuthenticated, isCitizen, isOfficer, isAdmin } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 bg-gradient-to-b from-slate-900 via-navy-900 to-slate-950 text-white">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-600/15 via-transparent to-transparent pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-400/20 text-blue-300 text-xs font-semibold">
              <Activity className="w-3.5 h-3.5 text-blue-400" />
              Next-Gen Municipal AI Governance
            </div>

            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight">
              Civic Complaint <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-teal-300 to-sky-400">
                Prioritizer & Router
              </span>
            </h1>

            <p className="text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
              A Multimodal AI Platform that cleans civic grievance text, detects road & urban waste damages via Computer Vision, calculates transparent 0–100 priority scores, and routes complaints with automated SLAs.
            </p>

            <div className="pt-4 flex flex-wrap justify-center gap-4">
              {isAuthenticated ? (
                <>
                  {isCitizen && (
                    <Link
                      to="/submit"
                      className="px-6 py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/25 transition-all flex items-center gap-2"
                    >
                      Report Civic Issue <ArrowRight className="w-4 h-4" />
                    </Link>
                  )}
                  {isOfficer && (
                    <Link
                      to="/officer/dashboard"
                      className="px-6 py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/25 transition-all flex items-center gap-2"
                    >
                      Open Officer Console <ArrowRight className="w-4 h-4" />
                    </Link>
                  )}
                  {isAdmin && (
                    <Link
                      to="/admin/dashboard"
                      className="px-6 py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/25 transition-all flex items-center gap-2"
                    >
                      Open Admin Dashboard <ArrowRight className="w-4 h-4" />
                    </Link>
                  )}
                </>
              ) : (
                <>
                  <Link
                    to="/submit"
                    className="px-6 py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/25 transition-all flex items-center gap-2"
                  >
                    Submit Complaint <ArrowRight className="w-4 h-4" />
                  </Link>
                  <Link
                    to="/login"
                    className="px-6 py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-xl border border-slate-700 transition-all"
                  >
                    Officer / Admin Login
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Multimodal Pillars */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            How The Multimodal AI Platform Works
          </h2>
          <p className="text-sm text-slate-500 mt-2">
            Eliminates slow manual triage by integrating vision, semantics, and context in real-time.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
              <Brain className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">1. NLP Semantic Engine</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Cleans noisy citizen text and categorizes into 10 civic domains (Road, Garbage, Water, Sewage, etc.) while preserving critical urgency triggers (e.g. "school", "hospital", "injury").
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4">
              <Eye className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">2. Computer Vision Inspection</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Detects road potholes using YOLO object detection, categorizes urban waste via PyTorch transfer learning, and calculates physical damage area coverage percentage.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">3. Priority & SLA Routing</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Fuses text severity, visual damage, and local danger into an objective 0–100 priority score, mapping to strict SLA enforcement (CRITICAL = 24h, HIGH = 48h).
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-8 text-center text-xs text-slate-500">
        <p>© 2026 Civic Complaint Prioritizer. Modular Multimodal AI Platform.</p>
      </footer>
    </div>
  );
};
