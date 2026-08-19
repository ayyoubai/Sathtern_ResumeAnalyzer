import { Routes } from '@angular/router';
import { ResumeUploadComponent } from './features/resume-upload/resume-upload.component';

export const routes: Routes = [
  {
    path: 'upload',
    component: ResumeUploadComponent
  },
  {
    path: '',
    redirectTo: 'upload',
    pathMatch: 'full'
  }
];
