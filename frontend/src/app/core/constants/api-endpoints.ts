import { environment } from '../../../environments/environment';

export const ApiEndpoints = {
  general: {
    home: `${environment.apiUrl}/`,
    health: `${environment.apiUrl}/health`,
  },
  files: {
    upload: `${environment.apiUrl}/files/upload`,
  },
};
