// app.routes.ts
import { Routes } from '@angular/router';
import { AuthGuard } from './services/auth/auth.guard';
import {LoginComponent} from './components/login/login.component';
import {DashboardComponent} from './components/dashboard/dashboard.component';
import {RegisterComponent} from './components/register/register.component';
import {ForgotPasswordComponent} from './components/forgot-password/forgot-password.component';

export const routes: Routes = [
  // Public routes
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: 'register',
    component: RegisterComponent
  },
  {
    path: 'forgot-password',
    component: ForgotPasswordComponent
  },

  // Protected route with actual dashboard component
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [AuthGuard]
  },

  // Wildcard route for 404
  {
    path: '**',
    redirectTo: 'login'
  }
];
