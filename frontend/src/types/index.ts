export type UserRole = 'CITIZEN' | 'OFFICER' | 'ADMIN';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  created_at: string;
}

export type SeverityLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type ComplaintStatus = 'SUBMITTED' | 'IN_REVIEW' | 'ASSIGNED' | 'IN_PROGRESS' | 'RESOLVED' | 'REJECTED';

export interface DetectedObject {
  class: string;
  confidence: number;
  bbox?: number[];
  area_percentage?: number;
}

export interface AIAnalysis {
  id: number;
  complaint_id: string;
  text_category: string;
  text_confidence: number;
  text_severity: number;
  visual_category?: string;
  visual_confidence?: number;
  visual_severity?: number;
  detected_objects: DetectedObject[];
  damage_area_percentage?: number;
  duplicate_similarity?: number;
  multimodal_score: number;
  explanation: string;
  model_version: string;
  created_at: string;
}

export interface ComplaintHistory {
  id: number;
  complaint_id: string;
  old_status?: string;
  new_status: string;
  changed_by?: number;
  comment?: string;
  timestamp: string;
}

export interface Complaint {
  id: string;
  user_id: number;
  title: string;
  description: string;
  category: string;
  status: ComplaintStatus;
  severity: SeverityLevel;
  priority_score: number;
  department: string;
  sla_hours: number;
  latitude?: number;
  longitude?: number;
  address?: string;
  image_url?: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  sla_status?: 'ON_TRACK' | 'DUE_SOON' | 'OVERDUE';
  ai_analysis?: AIAnalysis;
  history?: ComplaintHistory[];
}

export interface ComplaintSubmissionResult {
  complaint_id: string;
  category: string;
  severity: SeverityLevel;
  priority_score: number;
  department: string;
  sla_hours: number;
  explanation: string;
  visual_category?: string;
  damage_area_percentage?: number;
  duplicate_warning?: any;
  complaint: Complaint;
}

export interface Department {
  id: number;
  name: string;
  category: string;
  sla_hours: number;
  officer_id?: number;
}

export interface AdminStats {
  total_complaints: number;
  critical_complaints: number;
  pending_complaints: number;
  resolved_complaints: number;
  sla_compliance_rate: number;
  avg_priority_score: number;
  by_category: { category: string; count: number; percentage: number }[];
  by_priority: { priority: string; count: number; color: string }[];
  by_department: { department: string; total: number; resolved: number; sla_compliance_rate: number }[];
  daily_trends: { date: string; count: number; critical_count: number }[];
  sla_violations: number;
}
