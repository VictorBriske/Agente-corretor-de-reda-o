import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Competencia } from '../../models/correcao.model';

@Component({
  selector: 'app-competencia-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './competencia-card.component.html',
  styleUrl: './competencia-card.component.scss'
})
export class CompetenciaCardComponent {
  @Input() competencia!: Competencia;

  get notaColor(): string {
    if (this.competencia.nota >= 160) return 'success';
    if (this.competencia.nota >= 120) return 'primary';
    if (this.competencia.nota >= 80) return 'warning';
    return 'danger';
  }

  get notaTexto(): string {
    if (this.competencia.nota >= 160) return 'Excelente';
    if (this.competencia.nota >= 120) return 'Bom';
    if (this.competencia.nota >= 80) return 'Regular';
    return 'Precisa melhorar';
  }
}
