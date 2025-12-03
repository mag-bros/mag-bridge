import { Component } from '@angular/core';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonModule } from '@angular/material/button';
import { Form } from './components/form/form';
import { SplashScreen } from './components/splash-screen/splash-screen';
import { RestService } from './core/services/rest.service';
import { interval, Subscription } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MatSlideToggleModule, MatButtonModule, Form, SplashScreen],
  templateUrl: './app.html',
})
export class AppComponent {

  isLoading = true;
  private backendCheckSubscription!: Subscription;

  constructor(private restService: RestService) { }

  ngOnInit() {
    this.startBackendHealthCheck();
  }

  // ===========================================================================
  //  Backend Health Check
  // ===========================================================================

  private startBackendHealthCheck() {
    const startTime = performance.now();
    const startIso = new Date().toISOString();

    window.stdout?.log('Starting backend health check at', startIso);

    this.backendCheckSubscription = interval(500).subscribe(() => {
      this.checkBackendHealth(startTime);
    });
  }

  private checkBackendHealth(startTime: number) {
    const health$ = this.restService.get<any>(
      this.restService.endpoints.general.health
    );

    health$.subscribe({
      next: (res) => this.handleBackendReady(res, startTime),
      error: (err) => this.handleBackendNotReady(err),
    });
  }

  private handleBackendReady(res: any, startTime: number) {
    // ECONNREFUSED from main.js is mapped to `null`
    if (res == null) {
      window.stdout?.error('Backend not yet ready (connection refused)');
      return;
    }

    const seconds = ((performance.now() - startTime) / 1000).toFixed(2);

    window.stdout?.log('Backend health OK:', res, `ready after ${seconds}s`);

    this.isLoading = false;
    this.backendCheckSubscription.unsubscribe();
  }

  private handleBackendNotReady(err: any) {
    // This is for real errors, not "backend not listening yet"
    window.stdout?.error('Backend healthcheck error:', err);
  }
}
