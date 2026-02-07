import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { AnaliseCompleta, EstatisticasEvolucao } from '../models/redacao.model';

@Injectable({
  providedIn: 'root'
})
export class AnaliseService {
  constructor(private api: ApiService) {}

  obterAnalise(redacaoId: string): Observable<AnaliseCompleta> {
    return this.api.get<AnaliseCompleta>(`/analises/${redacaoId}`);
  }

  listarAnalises(limite: number = 10): Observable<any[]> {
    return this.api.get<any[]>(`/analises?limite=${limite}`);
  }

  obterEstatisticasEvolucao(): Observable<EstatisticasEvolucao> {
    return this.api.get<EstatisticasEvolucao>('/analises/estatisticas/evolucao');
  }
}

