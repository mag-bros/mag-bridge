import { Component } from '@angular/core';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MatSlideToggleModule, MatButtonModule],
  templateUrl: './app.html',
})
export class AppComponent {}
