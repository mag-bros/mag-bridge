import { Component, ElementRef, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { RestService } from '../../core/services/rest.service';

@Component({
  selector: 'app-form',
  imports: [MatFormFieldModule, MatInputModule, MatButtonModule],
  templateUrl: './form.html',
  styleUrl: './form.scss',
})
export class Form {
  constructor(private restService: RestService) {}

  @ViewChild('number', { read: ElementRef }) number!: ElementRef<HTMLElement>;

  submitButtonClicked() {
    const inputValue = (this.number.nativeElement as HTMLInputElement).value;
    const number = parseFloat(inputValue);

    if (isNaN(number)) {
      alert('Please enter a valid number');
      return;
    }

    this.restService.post(this.restService.endpoints.math.divideByTwo(number), {}).subscribe({
      next: (res) => console.log('Result:', res),
      error: (err) => console.error('Error:', err),
    });
  }
}
