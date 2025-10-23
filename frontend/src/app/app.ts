import { Component } from '@angular/core';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonModule } from '@angular/material/button';
import { Form } from './form/form/form';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MatSlideToggleModule, MatButtonModule, Form],
  templateUrl: './app.html',
})
export class AppComponent {}
