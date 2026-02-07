import { Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { ApiService } from './api.service';
import { UsuarioLogin, UsuarioCadastro, TokenResponse, Usuario } from '../models/auth.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject: Usuario | null = null;

  constructor(private api: ApiService) {
    // Tentar recuperar usuário do localStorage
    const userStr = localStorage.getItem('current_user');
    if (userStr) {
      try {
        this.currentUserSubject = JSON.parse(userStr);
      } catch (e) {
        localStorage.removeItem('current_user');
      }
    }
  }

  get currentUser(): Usuario | null {
    return this.currentUserSubject;
  }

  get isAuthenticated(): boolean {
    return !!this.api.getToken() && !!this.currentUserSubject;
  }

  get isPremium(): boolean {
    // Informações de plano removidas do frontend
    return false;
  }

  login(credentials: UsuarioLogin): Observable<TokenResponse> {
    return this.api.post<TokenResponse>('/usuarios/login', credentials).pipe(
      tap(response => {
        this.api.setToken(response.access_token);
        this.setCurrentUser(response.usuario);
      })
    );
  }

  cadastro(dados: UsuarioCadastro): Observable<TokenResponse> {
    return this.api.post<TokenResponse>('/usuarios/cadastro', dados).pipe(
      tap(response => {
        this.api.setToken(response.access_token);
        this.setCurrentUser(response.usuario);
      })
    );
  }

  logout(): void {
    this.api.setToken(null);
    this.currentUserSubject = null;
    localStorage.removeItem('current_user');
  }

  getPerfil(): Observable<Usuario> {
    return this.api.get<Usuario>('/usuarios/me').pipe(
      tap(usuario => {
        this.setCurrentUser(usuario);
      })
    );
  }

  private setCurrentUser(usuario: Usuario): void {
    this.currentUserSubject = usuario;
    localStorage.setItem('current_user', JSON.stringify(usuario));
  }
}

