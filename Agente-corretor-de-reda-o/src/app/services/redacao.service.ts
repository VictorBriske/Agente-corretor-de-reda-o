import { Injectable } from '@angular/core';
import { Observable, interval, switchMap, takeWhile, throwError, of } from 'rxjs';
import { ApiService } from './api.service';
import { Redacao, RedacaoSubmit, StatusRedacao } from '../models/redacao.model';

@Injectable({
  providedIn: 'root'
})
export class RedacaoService {
  constructor(private api: ApiService) {}

  submeterRedacao(redacao: RedacaoSubmit): Observable<Redacao> {
    return this.api.post<Redacao>('/redacoes', redacao);
  }

  obterRedacao(redacaoId: string): Observable<Redacao> {
    return this.api.get<Redacao>(`/redacoes/${redacaoId}`);
  }

  listarRedacoes(limite: number = 10): Observable<Redacao[]> {
    return this.api.get<Redacao[]>(`/redacoes?limite=${limite}`);
  }

  /**
   * Aguarda até que a redação seja processada
   * Faz polling a cada 2 segundos até o status ser 'concluida' ou 'erro'
   */
  aguardarProcessamento(redacaoId: string, maxTentativas: number = 60): Observable<Redacao> {
    let tentativas = 0;
    
    // Primeira verificação imediata
    return this.obterRedacao(redacaoId).pipe(
      switchMap((redacaoInicial) => {
        // Se já está concluída ou com erro, retornar imediatamente
        if (redacaoInicial.status === 'concluida' || redacaoInicial.status === 'erro') {
          return of(redacaoInicial);
        }
        
        // Caso contrário, fazer polling
        return interval(2000).pipe(
          switchMap(() => {
            tentativas++;
            if (tentativas > maxTentativas) {
              return throwError(() => new Error('Tempo limite de processamento excedido'));
            }
            
            return this.obterRedacao(redacaoId);
          }),
          takeWhile((redacao: Redacao) => {
            const status = redacao.status;
            return status === 'pendente' || status === 'analisando';
          }, true) // inclusive: inclui o último valor que não passou no takeWhile
        );
      })
    );
  }
}

