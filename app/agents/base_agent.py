"""
Agente Base - Classe abstrata para todos os agentes
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from app.services.llm_service import llm_service


class BaseAgent(ABC):
    """Classe base para todos os agentes"""
    
    def __init__(self, nome: str, descricao: str):
        self.nome = nome
        self.descricao = descricao
        self.llm_service = llm_service
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Retorna o system prompt específico do agente"""
        pass
    
    @abstractmethod
    async def analisar(self, texto: str, tema: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa o texto e retorna resultado estruturado
        
        Args:
            texto: Texto da redação
            tema: Tema da redação
            contexto: Contexto adicional (tipo de redação, etc)
            
        Returns:
            Dicionário com análise estruturada
        """
        pass
    
    async def _gerar_resposta(
        self,
        user_prompt: str,
        temperature: float = 0.7,
        json_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Gera resposta usando o LLM
        
        Args:
            user_prompt: Prompt do usuário
            temperature: Temperatura do modelo
            json_mode: Se deve retornar JSON
            
        Returns:
            Resposta do LLM
        """
        system_prompt = self.get_system_prompt()
        
        return await self.llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            json_mode=json_mode
        )
    
    def _formatar_texto_analise(self, texto: str, tema: str) -> str:
        """Formata o texto para análise"""
        return f"""
TEMA: {tema}

TEXTO DA REDAÇÃO:
{texto}
"""

