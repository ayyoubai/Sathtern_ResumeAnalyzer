import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ResumeAnalysisResponse } from '../models/resume-analysis.model';

@Injectable({
  providedIn: 'root'
})
export class ResumeService {

  private readonly http = inject(HttpClient);

  private readonly API_URL = 'http://localhost:8000/api';

  /**
   * Uploads a PDF resume to the backend.
   * Returns a resume_id to be used for analysis.
   */
  uploadResume(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post(
      `${this.API_URL}/resume/upload`,
      formData
    );
  }

  /**
   * Analyzes a previously uploaded resume against a target job position.
   */
  analyzeResume(
    resumeId: string,
    targetRole?: string
  ): Observable<ResumeAnalysisResponse> {

    const body = targetRole
      ? { target_role: targetRole }
      : {};

    return this.http.post<ResumeAnalysisResponse>(
      `${this.API_URL}/resume/analyze/${resumeId}`,
      body
    );
  }
}
