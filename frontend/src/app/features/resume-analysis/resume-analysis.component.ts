import { Component, OnInit, OnDestroy, HostListener, inject } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

import { ResumeAnalysisStateService } from '../../core/services/resume.analysis.state.service'
import { ResumeAnalysisResponse } from '../../core/models/resume-analysis.model';

@Component({
  selector: 'app-resume-analysis',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './resume-analysis.component.html',
  styleUrl: './resume-analysis.component.scss'
})
export class ResumeAnalysisComponent implements OnInit, OnDestroy {

  private readonly resumeState = inject(ResumeAnalysisStateService);
  private readonly router = inject(Router);

  fileName: string | null = null;
  analysis: ResumeAnalysisResponse | null = null;

  scrollProgress = 0;
  showBackToTop = false;
  animatedScore = 0;

  private observer: IntersectionObserver | null = null;
  private scoreInterval: any;

  // ============================================================
  // LIFECYCLE
  // ============================================================

  ngOnInit(): void {
    // Pas de résultat en mémoire (arrivée directe sur /analysis) -> retour à l'upload
    if (!this.resumeState.analysis) {
      this.router.navigate(['/upload']);
      return;
    }

    this.fileName = this.resumeState.fileName;
    this.analysis = this.resumeState.analysis;

    this.initScrollReveal();
    this.animateScore(this.analysis.analysis.match_score);

    setTimeout(() => {
      document.getElementById('analysis-result')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }, 100);
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
    clearInterval(this.scoreInterval);
  }

  // ============================================================
  // SCROLL HANDLING
  // ============================================================

  @HostListener('window:scroll')
  onWindowScroll(): void {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    this.scrollProgress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    this.showBackToTop = scrollTop > 400;
  }

  scrollToTop(): void {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // ============================================================
  // SCROLL REVEAL (IntersectionObserver)
  // ============================================================

  private initScrollReveal(): void {
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            this.observer?.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
    );

    setTimeout(() => {
      document.querySelectorAll('.reveal').forEach((el) => {
        this.observer?.observe(el);
      });
    }, 100);
  }

  // ============================================================
  // SCORE COUNTER ANIMATION
  // ============================================================

  private animateScore(target: number): void {
    clearInterval(this.scoreInterval);
    this.animatedScore = 0;
    const duration = 1200;
    const steps = 60;
    const increment = target / steps;
    let current = 0;

    this.scoreInterval = setInterval(() => {
      current += increment;
      if (current >= target) {
        this.animatedScore = target;
        clearInterval(this.scoreInterval);
      } else {
        this.animatedScore = Math.round(current);
      }
    }, duration / steps);
  }

  // ============================================================
  // NEW ANALYSIS -> retour vers la page upload
  // ============================================================

  newAnalysis(): void {
    this.resumeState.clear();
    this.router.navigate(['/upload']);
  }

  // ============================================================
  // SCORE LABEL / CLASS
  // ============================================================

  get scoreLabel(): string {
    const score = this.analysis?.analysis.match_score ?? 0;
    if (score >= 80) return 'Excellent match';
    if (score >= 60) return 'Good match';
    if (score >= 40) return 'Moderate match';
    return 'Needs improvement';
  }

  get scoreClass(): string {
    const score = this.analysis?.analysis.match_score ?? 0;
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'moderate';
    return 'low';
  }

  getSkillWidth(status: string): number {
    switch (status) {
      case 'strong': return 100;
      case 'partial': return 55;
      default: return 0;
    }
  }
}
