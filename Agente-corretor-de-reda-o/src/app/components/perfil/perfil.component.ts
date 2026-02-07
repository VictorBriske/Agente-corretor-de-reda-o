import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { Usuario } from '../../models/auth.model';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './perfil.component.html',
  styleUrl: './perfil.component.scss'
})
export class PerfilComponent implements OnInit {
  usuario: Usuario | null = null;
  isLoading = false;
  error: string | null = null;

  constructor(private authService: AuthService) {}

  ngOnInit() {
    this.carregarPerfil();
  }

  carregarPerfil() {
    this.isLoading = true;
    this.error = null;

    if (this.authService.currentUser) {
      this.usuario = this.authService.currentUser;
      this.isLoading = false;
    } else {
      this.authService.getPerfil().subscribe({
        next: (usuario) => {
          this.usuario = usuario;
          this.isLoading = false;
        },
        error: (err) => {
          this.error = err.message || 'Erro ao carregar perfil';
          this.isLoading = false;
        }
      });
    }
  }
}

