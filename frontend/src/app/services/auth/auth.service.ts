// auth.service.ts
import {Injectable, signal, inject, computed} from '@angular/core';
import {environment} from '../../../environments/environment';
import {BehaviorSubject, catchError, map, Observable, of, switchMap, tap, throwError, timer} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {Router} from '@angular/router';
import {jwtDecode} from 'jwt-decode';

export interface AuthData {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: {
    id: string;
    username: string;
    email: string;
    roles: string[];
  }
}

export interface TokenPayload {
  sub: string; // user id
  username: string;
  roles: string[];
  exp: number;
  iat: number;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient)
  private router = inject(Router)

  // Token management
  private accessToken = signal<string | null>(this.getStoredAccessToken());
  private refreshToken = signal<string | null>(this.getStoredRefreshToken());

  // User state
  private userSignal = signal<{ id: string; username: string; email: string; roles: string[] } | null>(null);

  public isLoggedIn = computed(() => !!this.accessToken());
  public username = computed(() => this.userSignal()?.username || '');
  public userRoles = computed(() => this.userSignal()?.roles || []);

  // Refresh token subject and timer
  private refreshTokenInProgress = false;
  private refreshTokenSubject = new BehaviorSubject<string | null>(null);

  constructor() {
    // Initialize user from stored token if available
    this.initUserFromToken();

    // Set up a token refresh mechanism
    this.setupTokenRefresh();
  }

  login(authData: AuthData): Observable<boolean> {
    return this.http.post<AuthResponse>(`${environment.apiUrl}/auth/login`, authData)
      .pipe(
        tap(response => this.handleAuthResponse(response)),
        map(() => true),
        catchError(error => {
          console.error('Login failed', error);
          return throwError(() => error);
        })
      );
  }

  logout(): void {
    // Clear stored tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // Reset state
    this.accessToken.set(null);
    this.refreshToken.set(null);
    this.userSignal.set(null);

    // Navigate to a login page
    this.router.navigate(['/login']);
  }

  getAccessToken(): string | null {
    return this.accessToken();
  }

  // Check if user has required a role
  hasRole(role: string): boolean {
    return this.userRoles().includes(role);
  }

  // Token refresh mechanism
  refreshAccessToken(): Observable<string | null> {
    if (this.refreshTokenInProgress) {
      return this.refreshTokenSubject.asObservable();
    }

    this.refreshTokenInProgress = true;
    this.refreshTokenSubject.next(null);

    const storedRefreshToken = this.refreshToken();

    if (!storedRefreshToken) {
      this.logout();
      return of(null);
    }

    return this.http.post<AuthResponse>(
      `${environment.apiUrl}/auth/refresh`,
      { refresh_token: storedRefreshToken }
    ).pipe(
      tap(response => this.handleAuthResponse(response)),
      map(() => this.accessToken()),
      catchError(error => {
        console.error('Token refresh failed', error);
        this.logout();
        return of(null);
      }),
      tap(() => {
        this.refreshTokenInProgress = false;
        this.refreshTokenSubject.next(this.accessToken());
      })
    );
  }

  // Private helper methods
  private handleAuthResponse(response: AuthResponse): void {
    // Store tokens
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);

    // Update signals
    this.accessToken.set(response.access_token);
    this.refreshToken.set(response.refresh_token);
    this.userSignal.set(response.user);
  }

  private getStoredAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getStoredRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private initUserFromToken(): void {
    const token = this.accessToken();
    if (token) {
      try {
        const payload = jwtDecode<TokenPayload>(token);
        const isTokenExpired = Date.now() >= payload.exp * 1000;

        if (isTokenExpired) {
          // Token expired, try refreshing or logout
          this.refreshAccessToken().subscribe();
        } else {
          // Set user from token if available, or fetch user info
          this.fetchUserInfo().subscribe();
        }
      } catch (error) {
        console.error('Invalid token', error);
        this.logout();
      }
    }
  }

  private fetchUserInfo(): Observable<any> {
    return this.http.get<{ id: string; username: string; email: string; roles: string[] }>(
      `${environment.apiUrl}/auth/me`
    ).pipe(
      tap(user => this.userSignal.set(user)),
      catchError(error => {
        console.error('Failed to fetch user info', error);
        return throwError(() => error);
      })
    );
  }

  private setupTokenRefresh(): void {
    const token = this.accessToken();
    if (token) {
      try {
        const payload = jwtDecode<TokenPayload>(token);
        const expiresIn = payload.exp * 1000 - Date.now();

        // Refresh token 1 minute before expiration
        const refreshTime = Math.max(0, expiresIn - 60000);

        // Set up a timer for token refresh
        timer(refreshTime).pipe(
          switchMap(() => this.refreshAccessToken())
        ).subscribe();
      } catch (error) {
        console.error('Invalid token for refresh setup', error);
      }
    }
  }
}
