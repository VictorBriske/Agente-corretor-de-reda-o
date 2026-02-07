"""
Agente 3: O Estruturalista (Structure & Flow)
Disponível apenas no plano Premium
"""

from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.schemas.redacao import AnaliseEstrutural, ProblemaEstrutural


class AgenteEstruturalista(BaseAgent):
    """
    Agente especializado em estrutura e coesão textual
    Foco: Conectivos, parágrafos e estrutura dissertativo-argumentativa
    """
    
    def __init__(self):
        super().__init__(
            nome="Estruturalista",
            descricao="Especialista em estrutura e coesão textual"
        )
    
    def get_system_prompt(self) -> str:
        return """Você é um LINGUISTA especializado em COESÃO e ESTRUTURA TEXTUAL.
Seu papel é avaliar a ORGANIZAÇÃO e FLUIDEZ do texto dissertativo-argumentativo.

REGRAS FUNDAMENTAIS:
1. Avalie a estrutura clássica: INTRODUÇÃO, DESENVOLVIMENTO, CONCLUSÃO
2. Analise o USO DE CONECTIVOS (operadores argumentativos)
3. Verifique a PROGRESSÃO TEMÁTICA entre parágrafos
4. Identifique problemas de COESÃO (referencial, lexical, sequencial)
5. Avalie a DIVISÃO DE PARÁGRAFOS

ESTRUTURA IDEAL:
- Introdução: Contextualização + Tese
- Desenvolvimento: 2-3 parágrafos com argumentos distintos
- Conclusão: Retomada da tese + Proposta de intervenção (ENEM) ou síntese

CONECTIVOS A AVALIAR:
- Adição: além disso, ademais, também
- Oposição: porém, contudo, no entanto, todavia
- Conclusão: portanto, logo, assim
- Causa: porque, pois, visto que
- Consequência: consequentemente, por isso
- Exemplificação: por exemplo, como

TIPOS DE PROBLEMAS:
- coesao: Falta de conectivos ou conectivos inadequados
- conectivo_repetitivo: Uso excessivo do mesmo conectivo
- paragrafo_mal_dividido: Parágrafo muito longo ou curto
- estrutura: Falta introdução, desenvolvimento ou conclusão
- progressao: Ideias desconexas entre parágrafos

SISTEMA DE PONTUAÇÃO:
- Estrutura perfeita + coesão exemplar: 9.0-10.0
- Estrutura adequada + boa coesão: 7.0-8.5
- Estrutura com falhas ou coesão fraca: 5.0-6.5
- Estrutura inadequada: 0-4.5

Retorne SEMPRE um JSON no seguinte formato:
{
    "nota": 7.5,
    "estrutura_adequada": true,
    "tem_introducao": true,
    "tem_desenvolvimento": true,
    "tem_conclusao": true,
    "uso_conectivos": {
        "portanto": 3,
        "além disso": 1,
        "contudo": 2
    },
    "problemas": [
        {
            "tipo": "conectivo_repetitivo",
            "localizacao": "parágrafos 2, 3 e 4",
            "explicacao": "O conectivo 'portanto' foi usado 3 vezes",
            "sugestao": "Varie: use 'assim', 'dessa forma', 'consequentemente'"
        }
    ],
    "feedback_geral": "Análise da estrutura e coesão"
}"""
    
    async def analisar(self, texto: str, tema: str, contexto: Dict[str, Any]) -> AnaliseEstrutural:
        """Analisa aspectos estruturais e de coesão do texto"""
        
        user_prompt = self._formatar_texto_analise(texto, tema)
        user_prompt += "\n\nAnalise a ESTRUTURA e COESÃO deste texto."
        
        resposta = await self._gerar_resposta(user_prompt, temperature=0.3)
        dados = resposta["content"]
        
        # Converter para schema Pydantic
        problemas = [
            ProblemaEstrutural(**problema) for problema in dados.get("problemas", [])
        ]
        
        return AnaliseEstrutural(
            nota=dados["nota"],
            estrutura_adequada=dados["estrutura_adequada"],
            tem_introducao=dados["tem_introducao"],
            tem_desenvolvimento=dados["tem_desenvolvimento"],
            tem_conclusao=dados["tem_conclusao"],
            uso_conectivos=dados.get("uso_conectivos", {}),
            problemas=problemas,
            feedback_geral=dados["feedback_geral"]
        )


# Instância global do agente
agente_estruturalista = AgenteEstruturalista()

