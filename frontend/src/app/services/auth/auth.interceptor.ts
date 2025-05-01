// auth.interceptor.ts
import { inject } from '@angular/core';
import {
  HttpRequest,
  HttpHandlerFn,
  HttpEvent,
  HttpInterceptorFn,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, switchMap, filter, take } from 'rxjs/operators';
import { AuthService } from './auth.service';

// Global variables for the refresh token mechanism
let isRefreshing = false;
const refreshTokenSubject = new BehaviorSubject<string | null>(null);

// Modern functional interceptor for Angular 14+
export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const authService = inject(AuthService);

  // Skip adding token for auth endpoints
  if (isAuthRequest(request)) {
    return next(request);
  }

  // Add auth token to request
  const token = authService.getAccessToken();
  if (token) {
    request = addToken(request, token);
  }

  // Handle the request and catch errors
  return next(request).pipe(
    catchError(error => {
      if (error instanceof HttpErrorResponse && error.status === 401) {
        return handle401Error(request, next, authService);
      }
      return throwError(() => error);
    })
  );
};

// Helper functions
function addToken(request: HttpRequest<any>, token: string): HttpRequest<any> {
  return request.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`
    }
  });
}

function isAuthRequest(request: HttpRequest<any>): boolean {
  return (
    request.url.includes('/auth/login') ||
    request.url.includes('/auth/refresh')
  );
}

function handle401Error(
  request: HttpRequest<any>,
  next: HttpHandlerFn,
  authService: AuthService
): Observable<HttpEvent<any>> {
  if (!isRefreshing) {
    isRefreshing = true;
    refreshTokenSubject.next(null);

    return authService.refreshAccessToken().pipe(
      switchMap(token => {
        isRefreshing = false;

        if (token) {
          refreshTokenSubject.next(token);
          return next(addToken(request, token));
        }

        // Token refresh failed, logout and redirect
        authService.logout();
        return throwError(() => new Error('Session expired'));
      }),
      catchError(err => {
        isRefreshing = false;
        authService.logout();
        return throwError(() => err);
      })
    );
  }

  // Wait for token to be refreshed
  return refreshTokenSubject.pipe(
    filter(token => token !== null),
    take(1),
    switchMap(token => {
      if (token) {
        return next(addToken(request, token));
      }
      return throwError(() => new Error('No token available'));
    })
  );
}
