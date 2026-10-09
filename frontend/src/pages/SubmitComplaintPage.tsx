import React, { useState, useRef } from 'react';
import { api } from '../services/api';
import { AIAnalysisCard } from '../components/AIAnalysisCard';
import { Complaint, ComplaintSubmissionResult } from '../types';
import { UploadCloud, MapPin, Sparkles, CheckCircle2, AlertCircle, FileText, Image as ImageIcon, Crosshair, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const CIVIC_CATEGORIES = [
    "Road Damage",
    "Garbage",
    "Water Supply",
    "Sewage",
    "Drainage",
    "Streetlight",
    "Electricity",
    "Public Safety",
    "Traffic",
    "Other"
];

export const SubmitComplaintPage: React.FC = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [latitude, setLatitude] = useState<string>('12.9716');
  const [longitude, setLongitude] = useState<string>('77.5946');
  const [address, setAddress] = useState('');
  
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submissionResult, setSubmissionResult] = useState<ComplaintSubmissionResult | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
        setError('Please upload a valid JPG or PNG image.');
        return;
      }
      if (file.size > 15 * 1024 * 1024) {
        setError('Image file size must be less than 15MB.');
        return;
      }
      setError(null);
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleUseCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLatitude(pos.coords.latitude.toFixed(6));
          setLongitude(pos.coords.longitude.toFixed(6));
          setAddress(prev => prev || `Lat: ${pos.coords.latitude.toFixed(4)}, Long: ${pos.coords.longitude.toFixed(4)}`);
        },
        (err) => {
          setError(`Could not fetch geolocation: ${err.message}. Using default coordinates.`);
        }
      );
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      if (category) formData.append('category', category);
      if (latitude) formData.append('latitude', latitude);
      if (longitude) formData.append('longitude', longitude);
      if (address) formData.append('address', address);
      if (imageFile) formData.append('image', imageFile);

      const result: ComplaintSubmissionResult = await api.createComplaint(formData);
      setSubmissionResult(result);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit complaint. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Title */}
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-3">
          <span>Report a Civic Grievance</span>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-100 text-blue-700 flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5" /> Multimodal AI Enabled
          </span>
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Submit complaint description and photo. Our computer vision and NLP models will analyze the severity and route it immediately.
        </p>
      </div>

      {/* Success AI Result Card */}
      {submissionResult && (
        <div className="mb-10 space-y-6 animate-fadeIn">
          <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-emerald-500 text-white rounded-2xl flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-7 h-7" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-800">Registration Success</span>
                  <span className="font-mono text-sm font-bold bg-emerald-200/60 text-emerald-950 px-2 py-0.5 rounded">
                    {submissionResult.complaint_id}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-emerald-950 mt-0.5">
                  Assigned to {submissionResult.department} (SLA: {submissionResult.sla_hours}h)
                </h3>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  setSubmissionResult(null);
                  setTitle('');
                  setDescription('');
                  setImageFile(null);
                  setImagePreview(null);
                }}
                className="px-4 py-2 text-xs font-semibold bg-white border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 transition"
              >
                Submit Another
              </button>
              <Link
                to={`/complaints/${submissionResult.complaint_id}`}
                className="px-4 py-2 text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-sm transition flex items-center gap-1.5"
              >
                Track Live Status <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* AI Multimodal Analysis Card */}
          <AIAnalysisCard complaint={submissionResult.complaint} />
        </div>
      )}

      {/* Form Grid */}
      <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Complaint Details */}
        <div className="lg:col-span-2 space-y-6 bg-white p-6 sm:p-8 rounded-2xl border border-slate-200/80 shadow-sm">
          {error && (
            <div className="p-3.5 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Complaint Title *
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Deep crater pothole near Hospital gate"
              className="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                Grievance Description *
              </label>
              <span className="text-[11px] text-slate-400">
                Mention key hazards (school, hospital, accidents, depth)
              </span>
            </div>
            <textarea
              required
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the issue in detail. What is the impact? Are there ongoing hazards or risks to pedestrians/vehicles?"
              className="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition leading-relaxed"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Category (Optional - AI will classify)
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              >
                <option value="">Auto-Detect via NLP</option>
                {CIVIC_CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Address / Landmark
              </label>
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="e.g. Main Market Rd, Ward 14"
                className="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              />
            </div>
          </div>

          {/* Location Coordinates */}
          <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-blue-600" /> Geographic GPS Coordinates
              </span>
              <button
                type="button"
                onClick={handleUseCurrentLocation}
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                <Crosshair className="w-3.5 h-3.5" /> Detect Current GPS
              </button>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] text-slate-500 mb-1">Latitude</label>
                <input
                  type="text"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  placeholder="12.9716"
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs font-mono outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-500 mb-1">Longitude</label>
                <input
                  type="text"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  placeholder="77.5946"
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs font-mono outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Image Upload & Visual Analysis */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
              <ImageIcon className="w-4 h-4 text-blue-600" />
              Evidence Image Upload
            </label>

            {/* Dropzone */}
            <div
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
                imagePreview
                  ? 'border-blue-400 bg-blue-50/10'
                  : 'border-slate-300 hover:border-blue-500 hover:bg-slate-50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".jpg,.jpeg,.png"
                onChange={handleFileChange}
                className="hidden"
              />

              {imagePreview ? (
                <div className="space-y-3">
                  <img
                    src={imagePreview}
                    alt="Complaint Preview"
                    className="max-h-48 mx-auto rounded-xl object-cover shadow-sm border border-slate-200"
                  />
                  <p className="text-xs text-blue-600 font-semibold">
                    Click to change uploaded image
                  </p>
                </div>
              ) : (
                <div className="space-y-2 py-4">
                  <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 mx-auto flex items-center justify-center">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <div className="text-xs font-semibold text-slate-700">
                    Click or drag image here
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Supports JPG, JPEG, PNG (up to 15MB)
                  </p>
                </div>
              )}
            </div>

            <p className="text-[11px] text-slate-400 leading-relaxed">
              * The uploaded photo will be processed by our object detection model to detect damage extent and compute visual severity.
            </p>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-sm transition shadow-md shadow-blue-500/20 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Analyzing Multimodal Features...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Submit & Analyze Grievance
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
