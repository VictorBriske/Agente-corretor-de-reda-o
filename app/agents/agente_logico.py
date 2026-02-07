"""
Agente 2: O Lógico (Coherence & Argumentation)
Disponível apenas no plano Premium
"""

from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.schemas.redacao import AnaliseLogica, ProblemaLogico


class AgenteLogico(BaseAgent):
    """
    Agente especializado em análise lógica e argumentação
    Foco: Tese, argumentos, falácias e coerência lógica
    """
    
    def __init__(self):
        super().__init__(
            nome="Lógico",
            descricao="Especialista em argumentação e coerência lógica"
        )
    
    def get_system_prompt(self) -> str:
        return """Você é um FILÓSOFO e ANALISTA DE ARGUMENTAÇÃO especializado em lógica e retórica.
Seu papel é avaliar a QUALIDADE ARGUMENTATIVA de redações dissertativo-argumentativas.

REGRAS FUNDAMENTAIS:
1. Identifique a TESE principal do texto (se existir)
2. Avalie se os ARGUMENTOS sustentam a tese
3. Detecte FALÁCIAS LÓGICAS (ad hominem, espantalho, apelo à autoridade, etc)
4. Identifique CONTRADIÇÕES internas
5. Avalie a PROFUNDIDADE da argumentação

TIPOS DE PROBLEMAS:
- tese_ausente: Não há tese clara
- tese_confusa: Tese mal formulada ou ambígua
- argumento_fraco: Argumento superficial ou sem fundamento
- falacia: Falácia lógica detectada
- contradicao: Contradição entre parágrafos/ideias
- argumento_circular: O argumento não prova a tese, apenas a repete
- generalizacao_apressada: Conclusão baseada em amostra insuficiente

PROFUNDIDADE DA ARGUMENTAÇÃO:
- superficial: Apenas senso comum, sem desenvolvimento
- moderada: Argumentos desenvolvidos, mas previsíveis
- profunda: Argumentação complexa, bem fundamentada e original

SISTEMA DE PONTUAÇÃO:
- Tese clara + argumentos sólidos + sem falácias: 9.0-10.0
- Tese clara + argumentos medianos: 7.0-8.5
- Tese confusa ou argumentos fracos: 5.0-6.5
- Sem tese ou argumentação incoerente: 0-4.5

Retorne SEMPRE um JSON no seguinte formato:
{
    "nota": 8.0,
    "tese_clara": true,
    "tese_identificada": "A educação é a base para o desenvolvimento",
    "problemas": [
        {
            "tipo": "argumento_fraco",
            "paragrafo": 2,
            "trecho": "trecho problemático",
            "explicacao": "Por que é problemático",
            "sugestao": "Como melhorar"
        }
    ],
    "profundidade_argumentacao": "moderada",
    "falacias_detectadas": ["apelo à autoridade sem fundamento"],
    "feedback_geral": "Análise completa da argumentação"
}"""
    
    async def analisar(self, texto: str, tema: str, contexto: Dict[str, Any]) -> AnaliseLogica:
        """Analisa aspectos lógicos e argumentativos do texto"""
        
        user_prompt = self._formatar_texto_analise(texto, tema)
        user_prompt += "\n\nAnalise a LÓGICA e ARGUMENTAÇÃO deste texto com rigor filosófico."
        
        resposta = await self._gerar_resposta(user_prompt, temperature=0.4)
        dados = resposta["content"]
        
        # Converter para schema Pydantic
        problemas = [
            ProblemaLogico(**problema) for problema in dados.get("problemas", [])
        ]
        
        return AnaliseLogica(
            nota=dados["nota"],
            tese_clara=dados["tese_clara"],
            tese_identificada=dados.get("tese_identificada"),
            problemas=problemas,
            profundidade_argumentacao=dados["profundidade_argumentacao"],
            falacias_detectadas=dados.get("falacias_detectadas", []),
            feedback_geral=dados["feedback_geral"]
        )


# Instância global do agente
agente_logico = AgenteLogico()

