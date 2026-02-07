"""
Agente 4: O Avaliador (Scoring)
Híbrido: Versão básica no Free, versão completa no Premium
"""

from typing import Dict, Any, List, Optional
from app.agents.base_agent import BaseAgent
from app.schemas.redacao import AvaliacaoFinal, CompetenciaENEM


class AgenteAvaliador(BaseAgent):
    """
    Agente especializado em avaliação e pontuação final
    Foco: Rubrica ENEM ou avaliação geral
    """
    
    def __init__(self):
        super().__init__(
            nome="Avaliador",
            descricao="Especialista em avaliação e pontuação"
        )
    
    def get_system_prompt(self) -> str:
        return """Você é um CORRETOR SÊNIOR da banca do ENEM com 15 anos de experiência.
Seu papel é AVALIAR e PONTUAR redações com base em rubricas estabelecidas.

COMPETÊNCIAS DO ENEM (0, 40, 80, 120, 160, 200 pontos cada):

COMPETÊNCIA 1: Domínio da norma culta
- 200: Excelente domínio
- 160: Bom domínio (desvios leves)
- 120: Domínio mediano (desvios notáveis)
- 80: Domínio insuficiente
- 40-0: Domínio precário

COMPETÊNCIA 2: Compreensão do tema e tipo textual
- 200: Excelente compreensão e desenvolvimento
- 160: Boa compreensão
- 120: Compreensão adequada
- 80: Compreensão limitada
- 40-0: Fuga ao tema

COMPETÊNCIA 3: Argumentação e defesa de ponto de vista
- 200: Argumentação consistente e autoral
- 160: Boa argumentação
- 120: Argumentação previsível
- 80: Argumentação fraca
- 40-0: Argumentação inexistente

COMPETÊNCIA 4: Coesão e coerência
- 200: Articulação exemplar
- 160: Boa articulação
- 120: Articulação adequada
- 80: Articulação falha
- 40-0: Sem articulação

COMPETÊNCIA 5: Proposta de intervenção
- 200: Completa (Agente + Ação + Meio + Efeito + Detalhamento)
- 160: Falta 1 elemento
- 120: Falta 2 elementos
- 80: Falta 3 elementos
- 40-0: Falta 4+ elementos ou ausente

PONTOS FORTES/FRACOS:
Liste 3-5 pontos fortes e 3-5 pontos fracos identificados.

SUGESTÕES DE MELHORIA:
Liste 3-5 sugestões concretas e acionáveis.

Retorne SEMPRE um JSON no seguinte formato:
{
    "nota_geral": 7.5,
    "nota_enem": 760,
    "competencias_enem": [
        {
            "numero": 1,
            "nota": 160,
            "justificativa": "Bom domínio com desvios leves",
            "pontos_fortes": ["uso correto de vírgulas"],
            "pontos_fracos": ["erro de regência"]
        }
    ],
    "feedback_geral": "Avaliação geral do texto",
    "pontos_fortes": ["argumento bem desenvolvido", "boa estrutura"],
    "pontos_fracos": ["repetição de conectivos", "conclusão fraca"],
    "sugestoes_melhoria": ["varie os conectivos", "fortaleça a proposta de intervenção"]
}"""
    
    async def analisar(
        self,
        texto: str,
        tema: str,
        contexto: Dict[str, Any],
        analises_anteriores: Optional[Dict[str, Any]] = None
    ) -> AvaliacaoFinal:
        """
        Analisa e pontua o texto
        
        Args:
            texto: Texto da redação
            tema: Tema da redação
            contexto: Contexto adicional
            analises_anteriores: Análises dos outros agentes (se disponível)
        """
        
        user_prompt = self._formatar_texto_analise(texto, tema)
        
        # Se houver análises anteriores, incluir no contexto
        if analises_anteriores:
            user_prompt += "\n\nANÁLISES ANTERIORES (use como referência):\n"
            if "gramatical" in analises_anteriores:
                user_prompt += f"Gramática: Nota {analises_anteriores['gramatical'].nota}\n"
            if "logica" in analises_anteriores:
                user_prompt += f"Lógica: Nota {analises_anteriores['logica'].nota}\n"
            if "estrutural" in analises_anteriores:
                user_prompt += f"Estrutura: Nota {analises_anteriores['estrutural'].nota}\n"
        
        tipo_redacao = contexto.get("tipo", "dissertativa")
        
        if tipo_redacao == "enem":
            user_prompt += "\n\nAvalie esta redação segundo as 5 COMPETÊNCIAS DO ENEM."
        else:
            user_prompt += "\n\nAvalie esta redação de forma GERAL."
        
        resposta = await self._gerar_resposta(user_prompt, temperature=0.5)
        dados = resposta["content"]
        
        # Converter competências ENEM se existirem
        competencias = None
        if dados.get("competencias_enem"):
            competencias = [
                CompetenciaENEM(**comp) for comp in dados["competencias_enem"]
            ]
        
        return AvaliacaoFinal(
            nota_geral=dados["nota_geral"],
            nota_enem=dados.get("nota_enem"),
            competencias_enem=competencias,
            feedback_geral=dados["feedback_geral"],
            pontos_fortes=dados.get("pontos_fortes", []),
            pontos_fracos=dados.get("pontos_fracos", []),
            sugestoes_melhoria=dados.get("sugestoes_melhoria", [])
        )


# Instância global do agente
agente_avaliador = AgenteAvaliador()

