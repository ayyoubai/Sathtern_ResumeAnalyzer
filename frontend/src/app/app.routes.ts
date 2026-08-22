import { Routes } from '@angular/router';
import { ResumeUploadComponent } from './features/resume-upload/resume-upload.component';
import { ResumeAnalysisComponent } from './features/resume-analysis/resume-analysis.component';

export const routes: Routes = [
  {
    path: 'upload',
    component: ResumeUploadComponent
  },
  {
    path: 'analysis',
    component: ResumeAnalysisComponent
  },
  {
    path: '',
    redirectTo: 'upload',
    pathMatch: 'full'
  }
];
