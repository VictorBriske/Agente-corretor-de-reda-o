"""
Orquestrador de Agentes - Sistema Multiagentes
Coordena a execução dos agentes baseado no plano do usuário
"""

import time
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from app.agents.agente_gramatico import agente_gramatico
from app.agents.agente_logico import agente_logico
from app.agents.agente_estruturalista import agente_estruturalista
from app.agents.agente_avaliador import agente_avaliador
from app.agents.funcionalidades_premium import (
    analisador_repertorio,
    gerador_reescrita,
    modo_socratico
)
from app.schemas.redacao import AnaliseCompleta, RedacaoSubmit, TrechoMelhoria
from app.schemas.usuario import PlanoEnum


class OrquestradorAgentes:
    """
    Orquestrador que gerencia o fluxo de análise entre os agentes
    """
    
    def __init__(self):
        self.agente_gramatico = agente_gramatico
        self.agente_logico = agente_logico
        self.agente_estruturalista = agente_estruturalista
        self.agente_avaliador = agente_avaliador
        self.analisador_repertorio = analisador_repertorio
        self.gerador_reescrita = gerador_reescrita
        self.modo_socratico = modo_socratico
    
    async def analisar_redacao(
        self,
        redacao: RedacaoSubmit,
        plano_usuario: PlanoEnum,
        redacao_id: str
    ) -> AnaliseCompleta:
        """
        Analisa uma redação usando os agentes apropriados
        
        Args:
            redacao: Dados da redação
            plano_usuario: Plano do usuário (free, premium, b2b)
            redacao_id: ID da redação
            
        Returns:
            Análise completa estruturada
        """
        inicio = time.time()
        total_tokens = 0
        
        texto = redacao.texto
        tema = redacao.tema
        contexto = {
            "tipo": redacao.tipo.value,
            "referencias_esperadas": redacao.referencias_esperadas or []
        }
        
        # === AGENTE 1: GRAMÁTICO (SEMPRE DISPONÍVEL) ===
        print(f"[AGENT] Executando Agente Gramatico...")
        analise_gramatical = await self.agente_gramatico.analisar(texto, tema, contexto)
        
        # === DETECÇÃO DE FUGA AO TEMA (SEMPRE DISPONÍVEL) ===
        fuga_tema_result = await self._detectar_fuga_tema(texto, tema, contexto)
        
        # === AGENTES PREMIUM ===
        analise_logica = None
        analise_estrutural = None
        repertorio = None
        reescritas = None
        modo_socratico_result = None
        
        if plano_usuario in [PlanoEnum.PREMIUM, PlanoEnum.B2B]:
            print(f"[PREMIUM] Executando analises PREMIUM...")
            
            # Agente 2: Lógico
            print(f"[AGENT] Executando Agente Logico...")
            analise_logica = await self.agente_logico.analisar(texto, tema, contexto)
            
            # Agente 3: Estruturalista
            print(f"[AGENT] Executando Agente Estruturalista...")
            analise_estrutural = await self.agente_estruturalista.analisar(texto, tema, contexto)
            
            # Repertório Sociocultural
            print(f"📚 Analisando Repertório Sociocultural...")
            repertorio = await self.analisador_repertorio.analisar(texto, tema, contexto)
            
            # Reescrita Comparativa
            print(f"✍️  Gerando Reescritas Comparativas...")
            reescritas = await self.gerador_reescrita.analisar(texto, tema, contexto)
            
            # Modo Socrático (Premium Exclusive)
            print(f"🤔 Gerando Perguntas Socráticas...")
            modo_socratico_result = await self.modo_socratico.analisar(texto, tema, contexto)
        
        # === AGENTE 4: AVALIADOR (HÍBRIDO) ===
        print(f"[AGENT] Executando Agente Avaliador...")
        
        # Passar análises anteriores para o avaliador
        analises_anteriores = {
            "gramatical": analise_gramatical
        }
        if analise_logica:
            analises_anteriores["logica"] = analise_logica
        if analise_estrutural:
            analises_anteriores["estrutural"] = analise_estrutural
        
        avaliacao_final = await self.agente_avaliador.analisar(
            texto, tema, contexto, analises_anteriores
        )
        
        # === COMPILAR ANÁLISE COMPLETA ===
        tempo_total = time.time() - inicio

        # === TRECHOS PARA MELHORIA (para destaque no frontend) ===
        trechos_melhoria = self._gerar_trechos_melhoria(
            texto=texto,
            analise_gramatical=analise_gramatical,
            analise_logica=analise_logica
        )
        
        analise_completa = AnaliseCompleta(
            redacao_id=redacao_id,
            plano_usuario=plano_usuario.value,
            
            # Análises sempre disponíveis
            analise_gramatical=analise_gramatical,
            fuga_ao_tema=fuga_tema_result["fuga"],
            aderencia_tema=fuga_tema_result["aderencia"],
            palavras_chave_usadas=fuga_tema_result["palavras_usadas"],
            
            # Análises Premium
            analise_logica=analise_logica,
            analise_estrutural=analise_estrutural,
            repertorio_sociocultural=repertorio,
            reescritas_comparativas=reescritas,
            modo_socratico=modo_socratico_result,
            
            # Avaliação final
            avaliacao_final=avaliacao_final,

            # Trechos a melhorar
            trechos_melhoria=trechos_melhoria,
            
            # Metadados
            tempo_processamento=round(tempo_total, 2),
            data_analise=datetime.now(),
            tokens_utilizados=total_tokens if total_tokens > 0 else None
        )
        
        print(f"[OK] Analise concluida em {tempo_total:.2f}s")
        
        return analise_completa

    def _paragraph_spans(self, texto: str) -> List[Tuple[int, int]]:
        """
        Retorna spans (inicio,fim) de parágrafos (1-based no frontend/agentes).
        Considera parágrafos separados por linha em branco.
        """
        spans: List[Tuple[int, int]] = []
        start = 0
        for m in re.finditer(r'\n\s*\n+', texto):
            end = m.start()
            if texto[start:end].strip():
                spans.append((start, end))
            start = m.end()
        if texto[start:].strip():
            spans.append((start, len(texto)))
        return spans

    def _find_span(self, texto: str, trecho: str, paragrafo: Optional[int] = None) -> Optional[Tuple[int, int]]:
        """
        Tenta localizar o trecho no texto e retornar (inicio,fim) 0-based.
        - Primeiro tenta busca exata (preferindo parágrafo indicado).
        - Se falhar, tenta busca tolerante a whitespace.
        """
        if not trecho or not texto:
            return None

        spans = self._paragraph_spans(texto)

        # 1) Buscar dentro do parágrafo indicado (quando possível)
        if paragrafo and 1 <= paragrafo <= len(spans):
            p_start, p_end = spans[paragrafo - 1]
            sub = texto[p_start:p_end]
            idx = sub.find(trecho)
            if idx != -1:
                inicio = p_start + idx
                return (inicio, inicio + len(trecho))

        # 2) Buscar exato no texto todo
        idx = texto.find(trecho)
        if idx != -1:
            return (idx, idx + len(trecho))

        # 3) Buscar tolerante a whitespace (mantendo posições do texto original)
        tokens = re.split(r'\s+', trecho.strip())
        if not tokens:
            return None
        pattern = r'\s+'.join(re.escape(t) for t in tokens)
        m = re.search(pattern, texto, flags=re.MULTILINE)
        if m:
            return (m.start(), m.end())

        return None

    def _dedupe_and_limit(self, trechos: List[TrechoMelhoria], limite: int = 25) -> List[TrechoMelhoria]:
        """Ordena por posição, remove overlaps simples e limita quantidade."""
        trechos_sorted = sorted(trechos, key=lambda t: (t.inicio, t.fim))
        filtrados: List[TrechoMelhoria] = []
        last_end = -1
        for t in trechos_sorted:
            if t.inicio < last_end:
                continue
            filtrados.append(t)
            last_end = t.fim
            if len(filtrados) >= limite:
                break
        return filtrados

    def _gerar_trechos_melhoria(
        self,
        texto: str,
        analise_gramatical: Any,
        analise_logica: Optional[Any]
    ) -> List[TrechoMelhoria]:
        """
        Constrói uma lista unificada de trechos a melhorar com posições,
        baseada nos apontamentos dos agentes.
        """
        trechos: List[TrechoMelhoria] = []

        # Gramática
        try:
            for erro in getattr(analise_gramatical, "erros", []) or []:
                span = self._find_span(texto, getattr(erro, "trecho", ""))
                if not span:
                    continue
                inicio, fim = span
                trecho_exato = texto[inicio:fim]
                # Preencher posições no próprio erro (útil para persistência)
                try:
                    erro.posicao_inicio = inicio
                    erro.posicao_fim = fim
                    erro.trecho = trecho_exato
                except Exception:
                    pass

                trechos.append(TrechoMelhoria(
                    inicio=inicio,
                    fim=fim,
                    trecho=trecho_exato,
                    categoria="gramatica",
                    tipo=getattr(erro, "tipo", "gramatica"),
                    explicacao=getattr(erro, "explicacao", ""),
                    sugestao=getattr(erro, "sugestao", ""),
                    paragrafo=None
                ))
        except Exception:
            pass

        # Lógica (Premium)
        if analise_logica:
            try:
                for problema in getattr(analise_logica, "problemas", []) or []:
                    par = getattr(problema, "paragrafo", None)
                    span = self._find_span(texto, getattr(problema, "trecho", ""), paragrafo=par)
                    if not span:
                        continue
                    inicio, fim = span
                    trecho_exato = texto[inicio:fim]
                    # Preencher posições no próprio problema (útil para persistência)
                    try:
                        problema.posicao_inicio = inicio
                        problema.posicao_fim = fim
                        problema.trecho = trecho_exato
                    except Exception:
                        pass

                    trechos.append(TrechoMelhoria(
                        inicio=inicio,
                        fim=fim,
                        trecho=trecho_exato,
                        categoria="logica",
                        tipo=getattr(problema, "tipo", "logica"),
                        explicacao=getattr(problema, "explicacao", ""),
                        sugestao=getattr(problema, "sugestao", ""),
                        paragrafo=par if isinstance(par, int) else None
                    ))
            except Exception:
                pass

        return self._dedupe_and_limit(trechos)
    
    async def _detectar_fuga_tema(
        self,
        texto: str,
        tema: str,
        contexto: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detecta se o texto fugiu ao tema proposto
        
        Returns:
            Dict com fuga (bool), aderencia (float 0-100) e palavras_usadas
        """
        # Extrair palavras-chave do tema
        palavras_tema = set(tema.lower().split())
        palavras_tema = {p for p in palavras_tema if len(p) > 3}  # Filtrar palavras curtas
        
        # Verificar presença no texto
        texto_lower = texto.lower()
        palavras_usadas = [p for p in palavras_tema if p in texto_lower]
        
        # Calcular aderência
        if len(palavras_tema) > 0:
            aderencia = (len(palavras_usadas) / len(palavras_tema)) * 100
        else:
            aderencia = 0
        
        # Se tiver menos de 30% das palavras-chave, pode ser fuga
        fuga = aderencia < 30
        
        # Adicionar palavras esperadas do contexto
        if contexto.get("referencias_esperadas"):
            palavras_usadas.extend([
                ref for ref in contexto["referencias_esperadas"]
                if ref.lower() in texto_lower
            ])
        
        return {
            "fuga": fuga,
            "aderencia": round(aderencia, 2),
            "palavras_usadas": list(set(palavras_usadas))
        }


# Instância global do orquestrador
orquestrador = OrquestradorAgentes()

