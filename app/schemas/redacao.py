"""
Schemas para redações
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import re


class TipoRedacaoEnum(str, Enum):
    """Tipos de redação"""
    ENEM = "enem"
    DISSERTATIVA = "dissertativa"
    ARGUMENTATIVA = "argumentativa"
    CONCURSO = "concurso"


class RedacaoSubmit(BaseModel):
    """Schema para submissão de redação"""
    titulo: str = Field(..., min_length=5, max_length=200)
    texto: str = Field(..., min_length=100, max_length=10000)
    tema: str = Field(..., min_length=1, max_length=500)  # Reduzido min_length para aceitar "livre"
    tipo: TipoRedacaoEnum = TipoRedacaoEnum.DISSERTATIVA
    referencias_esperadas: Optional[List[str]] = Field(
        default=None,
        description="Palavras-chave esperadas no tema"
    )
    
    @field_validator('texto')
    @classmethod
    def limpar_caracteres_controle(cls, v: str) -> str:
        """
        Remove caracteres de controle inválidos do texto
        Mantém apenas quebras de linha válidas (\n, \r\n)
        """
        if not v:
            return v
        
        # Remover caracteres de controle inválidos (exceto \n, \r, \t)
        # Caracteres válidos: \n (0x0A), \r (0x0D), \t (0x09)
        # Remover outros caracteres de controle (0x00-0x08, 0x0B-0x0C, 0x0E-0x1F)
        texto_limpo = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', v)
        
        # Normalizar quebras de linha para \n
        texto_limpo = texto_limpo.replace('\r\n', '\n').replace('\r', '\n')
        
        return texto_limpo
    
    @field_validator('titulo')
    @classmethod
    def limpar_titulo(cls, v: str) -> str:
        """Remove caracteres de controle do título"""
        if not v:
            return v
        return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', v).strip()
    
    @field_validator('tema')
    @classmethod
    def limpar_tema(cls, v: str) -> str:
        """Remove caracteres de controle do tema"""
        if not v:
            return v
        return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', v).strip()


class RedacaoResponse(BaseModel):
    """Schema de resposta de redação"""
    id: str
    usuario_id: str
    titulo: str
    texto: str
    tema: str
    tipo: TipoRedacaoEnum
    data_submissao: datetime
    status: str = "pendente"  # pendente, analisando, concluída
    nota_enem: Optional[int] = None
    nota_geral: Optional[float] = None
    
    class Config:
        from_attributes = True


class ErroGramatical(BaseModel):
    """Erro gramatical detectado"""
    trecho: str
    tipo: str  # ortografia, regência, concordância, etc
    explicacao: str
    sugestao: str
    regra: str
    posicao_inicio: Optional[int] = None
    posicao_fim: Optional[int] = None


class AnaliseGramatical(BaseModel):
    """Análise do Agente Gramático"""
    nota: float = Field(..., ge=0, le=10)
    erros: List[ErroGramatical]
    total_erros: int
    vicios_linguagem: List[str] = []
    feedback_geral: str


class ProblemaLogico(BaseModel):
    """Problema lógico detectado"""
    tipo: str  # tese_ausente, argumento_fraco, falácia, contradição
    paragrafo: int
    trecho: str
    explicacao: str
    sugestao: str
    posicao_inicio: Optional[int] = None
    posicao_fim: Optional[int] = None


class TrechoMelhoria(BaseModel):
    """Trecho específico do texto que pode ser melhorado, com posição para destaque no frontend."""
    inicio: int = Field(..., ge=0, description="Índice inicial (0-based) no texto original")
    fim: int = Field(..., ge=0, description="Índice final (exclusivo) no texto original")
    trecho: str = Field(..., min_length=1, description="Trecho exato do texto original")
    categoria: str = Field(..., description="origem do apontamento: gramatica, logica, etc")
    tipo: str = Field(..., description="tipo específico do problema")
    explicacao: str
    sugestao: str
    paragrafo: Optional[int] = None


class AnaliseLogica(BaseModel):
    """Análise do Agente Lógico (Premium)"""
    nota: float = Field(..., ge=0, le=10)
    tese_clara: bool
    tese_identificada: Optional[str]
    problemas: List[ProblemaLogico]
    profundidade_argumentacao: str  # superficial, moderada, profunda
    falacias_detectadas: List[str] = []
    feedback_geral: str


class ProblemaEstrutural(BaseModel):
    """Problema estrutural detectado"""
    tipo: str  # coesão, conectivo, parágrafo, estrutura
    localizacao: str
    explicacao: str
    sugestao: str


class AnaliseEstrutural(BaseModel):
    """Análise do Agente Estruturalista (Premium)"""
    nota: float = Field(..., ge=0, le=10)
    estrutura_adequada: bool
    tem_introducao: bool
    tem_desenvolvimento: bool
    tem_conclusao: bool
    uso_conectivos: Dict[str, int]  # conectivo: frequência
    problemas: List[ProblemaEstrutural]
    feedback_geral: str


class CompetenciaENEM(BaseModel):
    """Avaliação de uma competência do ENEM"""
    numero: int = Field(..., ge=1, le=5)
    nota: int = Field(..., ge=0, le=200)
    justificativa: str
    pontos_fortes: List[str] = []
    pontos_fracos: List[str] = []


class AvaliacaoFinal(BaseModel):
    """Avaliação final do Agente Avaliador"""
    nota_geral: float = Field(..., ge=0, le=10)
    nota_enem: Optional[int] = Field(None, ge=0, le=1000)
    competencias_enem: Optional[List[CompetenciaENEM]] = None
    feedback_geral: str
    pontos_fortes: List[str]
    pontos_fracos: List[str]
    sugestoes_melhoria: List[str]


class RepertorioSociocultural(BaseModel):
    """Análise de repertório sociocultural (Premium)"""
    citacoes_identificadas: List[Dict[str, str]]  # {tipo, conteudo, produtiva}
    uso_adequado: bool
    feedback: str


class ReescritaComparativa(BaseModel):
    """Reescrita comparativa (Premium)"""
    trecho_original: str
    trecho_reescrito: str
    explicacao: str
    melhorias: List[str]


class ModeSocratico(BaseModel):
    """Perguntas do modo socrático (Premium)"""
    perguntas: List[Dict[str, str]]  # {paragrafo, pergunta, objetivo}


class AnaliseCompleta(BaseModel):
    """Análise completa da redação"""
    redacao_id: str
    plano_usuario: str
    
    # Análise gramatical (sempre disponível)
    analise_gramatical: AnaliseGramatical
    
    # Detecção de fuga ao tema (sempre disponível)
    fuga_ao_tema: bool
    aderencia_tema: float = Field(..., ge=0, le=100)
    palavras_chave_usadas: List[str]
    
    # Análises Premium
    analise_logica: Optional[AnaliseLogica] = None
    analise_estrutural: Optional[AnaliseEstrutural] = None
    repertorio_sociocultural: Optional[RepertorioSociocultural] = None
    reescritas_comparativas: Optional[List[ReescritaComparativa]] = None
    modo_socratico: Optional[ModeSocratico] = None
    
    # Avaliação final
    avaliacao_final: AvaliacaoFinal

    # Trechos a melhorar (para destaque no frontend)
    trechos_melhoria: List[TrechoMelhoria] = []
    
    # Metadados
    tempo_processamento: float  # em segundos
    data_analise: datetime
    tokens_utilizados: Optional[int] = None
    
    class Config:
        from_attributes = True

