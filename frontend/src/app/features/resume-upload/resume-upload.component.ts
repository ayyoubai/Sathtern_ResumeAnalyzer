import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { ResumeService } from '../../core/services/resume.service';
import { ResumeAnalysisStateService } from '../../core/services/resume.analysis.state.service'

@Component({
  selector: 'app-resume-upload',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './resume-upload.component.html',
  styleUrl: './resume-upload.component.scss'
})
export class ResumeUploadComponent {

  private readonly resumeService = inject(ResumeService);
  private readonly resumeState = inject(ResumeAnalysisStateService);
  private readonly router = inject(Router);

  selectedFile: File | null = null;
  uploading = false;
  analyzing = false;
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

  // ============================================================
  // FILE SELECTION
  // ============================================================

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;
    this.handleFile(input.files[0]);
  }

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
  }

  // ============================================================
  // DRAG & DROP
  // ============================================================

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
    if (!files || files.length === 0) return;
    this.handleFile(files[0]);
  }

  // ============================================================
  // REMOVE FILE
  // ============================================================

  removeFile(): void {
    this.selectedFile = null;
    this.error = null;
  }

  // ============================================================
  // UPLOAD + ANALYZE, PUIS NAVIGATION VERS LA PAGE RESULTATS
  // ============================================================

  uploadAndAnalyze(): void {
    if (!this.selectedFile) {
      this.error = 'Please select your resume first.';
      return;
    }
    if (!this.targetRole) {
      this.error = 'Please select a target position.';
      return;
    }

    const fileName = this.selectedFile.name;

    this.uploading = true;
    this.analyzing = false;
    this.error = null;

    this.resumeService.uploadResume(this.selectedFile).subscribe({
      next: (uploadResponse) => {
        const resumeId = uploadResponse?.resume_id;
        if (!resumeId) {
          this.uploading = false;
          this.error = 'The server did not return a resume ID.';
          return;
        }

        this.uploading = false;
        this.analyzing = true;

        this.resumeService.analyzeResume(resumeId, this.targetRole).subscribe({
          next: (response) => {
            this.analyzing = false;
            this.resumeState.setResult(fileName, response);
            this.router.navigate(['/analysis']);
          },
          error: (err) => {
            console.error('ANALYSIS ERROR:', err);
            this.analyzing = false;
            this.error = 'The resume was uploaded, but the analysis failed.';
          }
        });
      },
      error: (err) => {
        console.error('UPLOAD ERROR:', err);
        this.uploading = false;
        this.analyzing = false;
        this.error = 'Unable to upload the resume.';
      }
    });
  }
}
