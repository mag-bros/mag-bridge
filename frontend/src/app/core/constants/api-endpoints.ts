import { environment } from '../../../environments/environment';

export const ApiEndpoints = {
  general: {
    home: `${environment.apiUrl}/`,
  },
  math: {
    divideByTwo: (number: number) => `${environment.apiUrl}/divideByTwo?number=${number}`,
  },
};
