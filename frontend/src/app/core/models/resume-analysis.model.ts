export interface SkillMatch {
  skill: string;
  status: 'strong' | 'partial' | 'missing';
}

export interface ResumeAnalysis {
  target_role: string;
  role_confidence: number;
  match_score: number;
  strengths: string[];
  missing_skills: string[];
  skills_match: SkillMatch[];
  recommendations: string[];
  cv_improvements: string[];
}

export interface ResumeAnalysisResponse {
  resume_id: string;
  analysis: ResumeAnalysis;
}
