import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ResumeService } from '../../core/services/resume.service';
import { ResumeAnalysisResponse } from '../../core/models/resume-analysis.model';

@Component({
  selector: 'app-resume-upload',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './resume-upload.component.html',
  styleUrl: './resume-upload.component.scss'
})
export class ResumeUploadComponent {

  private readonly resumeService = inject(ResumeService);

  selectedFile: File | null = null;

  uploading = false;
  analyzing = false;

  analysis: ResumeAnalysisResponse | null = null;

  error: string | null = null;

  targetRole = 'Full Stack Developer';

  isDragging = false;

  readonly roles = [
    'Full Stack Developer',
    'Frontend Developer',
    'Backend Developer',
    'Software Engineer',
    'DevOps Engineer',
    'Data Analyst',
    'Data Scientist',
    'AI Engineer',
    'Machine Learning Engineer',
    'Cybersecurity Engineer'
  ];

  // =====================================================
  // FILE SELECTION
  // =====================================================

  onFileSelected(event: Event): void {

    const input = event.target as HTMLInputElement;

    if (!input.files || input.files.length === 0) {
      return;
    }

    this.handleFile(input.files[0]);
  }

  // =====================================================
  // FILE HANDLING
  // =====================================================

  private handleFile(file: File): void {

    if (
      file.type !== 'application/pdf' &&
      !file.name.toLowerCase().endsWith('.pdf')
    ) {

      this.error = 'Please select a PDF file.';
      this.selectedFile = null;

      return;
    }

    this.selectedFile = file;
    this.error = null;
    this.analysis = null;
  }

  // =====================================================
  // DRAG & DROP
  // =====================================================

  onDragOver(event: DragEvent): void {

    event.preventDefault();

    this.isDragging = true;
  }

  onDragLeave(event: DragEvent): void {

    event.preventDefault();

    this.isDragging = false;
  }

  onDrop(event: DragEvent): void {

    event.preventDefault();

    this.isDragging = false;

    const files = event.dataTransfer?.files;

    if (!files || files.length === 0) {
      return;
    }

    this.handleFile(files[0]);
  }

  // =====================================================
  // REMOVE FILE
  // =====================================================

  removeFile(): void {

    this.selectedFile = null;
    this.error = null;
    this.analysis = null;
  }

  // =====================================================
  // ANALYZE
  // =====================================================

  uploadAndAnalyze(): void {

    if (!this.selectedFile) {

      this.error = 'Please select your resume first.';

      return;
    }

    if (!this.targetRole) {

      this.error = 'Please select a target position.';

      return;
    }

    this.uploading = true;
    this.analyzing = false;
    this.error = null;
    this.analysis = null;

    this.resumeService
      .uploadResume(this.selectedFile)
      .subscribe({

        next: (uploadResponse) => {

          const resumeId = uploadResponse?.resume_id;

          if (!resumeId) {

            this.uploading = false;

            this.error =
              'The server did not return a resume ID.';

            return;
          }

          this.uploading = false;
          this.analyzing = true;

          this.resumeService
            .analyzeResume(
              resumeId,
              this.targetRole
            )
            .subscribe({

              next: (response) => {

                this.analysis = response;

                this.analyzing = false;

                setTimeout(() => {
                  document
                    .getElementById('analysis-result')
                    ?.scrollIntoView({
                      behavior: 'smooth',
                      block: 'start'
                    });
                }, 100);
              },

              error: (err) => {

                console.error(
                  'ANALYSIS ERROR:',
                  err
                );

                this.analyzing = false;

                this.error =
                  'The resume was uploaded, but the analysis failed.';
              }

            });
        },

        error: (err) => {

          console.error(
            'UPLOAD ERROR:',
            err
          );

          this.uploading = false;
          this.analyzing = false;

          this.error =
            'Unable to upload the resume.';
        }

      });
  }

  // =====================================================
  // NEW ANALYSIS
  // =====================================================

  newAnalysis(): void {

    this.selectedFile = null;
    this.analysis = null;
    this.error = null;
    this.uploading = false;
    this.analyzing = false;

    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }

  // =====================================================
  // SCORE LABEL
  // =====================================================

  get scoreLabel(): string {

    const score =
      this.analysis?.analysis.match_score ?? 0;

    if (score >= 80) {
      return 'Excellent match';
    }

    if (score >= 60) {
      return 'Good match';
    }

    if (score >= 40) {
      return 'Moderate match';
    }

    return 'Needs improvement';
  }

  // =====================================================
  // SCORE CLASS
  // =====================================================

  get scoreClass(): string {

    const score =
      this.analysis?.analysis.match_score ?? 0;

    if (score >= 80) {
      return 'excellent';
    }

    if (score >= 60) {
      return 'good';
    }

    if (score >= 40) {
      return 'moderate';
    }

    return 'low';
  }

  // =====================================================
  // SKILL WIDTH
  // =====================================================

  getSkillWidth(status: string): number {

    switch (status) {

      case 'strong':
        return 100;

      case 'partial':
        return 55;

      default:
        return 0;
    }
  }
}
