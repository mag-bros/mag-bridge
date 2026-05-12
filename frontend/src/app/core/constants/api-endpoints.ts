import { environment } from '../../../environments/environment';

export const ApiEndpoints = {
  general: {
    home: `${environment.apiUrl}/`,
    health: `${environment.apiUrl}/health`,
  },
  experiments: `${environment.apiUrl}/experiments/`,
};
