export type TipoRedacao = 'enem' | 'dissertativa' | 'argumentativa' | 'concurso';
export type StatusRedacao = 'pendente' | 'analisando' | 'concluida' | 'erro';

export interface RedacaoSubmit {
  titulo: string;
  texto: string;
  tema: string;
  tipo: TipoRedacao;
  referencias_esperadas?: string[];
}

export interface Redacao {
  id: string;
  usuario_id: string;
  titulo: string;
  texto: string;
  tema: string;
  tipo: TipoRedacao;
  data_submissao: string;
  status: StatusRedacao;
  nota_enem?: number;
  nota_geral?: number;
}

// Análise Gramatical
export interface ErroGramatical {
  trecho: string;
  tipo: string;
  explicacao: string;
  sugestao: string;
  regra: string;
  posicao_inicio?: number;
  posicao_fim?: number;
}

export interface AnaliseGramatical {
  nota: number;
  erros: ErroGramatical[];
  total_erros: number;
  vicios_linguagem: string[];
  feedback_geral: string;
}

// Análise Lógica (Premium)
export interface ProblemaLogico {
  tipo: string;
  paragrafo: number;
  trecho: string;
  explicacao: string;
  sugestao: string;
  posicao_inicio?: number;
  posicao_fim?: number;
}

export interface AnaliseLogica {
  nota: number;
  tese_clara: boolean;
  tese_identificada?: string;
  problemas: ProblemaLogico[];
  profundidade_argumentacao: string;
  falacias_detectadas: string[];
  feedback_geral: string;
}

// Análise Estrutural (Premium)
export interface ProblemaEstrutural {
  tipo: string;
  localizacao: string;
  explicacao: string;
  sugestao: string;
}

export interface AnaliseEstrutural {
  nota: number;
  estrutura_adequada: boolean;
  tem_introducao: boolean;
  tem_desenvolvimento: boolean;
  tem_conclusao: boolean;
  uso_conectivos: { [key: string]: number };
  problemas: ProblemaEstrutural[];
  feedback_geral: string;
}

// Competência ENEM
export interface CompetenciaENEM {
  numero: number;
  nota: number;
  justificativa: string;
  pontos_fortes: string[];
  pontos_fracos: string[];
}

// Avaliação Final
export interface AvaliacaoFinal {
  nota_geral: number;
  nota_enem?: number;
  competencias_enem?: CompetenciaENEM[];
  feedback_geral: string;
  pontos_fortes: string[];
  pontos_fracos: string[];
  sugestoes_melhoria: string[];
}

// Repertório Sociocultural (Premium)
export interface RepertorioSociocultural {
  citacoes_identificadas: Array<{
    tipo: string;
    conteudo: string;
    produtiva: string;
  }>;
  uso_adequado: boolean;
  feedback: string;
}

// Reescrita Comparativa (Premium)
export interface ReescritaComparativa {
  trecho_original: string;
  trecho_reescrito: string;
  explicacao: string;
  melhorias: string[];
}

// Modo Socrático (Premium)
export interface ModoSocratico {
  perguntas: Array<{
    paragrafo: string;
    pergunta: string;
    objetivo: string;
  }>;
}

// Trechos a melhorar (para destaque no front)
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

// Análise Completa
export interface AnaliseCompleta {
  redacao_id: string;
  analise_gramatical: AnaliseGramatical;
  fuga_ao_tema: boolean;
  aderencia_tema: number;
  palavras_chave_usadas: string[];
  analise_logica?: AnaliseLogica;
  analise_estrutural?: AnaliseEstrutural;
  repertorio_sociocultural?: RepertorioSociocultural;
  reescritas_comparativas?: ReescritaComparativa[];
  modo_socratico?: ModoSocratico;
  avaliacao_final: AvaliacaoFinal;
  trechos_melhoria?: TrechoMelhoria[];
  tempo_processamento: number;
  data_analise: string;
  tokens_utilizados?: number;
}

// Estatísticas de Evolução
export interface EstatisticasEvolucao {
  total_analises: number;
  media_geral: number;
  melhor_nota: number;
  pior_nota: number;
  premium: boolean;
  evolucao?: Array<{
    data: string;
    nota: number;
    nota_enem?: number;
  }>;
  mensagem_upgrade?: string;
}

