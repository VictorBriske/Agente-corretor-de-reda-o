import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { UsuarioLogin } from '../../models/auth.model';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  email = '';
  senha = '';
  showPassword = false;
  isLoading = false;
  error: string | null = null;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit() {
    if (!this.email || !this.senha) {
      this.error = 'Por favor, preencha todos os campos';
      return;
    }

    this.isLoading = true;
    this.error = null;

    const credentials: UsuarioLogin = {
      email: this.email,
      senha: this.senha
    };

    this.authService.login(credentials).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/app/home']);
      },
      error: (err) => {
        this.isLoading = false;
        this.error = err.message || 'Erro ao fazer login. Verifique suas credenciais.';
      }
    });
  }
}

