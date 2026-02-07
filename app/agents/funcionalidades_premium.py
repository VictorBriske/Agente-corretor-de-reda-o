"""
Funcionalidades Premium Adicionais
"""

from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.schemas.redacao import (
    RepertorioSociocultural,
    ReescritaComparativa,
    ModeSocratico
)


class AnalisadorRepertorio(BaseAgent):
    """Analisa repertório sociocultural (Premium)"""
    
    def __init__(self):
        super().__init__(
            nome="Analisador de Repertório",
            descricao="Avalia citações e repertório sociocultural"
        )
    
    def get_system_prompt(self) -> str:
        return """Você é um AVALIADOR DE REPERTÓRIO SOCIOCULTURAL especializado.
Seu papel é identificar e avaliar citações, referências e conhecimentos externos.

TIPOS DE REPERTÓRIO:
- historico: Fatos históricos, períodos, eventos
- filosofico: Filósofos, teorias filosóficas
- literario: Obras, autores, movimentos literários
- cientifico: Dados, pesquisas, estatísticas
- cultural: Filmes, músicas, arte
- juridico: Leis, constituição, jurisprudência

CRITÉRIOS:
1. A citação está CORRETA?
2. Foi usada de forma PRODUTIVA (conectada ao argumento)?
3. Foi apenas "jogada" no texto sem conexão?

Retorne JSON:
{
    "citacoes_identificadas": [
        {
            "tipo": "filosofico",
            "conteudo": "Platão e o mito da caverna",
            "produtiva": "sim",
            "justificativa": "Conectou bem com o argumento sobre alienação"
        }
    ],
    "uso_adequado": true,
    "feedback": "Análise geral"
}"""
    
    async def analisar(self, texto: str, tema: str, contexto: Dict[str, Any]) -> RepertorioSociocultural:
        user_prompt = self._formatar_texto_analise(texto, tema)
        user_prompt += "\n\nIdentifique e avalie o REPERTÓRIO SOCIOCULTURAL usado."
        
        resposta = await self._gerar_resposta(user_prompt, temperature=0.4)
        dados = resposta["content"]
        
        return RepertorioSociocultural(
            citacoes_identificadas=dados.get("citacoes_identificadas", []),
            uso_adequado=dados.get("uso_adequado", True),
            feedback=dados["feedback"]
        )


class GeradorReescrita(BaseAgent):
    """Gera reescritas comparativas (Premium)"""
    
    def __init__(self):
        super().__init__(
            nome="Gerador de Reescrita",
            descricao="Mostra como um especialista escreveria"
        )
    
    def get_system_prompt(self) -> str:
        return """Você é um ESCRITOR EXPERT em redações dissertativo-argumentativas.
Seu papel é REESCREVER trechos problemáticos, mostrando a VERSÃO MELHORADA.

REGRAS:
1. Identifique 2-3 trechos que podem ser MELHORADOS
2. Reescreva cada trecho mostrando como um ESPECIALISTA escreveria
3. EXPLIQUE as melhorias feitas
4. Mantenha a IDEIA ORIGINAL do autor, mas aprimore a forma

Retorne JSON:
{
    "reescritas": [
        {
            "trecho_original": "A educação é importante porque sim.",
            "trecho_reescrito": "A educação configura-se como elemento basilar para o desenvolvimento social, uma vez que capacita indivíduos a exercerem plenamente sua cidadania.",
            "explicacao": "Substituí linguagem coloquial por formal, adicionei fundamento ao argumento",
            "melhorias": ["linguagem mais formal", "argumento fundamentado", "conectivo adequado"]
        }
    ]
}"""
    
    async def analisar(self, texto: str, tema: str, contexto: Dict[str, Any]) -> List[ReescritaComparativa]:
        user_prompt = self._formatar_texto_analise(texto, tema)
        user_prompt += "\n\nIdentifique 2-3 trechos problemáticos e REESCREVA-OS de forma exemplar."
        
        resposta = await self._gerar_resposta(user_prompt, temperature=0.6)
        dados = resposta["content"]
        
        return [
            ReescritaComparativa(**reescrita)
            for reescrita in dados.get("reescritas", [])
        ]


class ModoSocraticoGenerator(BaseAgent):
    """Gera perguntas socráticas (Premium Exclusive)"""
    
    def __init__(self):
        super().__init__(
            nome="Modo Socrático",
            descricao="Faz perguntas para estimular pensamento crítico"
        )
    
    def get_system_prompt(self) -> str:
        return """Você é SÓCRATES, o filósofo que ensina através de PERGUNTAS.
Seu papel é fazer perguntas que levem o aluno a PENSAR e MELHORAR seu texto.

REGRAS:
1. NÃO dê respostas, faça PERGUNTAS
2. Perguntas devem ser ESPECÍFICAS ao texto
3. Objetivo: fazer o aluno CONECTAR ideias, FUNDAMENTAR argumentos, APROFUNDAR raciocínio

TIPOS DE PERGUNTAS:
- Clarificação: "O que você quis dizer com...?"
- Fundamento: "Por que você acredita nisso?"
- Perspectiva: "Como alguém que discorda veria isso?"
- Implicação: "Se isso é verdade, o que se segue?"
- Evidência: "Que evidências apoiam sua afirmação?"

Retorne JSON:
{
    "perguntas": [
        {
            "paragrafo": "2",
            "pergunta": "Você afirmou que a educação resolve todos os problemas, mas não considerou fatores econômicos. Como esses fatores se relacionam com sua tese?",
            "objetivo": "Fazer o aluno considerar complexidade e evitar simplificação"
        }
    ]
}"""
    
    async def analisar(self, texto: str, tema: str, contexto: Dict[str, Any]) -> ModeSocratico:
        user_prompt = self._formatar_texto_analise(texto, tema)
        user_prompt += "\n\nFaça 3-5 PERGUNTAS SOCRÁTICAS para ajudar o aluno a melhorar o texto."
        
        resposta = await self._gerar_resposta(user_prompt, temperature=0.7)
        dados = resposta["content"]
        
        return ModeSocratico(
            perguntas=dados.get("perguntas", [])
        )


# Instâncias globais
analisador_repertorio = AnalisadorRepertorio()
gerador_reescrita = GeradorReescrita()
modo_socratico = ModoSocraticoGenerator()

