import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { UsuarioCadastro } from '../../models/auth.model';

@Component({
  selector: 'app-cadastro',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './cadastro.component.html',
  styleUrl: './cadastro.component.scss'
})
export class CadastroComponent {
  nome = '';
  email = '';
  senha = '';
  confirmarSenha = '';
  showPassword = false;
  showConfirmPassword = false;
  isLoading = false;
  error: string | null = null;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  get isValid(): boolean {
    return this.nome.length >= 3 &&
           this.email.includes('@') &&
           this.senha.length >= 6 &&
           this.senha === this.confirmarSenha;
  }

  onSubmit() {
    if (!this.isValid) {
      this.error = 'Por favor, preencha todos os campos corretamente';
      return;
    }

    this.isLoading = true;
    this.error = null;

    const dados: UsuarioCadastro = {
      nome: this.nome,
      email: this.email,
      senha: this.senha
    };

    this.authService.cadastro(dados).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/app/home']);
      },
      error: (err) => {
        this.isLoading = false;
        this.error = err.message || 'Erro ao criar conta. Tente novamente.';
      }
    });
  }
}

