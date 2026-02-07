"""
Serviço de integração com LLMs (OpenAI, Gemini)
"""

from typing import Optional, Dict, Any
import json
from app.config import settings


class LLMService:
    """Serviço para interação com LLMs"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        
        # Inicializar cliente baseado no provider
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "gemini":
            self._init_gemini()
    
    def _init_openai(self):
        """Inicializa cliente OpenAI"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except ImportError:
            raise Exception("OpenAI não instalado. Execute: pip install openai")
    
    def _init_gemini(self):
        """Inicializa cliente Gemini"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            raise Exception("Google Generative AI não instalado. Execute: pip install google-generativeai")
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Gera resposta do LLM
        
        Args:
            system_prompt: Prompt de sistema (contexto/role)
            user_prompt: Prompt do usuário
            temperature: Temperatura (0-1)
            max_tokens: Máximo de tokens
            json_mode: Se deve retornar JSON estruturado
            
        Returns:
            Dict com resposta e metadados
        """
        temp = temperature or self.temperature
        tokens = max_tokens or self.max_tokens
        
        if self.provider == "openai":
            return await self._generate_openai(
                system_prompt, user_prompt, temp, tokens, json_mode
            )
        elif self.provider == "gemini":
            return await self._generate_gemini(
                system_prompt, user_prompt, temp, tokens, json_mode
            )
    
    async def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Gera resposta usando OpenAI"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            
            return {
                "content": json.loads(content) if json_mode else content,
                "tokens_used": response.usage.total_tokens,
                "model": response.model
            }
        except Exception as e:
            raise Exception(f"Erro ao chamar OpenAI: {str(e)}")
    
    async def _generate_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Gera resposta usando Gemini"""
        try:
            # Gemini combina system e user prompt
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            if json_mode:
                full_prompt += "\n\nResponda APENAS com um JSON válido."
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            response = self.client.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            content = response.text
            
            return {
                "content": json.loads(content) if json_mode else content,
                "tokens_used": None,  # Gemini não retorna contagem de tokens diretamente
                "model": self.model
            }
        except Exception as e:
            raise Exception(f"Erro ao chamar Gemini: {str(e)}")


# Instância global do serviço
llm_service = LLMService()

