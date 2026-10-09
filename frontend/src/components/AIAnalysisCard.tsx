import React from 'react';
import { AIAnalysis, Complaint } from '../types';
import { PriorityGauge } from './PriorityGauge';
import { SeverityBadge } from './StatusBadge';
import { Brain, Sparkles, AlertTriangle, Eye, FileText, Clock, Building2, ShieldAlert } from 'lucide-react';

interface AIAnalysisCardProps {
  complaint: Complaint;
}

export const AIAnalysisCard: React.FC<AIAnalysisCardProps> = ({ complaint }) => {
  const analysis = complaint.ai_analysis;

  if (!analysis) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6 text-center text-slate-500">
        <Brain className="w-10 h-10 mx-auto text-slate-400 mb-2" />
        <p className="font-medium">AI analysis pending or unavailable for this record.</p>
      </div>
    );
  }

  const detectedObjects = analysis.detected_objects || [];

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 px-6 py-5 text-white flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              Multimodal AI Evaluation
              <span className="text-xs font-normal text-blue-300 bg-blue-950/60 px-2 py-0.5 rounded-full border border-blue-800">
                {analysis.model_version}
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Co-analyzed text semantics, computer vision damage metrics, and local safety features.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <SeverityBadge severity={complaint.severity} size="lg" />
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Core Metric Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Priority Score Gauge */}
          <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 flex flex-col items-center justify-center text-center">
            <PriorityGauge score={complaint.priority_score} size={84} />
            <span className="text-xs text-slate-500 font-medium mt-1">Calculated Priority</span>
          </div>

          {/* Text Severity */}
          <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-600">
              <span className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-blue-500" />
                Text Severity
              </span>
              <span className="text-xs font-bold text-slate-700">
                {Math.round(analysis.text_severity)}/100
              </span>
            </div>
            <div className="my-2">
              <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-blue-600 h-full rounded-full transition-all"
                  style={{ width: `${Math.min(100, analysis.text_severity)}%` }}
                />
              </div>
            </div>
            <div className="text-xs text-slate-500 flex justify-between">
              <span>Category: <strong>{analysis.text_category}</strong></span>
              <span>Conf: <strong>{Math.round(analysis.text_confidence * 100)}%</strong></span>
            </div>
          </div>

          {/* Visual Severity */}
          <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-600">
              <span className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
                <Eye className="w-3.5 h-3.5 text-indigo-500" />
                Visual Severity
              </span>
              <span className="text-xs font-bold text-slate-700">
                {analysis.visual_severity !== null && analysis.visual_severity !== undefined
                  ? `${Math.round(analysis.visual_severity)}/100`
                  : 'N/A'}
              </span>
            </div>
            <div className="my-2">
              <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-indigo-600 h-full rounded-full transition-all"
                  style={{ width: `${Math.min(100, analysis.visual_severity || 0)}%` }}
                />
              </div>
            </div>
            <div className="text-xs text-slate-500 flex justify-between">
              <span>Coverage: <strong>{analysis.damage_area_percentage ? `${analysis.damage_area_percentage}%` : '0%'}</strong></span>
              <span>{analysis.visual_category || 'No visual model'}</span>
            </div>
          </div>

          {/* Suggested SLA */}
          <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-600">
              <span className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-amber-500" />
                Target SLA
              </span>
              <span className="text-xs font-bold text-amber-700 bg-amber-100/70 px-2 py-0.5 rounded">
                {complaint.sla_hours} Hours
              </span>
            </div>
            <div className="my-2 text-xs text-slate-600">
              Assigned: <strong>{complaint.department}</strong>
            </div>
            <div className="text-xs text-slate-500 flex items-center gap-1">
              <Building2 className="w-3.5 h-3.5 text-slate-400" />
              <span>Auto-routed to sector authority</span>
            </div>
          </div>
        </div>

        {/* Explainability Callout */}
        <div className="bg-blue-50/60 border border-blue-200/80 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <div className="p-1.5 bg-blue-100 rounded-lg text-blue-700 shrink-0 mt-0.5">
              <Brain className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-blue-900 mb-1">
                Transparent Model Decision Attribution
              </h4>
              <p className="text-sm text-blue-950 font-medium leading-relaxed">
                {analysis.explanation}
              </p>
            </div>
          </div>
        </div>

        {/* Vision Detections Details (if objects detected) */}
        {detectedObjects.length > 0 && (
          <div className="border border-slate-200/80 rounded-xl p-4 bg-slate-50/40">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-orange-500" />
              Detected Civic Damages ({detectedObjects.length})
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {detectedObjects.map((obj, i) => (
                <div key={i} className="bg-white border border-slate-200 rounded-lg p-3 text-xs flex justify-between items-center">
                  <div>
                    <span className="font-semibold text-slate-800 capitalize">{obj.class}</span>
                    <div className="text-slate-400 text-[11px]">
                      Confidence: {Math.round(obj.confidence * 100)}%
                    </div>
                  </div>
                  {obj.area_percentage && (
                    <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">
                      {obj.area_percentage}% Area
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Duplicate Similarity Alert */}
        {analysis.duplicate_similarity && analysis.duplicate_similarity > 0.75 && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 flex items-center gap-3 text-amber-800 text-xs">
            <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0" />
            <div>
              <span className="font-semibold">Semantic Clustered Duplicate: </span>
              This complaint shares a {Math.round(analysis.duplicate_similarity * 100)}% semantic similarity with previously registered reports in the vicinity.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
