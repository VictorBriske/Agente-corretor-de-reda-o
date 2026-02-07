export interface UsuarioLogin {
  email: string;
  senha: string;
}

export interface UsuarioCadastro {
  email: string;
  nome: string;
  senha: string;
}

export interface Usuario {
  id: string;
  email: string;
  nome: string;
  data_criacao: string;
  correcoes_realizadas_hoje: number;
  limite_diario: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}

