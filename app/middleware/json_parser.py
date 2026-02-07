"""
Parser JSON customizado que limpa caracteres de controle
"""

import json
import re
from typing import Any


def limpar_caracteres_controle(texto: str) -> str:
    """Remove caracteres de controle inválidos"""
    if not texto:
        return texto
    # Remover caracteres de controle (exceto \n, \r, \t)
    texto_limpo = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', texto)
    # Normalizar quebras de linha
    texto_limpo = texto_limpo.replace('\r\n', '\n').replace('\r', '\n')
    return texto_limpo


def parse_json_com_limpeza(json_str: str) -> Any:
    """
    Parse JSON com limpeza automática de caracteres de controle
    """
    # Limpar caracteres de controle
    json_limpo = limpar_caracteres_controle(json_str)
    
    # Tentar fazer parse
    try:
        return json.loads(json_limpo)
    except json.JSONDecodeError as e:
        # Se ainda der erro, tentar limpar mais agressivamente
        # Remover todos os caracteres de controle
        json_ultra_limpo = re.sub(r'[\x00-\x1F]', '', json_limpo)
        try:
            return json.loads(json_ultra_limpo)
        except:
            raise e

