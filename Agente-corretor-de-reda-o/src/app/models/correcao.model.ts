export interface Competencia {
  numero: number;
  nome: string;
  nota: number;
  feedback: string;
  sugestoes: string;
}

export interface TrechoMelhoria {
  inicio: number;
  fim: number;
  trecho: string;
  categoria: string;
  tipo: string;
  explicacao: string;
  sugestao: string;
  paragrafo?: number;
}

export interface PerguntaSocratica {
  paragrafo: string;
  pergunta: string;
}

export interface ResultadoCorrecao {
  competencias: Competencia[];
  notaTotal: number;
  comentarioGeral: string;
  /**
   * Texto completo da redação (opcional) para exibição no resultado.
   */
  textoRedacao?: string;
  tituloRedacao?: string;
  temaRedacao?: string;
  trechosMelhoria?: TrechoMelhoria[];
  perguntasSocraticas?: PerguntaSocratica[];
}

export interface RequestCorrecao {
  redacao: string;
  tema: string;
}

