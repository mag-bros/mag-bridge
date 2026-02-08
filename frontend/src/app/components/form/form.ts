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
  response: string | undefined;

  @ViewChild('number', { read: ElementRef }) number!: ElementRef<HTMLElement>;

  pickFile() {
    window.electronAPI.selectFile().then((path: string | null) => {
      if (!path) {
        this.response = 'File selection cancelled';
        return;
      }

      const allowedExtension = '.sdf';
      if (!path.toLowerCase().endsWith(allowedExtension)) {
        this.response = 'Only SDF files are allowed';
        return;
      }

      this.restService.post(this.restService.endpoints.files.upload, { path }).subscribe({
        next: (res: any) => {
          this.response = `Uploaded: ${res.filename}`;
        },
        error: (err) => {
          this.response = 'Upload failed';
          console.error(err);
        },
      });
    });
  }
}
