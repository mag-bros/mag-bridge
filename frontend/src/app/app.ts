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
  constructor(private restService: RestService) {}
  isLoading = true;
  response: string | undefined;
  backendCheckSubscription!: Subscription;

  ngOnInit() {
    this.backendReadyCheck();
  }

  backendReadyCheck() {
    this.backendCheckSubscription = interval(500).subscribe(() => {
      this.restService.get<any>(this.restService.endpoints.general.health).subscribe({
        next: (res) => {
          console.log('Backend health OK:', res);
          this.isLoading = false;
          this.backendCheckSubscription.unsubscribe();
        },
        error: (err) => {
          console.error('Backend not yet ready (healthcheck failed):', err);
        },
      });
    });
  }
}
