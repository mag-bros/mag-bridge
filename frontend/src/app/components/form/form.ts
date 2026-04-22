import { Component, ElementRef, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule } from '@angular/material/core';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatRadioModule } from '@angular/material/radio';
import { FormsModule } from '@angular/forms';
import { RestService } from '../../core/services/rest.service';

@Component({
  selector: 'app-form',
  imports: [
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatOptionModule,
    MatCheckboxModule,
    MatRadioModule,
    FormsModule,
  ],
  templateUrl: './form.html',
  styleUrl: './form.scss',
})
export class Form {
  constructor(private restService: RestService) {}
  response: string | undefined;

  @ViewChild('number', { read: ElementRef }) number!: ElementRef<HTMLElement>;

  inputTypes = [
    { label: 'SDF file', value: 'sdf' },
    { label: 'Chemical formula or SMILES', value: 'smiles_formula' },
    { label: 'User already has Diamagnetic Susceptibility', value: 'susceptibility' },
  ];

  calculationOptions = [
    { label: 'χD Calculation', value: 'xd' },
    { label: 'DC Magnetic Data', value: 'dc' },
    { label: 'AC Magnetic Data', value: 'ac' },
  ];

  selectedInputType: string = 'sdf';
  selectedFile: string | null = null;
  formulaOrSmiles: string = '';
  susceptibility: number | null = null;
  selectedCalculations: string[] = [];

  toggleCalculation(option: string) {
    const index = this.selectedCalculations.indexOf(option);
    if (index === -1) {
      this.selectedCalculations.push(option);
    } else {
      this.selectedCalculations.splice(index, 1);
    }
  }

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
      this.selectedFile = path;
      this.response = `Selected: ${path}`;
    });
  }

  submit() {
    const requestData: any = {
      input_type: this.selectedInputType,
      selections: this.selectedCalculations.length > 0 ? this.selectedCalculations : undefined,
    };

    if (this.selectedInputType === 'sdf') {
      if (!this.selectedFile) {
        this.response = 'Please select an SDF file';
        return;
      }
      requestData.path = this.selectedFile;
    } else if (this.selectedInputType === 'smiles_formula') {
      if (!this.formulaOrSmiles) {
        this.response = 'Please enter SMILES or Formula';
        return;
      }
      requestData.smiles_formula = this.formulaOrSmiles;
    } else if (this.selectedInputType === 'susceptibility') {
      if (this.susceptibility === null) {
        this.response = 'Please enter susceptibility value';
        return;
      }
      requestData.susceptibility = this.susceptibility;
    }

    this.restService.post(this.restService.endpoints.calculations.submit, requestData).subscribe({
      next: (res: any) => {
        this.response = `Success: ${res.filename || 'Processed'}`;
      },
      error: (err) => {
        this.response = 'Operation failed';
        console.error(err);
      },
    });
  }
}
