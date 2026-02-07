import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RedacaoFormComponent } from '../redacao-form/redacao-form.component';
import { ResultadoCorrecaoComponent } from '../resultado-correcao/resultado-correcao.component';
import { RedacaoService } from '../../services/redacao.service';
import { ResultadoCorrecao } from '../../models/correcao.model';

@Component({
  selector: 'app-redacao',
  standalone: true,
  imports: [CommonModule, RedacaoFormComponent, ResultadoCorrecaoComponent],
  templateUrl: './redacao.component.html',
  styleUrl: './redacao.component.scss'
})
export class RedacaoComponent {
  @ViewChild(RedacaoFormComponent) formComponent!: RedacaoFormComponent;

  resultado: ResultadoCorrecao | null = null;
  isLoading = false;
  redacaoEnviada = false;

  constructor(private redacaoService: RedacaoService) {}

  onEnviarRedacao(data: {titulo: string, redacao: string, tema: string}) {
    this.isLoading = true;
    this.resultado = null;
    this.redacaoEnviada = false;

    if (this.formComponent) {
      this.formComponent.setLoading(true);
    }

    const redacaoSubmit = {
      titulo: data.titulo,
      texto: data.redacao,
      tema: data.tema,
      tipo: 'dissertativa' as const
    };

    this.redacaoService.submeterRedacao(redacaoSubmit).subscribe({
      next: () => {
        this.isLoading = false;
        this.redacaoEnviada = true;
        if (this.formComponent) {
          this.formComponent.setLoading(false);
        }
      },
      error: (error) => {
        console.error('Erro ao enviar redação:', error);
        this.isLoading = false;
        this.redacaoEnviada = false;
        if (this.formComponent) {
          this.formComponent.setLoading(false);
        }
        alert(error.message || 'Não foi possível enviar a redação. Tente novamente.');
      }
    });
  }
}

