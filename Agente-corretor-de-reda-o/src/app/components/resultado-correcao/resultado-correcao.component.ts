import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ResultadoCorrecao, TrechoMelhoria } from '../../models/correcao.model';
import { CompetenciaCardComponent } from '../competencia-card/competencia-card.component';

@Component({
  selector: 'app-resultado-correcao',
  standalone: true,
  imports: [CommonModule, CompetenciaCardComponent],
  templateUrl: './resultado-correcao.component.html',
  styleUrl: './resultado-correcao.component.scss'
})
export class ResultadoCorrecaoComponent {
  @Input() resultado!: ResultadoCorrecao;

  get textoSegmentado(): Array<{ texto: string; melhoria?: TrechoMelhoria }> {
    const texto = this.resultado?.textoRedacao || '';
    const trechos = (this.resultado?.trechosMelhoria || [])
      .filter(t => Number.isFinite(t.inicio) && Number.isFinite(t.fim) && t.fim > t.inicio)
      .sort((a, b) => a.inicio - b.inicio);

    if (!texto || trechos.length === 0) {
      return [{ texto }];
    }

    // Normalizar: remover overlaps simples
    const normalizados: TrechoMelhoria[] = [];
    let lastEnd = -1;
    for (const t of trechos) {
      if (t.inicio < 0 || t.fim > texto.length) continue;
      if (t.inicio < lastEnd) continue;
      normalizados.push(t);
      lastEnd = t.fim;
    }

    const segmentos: Array<{ texto: string; melhoria?: TrechoMelhoria }> = [];
    let cursor = 0;
    for (const t of normalizados) {
      if (t.inicio > cursor) {
        segmentos.push({ texto: texto.slice(cursor, t.inicio) });
      }
      segmentos.push({ texto: texto.slice(t.inicio, t.fim), melhoria: t });
      cursor = t.fim;
    }
    if (cursor < texto.length) {
      segmentos.push({ texto: texto.slice(cursor) });
    }
    return segmentos;
  }

  tipText(m: TrechoMelhoria): string {
    const parts = [m.explicacao, m.sugestao].filter(Boolean);
    return parts.join(' • ');
  }
}
