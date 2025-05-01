// forgot-password.component.ts
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import {Router, RouterLink} from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink
  ],
  templateUrl: './forgot-password.component.html',
  styleUrl: './forgot-password.component.css'
})
export class ForgotPasswordComponent {
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private http = inject(HttpClient);

  loading = false;
  submitted = false;
  success = false;
  error = '';

  resetForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]]
  });

  // Getter for easy access to form fields
  get f() { return this.resetForm.controls; }

  onSubmit() {
    this.submitted = true;

    // Stop here if form is invalid
    if (this.resetForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = '';

    // API call to request password reset
    this.http.post(`${environment.apiUrl}/auth/forgot-password`, {
      email: this.resetForm.value.email
    }).pipe(
      finalize(() => {
        this.loading = false;
      })
    ).subscribe({
      next: () => {
        this.success = true;
      },
      error: (err) => {
        this.error = err.error?.message || 'An error occurred. Please try again later.';
      }
    });
  }

  // Navigate back to login page
  backToLogin() {
    this.router.navigate(['/login']);
  }
}
