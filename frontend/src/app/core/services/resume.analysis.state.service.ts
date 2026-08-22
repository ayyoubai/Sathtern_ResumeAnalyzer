import { Injectable } from '@angular/core';
import { ResumeAnalysisResponse } from '../models/resume-analysis.model';

// Etat en mémoire partagé entre ResumeUploadComponent et ResumeAnalysisComponent.
// Comme ce sont deux routes différentes, on ne peut plus se passer les données
// par binding : ce service fait le pont (providedIn: 'root' => singleton appli).
@Injectable({ providedIn: 'root' })
export class ResumeAnalysisStateService {
  fileName: string | null = null;
  analysis: ResumeAnalysisResponse | null = null;

  setResult(fileName: string, analysis: ResumeAnalysisResponse): void {
    this.fileName = fileName;
    this.analysis = analysis;
  }

  clear(): void {
    this.fileName = null;
    this.analysis = null;
  }
}
