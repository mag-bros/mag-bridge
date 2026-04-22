import { environment } from '../../../environments/environment';

export const ApiEndpoints = {
  general: {
    home: `${environment.apiUrl}/`,
    health: `${environment.apiUrl}/health`,
  },
  calculations: {
    submit: `${environment.apiUrl}/calculations/submit`,
  },
};
