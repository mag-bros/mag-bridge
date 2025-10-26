import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, from } from 'rxjs';
import { ApiEndpoints } from '../constants/api-endpoints';

@Injectable({
  providedIn: 'root',
})
export class RestService {
  public endpoints = ApiEndpoints;

  constructor(private http: HttpClient) {}

  private isElectron(): boolean {
    return !!(window as any).electronAPI;
  }

  get<T>(url: string): Observable<T> {
    if (this.isElectron()) {
      return from((window as any).electronAPI.apiRequest(url, 'GET')) as Observable<T>;
    }
    return this.http.get<T>(url);
  }

  post<T>(url: string, data: any): Observable<T> {
    if (this.isElectron()) {
      return from((window as any).electronAPI.apiRequest(url, 'POST', data)) as Observable<T>;
    }
    return this.http.post<T>(url, data);
  }

  put<T>(url: string, data: any): Observable<T> {
    if (this.isElectron()) {
      return from((window as any).electronAPI.apiRequest(url, 'PUT', data)) as Observable<T>;
    }
    return this.http.put<T>(url, data);
  }

  delete<T>(url: string): Observable<T> {
    if (this.isElectron()) {
      return from((window as any).electronAPI.apiRequest(url, 'DELETE')) as Observable<T>;
    }
    return this.http.delete<T>(url);
  }
}
