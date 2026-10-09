import React, { useState, useEffect } from 'react';
import { Brain, Cpu, Eye, CheckCircle2, AlertCircle, BarChart3, Terminal } from 'lucide-react';

export const ModelStatsPage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2.5">
          <Cpu className="w-7 h-7 text-indigo-600" />
          ML Model Registry & Architecture
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Inspection console for NLP classifiers, Computer Vision detectors, and Multimodal Fusion pipelines.
        </p>
      </div>

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Text Model */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
                <Brain className="w-5 h-5" />
              </span>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">
                Active & Trained
              </span>
            </div>
            <h3 className="font-bold text-lg text-slate-900">NLP Category Classifier</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              TF-IDF (1-2 ngrams, 5000 features) + Balanced Logistic Regression classifier trained on 10 Civic Complaint categories.
            </p>
            <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1.5 text-slate-600 font-mono">
              <div className="flex justify-between">
                <span>Model:</span>
                <span className="font-semibold text-slate-900">TF-IDF + LogReg</span>
              </div>
              <div className="flex justify-between">
                <span>Classes:</span>
                <span className="font-semibold text-slate-900">10 Domains</span>
              </div>
              <div className="flex justify-between">
                <span>Artifact:</span>
                <span className="text-blue-600 truncate">baseline_tfidf.joblib</span>
              </div>
            </div>
          </div>
          <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-400">
            Retrain: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">python scripts/train_text.py</code>
          </div>
        </div>

        {/* Pothole Vision Model */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
                <Eye className="w-5 h-5" />
              </span>
              <span className="text-xs font-bold text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-full">
                Ultralytics YOLO
              </span>
            </div>
            <h3 className="font-bold text-lg text-slate-900">Pothole YOLO Detector</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              YOLOv8 object detector fine-tuned on the local Potholes dataset (819 images, 2,114 bounding box annotations).
            </p>
            <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1.5 text-slate-600 font-mono">
              <div className="flex justify-between">
                <span>Dataset:</span>
                <span className="font-semibold text-slate-900">potholes (COCO/YOLO)</span>
              </div>
              <div className="flex justify-between">
                <span>Target:</span>
                <span className="font-semibold text-slate-900">pothole [bbox, area %]</span>
              </div>
              <div className="flex justify-between">
                <span>Weights:</span>
                <span className="text-indigo-600 truncate">pothole_yolo.pt</span>
              </div>
            </div>
          </div>
          <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-400">
            Train: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">python scripts/train_detection.py</code>
          </div>
        </div>

        {/* Garbage Vision Model */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
                <BarChart3 className="w-5 h-5" />
              </span>
              <span className="text-xs font-bold text-purple-700 bg-purple-50 border border-purple-200 px-2.5 py-1 rounded-full">
                PyTorch ResNet-18
              </span>
            </div>
            <h3 className="font-bold text-lg text-slate-900">Urban Waste Classifier</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              PyTorch Transfer Learning classifier trained on the IndiUrbanClean dataset across 5 urban waste/cleanliness categories.
            </p>
            <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1.5 text-slate-600 font-mono">
              <div className="flex justify-between">
                <span>Dataset:</span>
                <span className="font-semibold text-slate-900">IndiUrbanClean (1,981 imgs)</span>
              </div>
              <div className="flex justify-between">
                <span>Classes:</span>
                <span className="font-semibold text-slate-900">5 Waste Classes</span>
              </div>
              <div className="flex justify-between">
                <span>Weights:</span>
                <span className="text-emerald-600 truncate">garbage_classifier.pth</span>
              </div>
            </div>
          </div>
          <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-400">
            Train: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">python scripts/train_classification.py</code>
          </div>
        </div>
      </div>

      {/* Terminal Commands Card */}
      <div className="bg-slate-900 text-slate-100 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-blue-400" />
          <h3 className="font-bold text-sm tracking-wide">Model Training & Inspection Commands</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-1">
            <span className="text-slate-400"># Audit raw local datasets</span>
            <div className="text-green-400 font-bold">python scripts/inspect_datasets.py</div>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-1">
            <span className="text-slate-400"># Prepare YOLO conversions</span>
            <div className="text-green-400 font-bold">python scripts/prepare_datasets.py</div>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-1">
            <span className="text-slate-400"># Train NLP Grievance Classifier</span>
            <div className="text-green-400 font-bold">python scripts/train_text.py</div>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-1">
            <span className="text-slate-400"># Run End-to-End System Evaluation</span>
            <div className="text-green-400 font-bold">python scripts/evaluate.py</div>
          </div>
        </div>
      </div>
    </div>
  );
};
