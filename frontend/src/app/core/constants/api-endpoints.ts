import { environment } from '../../../environments/environment';

export const ApiEndpoints = {
  general: {
    home: `${environment.apiUrl}/`,
    health: `${environment.apiUrl}/health`,
  },
  math: {
    divideByTwo: (number: number) => `${environment.apiUrl}/divideByTwo?number=${number}`,
  },
};
