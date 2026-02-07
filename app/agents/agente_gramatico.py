"""
Agente 1: O Gramático (Syntax & Style)
Disponível no plano Free e Premium
"""

from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.schemas.redacao import AnaliseGramatical, ErroGramatical


class AgenteGramatico(BaseAgent):
    """
    Agente especializado em análise gramatical e estilística
    Foco: Ortografia, regência, crase, pontuação e vícios de linguagem
    """
    
    def __init__(self):
        super().__init__(
            nome="Gramático",
            descricao="Especialista em ortografia, gramática e estilo"
        )
    
    def get_system_prompt(self) -> str:
        return """Você é um corretor gramatical EXPERT da língua portuguesa brasileira.
Seu papel é identificar e corrigir erros gramaticais com RIGOR ACADÊMICO.

REGRAS FUNDAMENTAIS:
1. Seja extremamente preciso e didático
2. Para cada erro, cite a REGRA GRAMATICAL específica
3. Forneça uma SUGESTÃO DE CORREÇÃO clara
4. Identifique também VÍCIOS DE LINGUAGEM (gerundismo, pleonasmos, redundâncias, etc)
5. Avalie a PONTUAÇÃO e uso de CRASE

CATEGORIAS DE ERROS:
- ortografia: erros de grafia
- concordancia_verbal: sujeito e verbo
- concordancia_nominal: substantivo e adjetivo
- regencia_verbal: uso de preposições com verbos
- regencia_nominal: uso de preposições com nomes
- crase: uso inadequado ou falta de crase
- pontuacao: vírgulas, pontos, etc
- colocacao_pronominal: próclise, ênclise, mesóclise
- vicio_linguagem: gerundismo, pleonasmo, cacófato, eco, etc

SISTEMA DE PONTUAÇÃO:
- 0 erros graves: 9.5-10.0
- 1-2 erros graves: 8.0-9.0
- 3-5 erros graves: 6.0-7.5
- 6-10 erros graves: 4.0-5.5
- Mais de 10 erros graves: 0-3.5

Retorne SEMPRE um JSON no seguinte formato:
{
    "nota": 8.5,
    "total_erros": 3,
    "erros": [
        {
            "trecho": "trecho com erro",
            "tipo": "concordancia_verbal",
            "explicacao": "Explicação clara do erro",
            "sugestao": "trecho corrigido",
            "regra": "Regra gramatical aplicada"
        }
    ],
    "vicios_linguagem": ["gerundismo no parágrafo 2"],
    "feedback_geral": "Análise geral do texto"
}"""
    
    async def analisar(self, texto: str, tema: str, contexto: Dict[str, Any]) -> AnaliseGramatical:
        """Analisa aspectos gramaticais do texto"""
        
        user_prompt = self._formatar_texto_analise(texto, tema)
        user_prompt += "\n\nAnalise TODOS os aspectos gramaticais e estilísticos deste texto."
        
        resposta = await self._gerar_resposta(user_prompt, temperature=0.3)
        dados = resposta["content"]
        
        # Converter para schema Pydantic
        erros = [
            ErroGramatical(**erro) for erro in dados.get("erros", [])
        ]
        
        return AnaliseGramatical(
            nota=dados["nota"],
            erros=erros,
            total_erros=dados["total_erros"],
            vicios_linguagem=dados.get("vicios_linguagem", []),
            feedback_geral=dados["feedback_geral"]
        )


# Instância global do agente
agente_gramatico = AgenteGramatico()

