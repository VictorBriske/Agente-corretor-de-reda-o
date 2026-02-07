import { Injectable } from '@angular/core';
import { Observable, switchMap, throwError } from 'rxjs';
import { RedacaoService } from './redacao.service';
import { AnaliseService } from './analise.service';
import { RedacaoSubmit } from '../models/redacao.model';
import { AnaliseCompleta } from '../models/redacao.model';
import { Competencia, ResultadoCorrecao, TrechoMelhoria, PerguntaSocratica } from '../models/correcao.model';

@Injectable({
  providedIn: 'root'
})
export class CorrecaoService {
  constructor(
    private redacaoService: RedacaoService,
    private analiseService: AnaliseService
  ) {}

  /**
   * Submete uma redação e aguarda o processamento
   * Retorna o resultado da análise convertido para o formato esperado
   */
  corrigirRedacao(request: { redacao: string, tema: string }): Observable<ResultadoCorrecao> {
    // Criar objeto de submissão
    const redacaoSubmit: RedacaoSubmit = {
      titulo: `Redação sobre ${request.tema}`,
      texto: request.redacao,
      tema: request.tema,
      tipo: 'dissertativa'
    };

    // Submeter redação
    return this.redacaoService.submeterRedacao(redacaoSubmit).pipe(
      switchMap((redacao) => {
        // Aguardar processamento (polling)
        return this.redacaoService.aguardarProcessamento(redacao.id).pipe(
          switchMap((redacaoProcessada) => {
            if (redacaoProcessada.status === 'erro') {
              return throwError(() => new Error('Erro ao processar a redação'));
            }
            
            // Se chegou aqui, está concluída (aguardarProcessamento só retorna quando concluída ou erro)
            // Buscar análise completa
            return this.analiseService.obterAnalise(redacao.id);
          })
        );
      }),
      switchMap((analise: AnaliseCompleta) => {
        // Converter análise para o formato esperado pelo componente
        return new Observable<ResultadoCorrecao>(observer => {
          const resultado = this.converterAnaliseParaResultado(analise);
          observer.next(resultado);
          observer.complete();
        });
      })
    );
  }

  /**
   * Converte a análise completa do backend para o formato esperado pelo frontend
   */
  converterAnaliseParaResultado(analise: AnaliseCompleta): ResultadoCorrecao {
    const competencias: Competencia[] = [];

    // Se tiver competências ENEM (Premium), usar elas
    if (analise.avaliacao_final.competencias_enem && analise.avaliacao_final.competencias_enem.length > 0) {
      const nomesCompetencias = [
        'Domínio da norma culta',
        'Compreensão do tema',
        'Seleção e organização de argumentos',
        'Mecanismos linguísticos',
        'Proposta de intervenção'
      ];

      competencias.push(...analise.avaliacao_final.competencias_enem.map((comp, index) => ({
        numero: comp.numero,
        nome: nomesCompetencias[comp.numero - 1] || `Competência ${comp.numero}`,
        nota: comp.nota,
        feedback: comp.justificativa,
        sugestoes: comp.pontos_fracos.join(' ')
      })));
    } else {
      // Para usuários Free, criar competências baseadas na análise gramatical e avaliação final
      const notaGeral = analise.avaliacao_final.nota_geral;
      const notaEnem = analise.avaliacao_final.nota_enem || Math.round(notaGeral * 100);
      
      // Distribuir a nota entre as 5 competências (aproximação)
      const notaPorCompetencia = Math.round(notaEnem / 5);
      
      competencias.push(
        {
          numero: 1,
          nome: 'Domínio da norma culta',
          nota: Math.round(analise.avaliacao_final.nota_geral * 20), // Converter para escala 0-200
          feedback: analise.analise_gramatical.feedback_geral,
          sugestoes: analise.analise_gramatical.erros.map(e => e.sugestao).join(' ')
        },
        {
          numero: 2,
          nome: 'Compreensão do tema',
          nota: Math.round(analise.aderencia_tema * 2), // Converter para escala 0-200
          feedback: analise.fuga_ao_tema 
            ? 'Atenção: Fuga ao tema detectada. ' 
            : `Aderência ao tema: ${analise.aderencia_tema.toFixed(1)}%. `,
          sugestoes: analise.palavras_chave_usadas.length > 0 
            ? `Palavras-chave utilizadas: ${analise.palavras_chave_usadas.join(', ')}`
            : 'Tente utilizar mais palavras-chave relacionadas ao tema.'
        },
        {
          numero: 3,
          nome: 'Seleção e organização de argumentos',
          nota: notaPorCompetencia,
          feedback: analise.avaliacao_final.feedback_geral,
          sugestoes: analise.avaliacao_final.sugestoes_melhoria.join(' ')
        },
        {
          numero: 4,
          nome: 'Mecanismos linguísticos',
          nota: notaPorCompetencia,
          feedback: analise.analise_estrutural?.feedback_geral || analise.avaliacao_final.feedback_geral,
          sugestoes: analise.analise_estrutural?.problemas.map(p => p.sugestao).join(' ') || ''
        },
        {
          numero: 5,
          nome: 'Proposta de intervenção',
          nota: notaPorCompetencia,
          feedback: analise.avaliacao_final.feedback_geral,
          sugestoes: analise.avaliacao_final.sugestoes_melhoria.join(' ')
        }
      );
    }

    return {
      competencias,
      notaTotal: analise.avaliacao_final.nota_enem || Math.round(analise.avaliacao_final.nota_geral * 100),
      comentarioGeral: analise.avaliacao_final.feedback_geral,
      trechosMelhoria: (analise.trechos_melhoria || []).map((t): TrechoMelhoria => ({
        inicio: t.inicio,
        fim: t.fim,
        trecho: t.trecho,
        categoria: t.categoria,
        tipo: t.tipo,
        explicacao: t.explicacao,
        sugestao: t.sugestao,
        paragrafo: t.paragrafo
      })),
      perguntasSocraticas: (analise.modo_socratico?.perguntas || []).map((p): PerguntaSocratica => ({
        paragrafo: p.paragrafo,
        pergunta: p.pergunta
      }))
    };
  }
}
