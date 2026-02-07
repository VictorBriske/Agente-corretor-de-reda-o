import { Component, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';
import { RedacaoService } from '../../services/redacao.service';
import { AnaliseService } from '../../services/analise.service';
import { CorrecaoService } from '../../services/correcao.service';
import { ResultadoCorrecaoComponent } from '../resultado-correcao/resultado-correcao.component';
import { Redacao } from '../../models/redacao.model';
import { ResultadoCorrecao } from '../../models/correcao.model';

@Component({
  selector: 'app-minhas-redacoes',
  standalone: true,
  imports: [CommonModule, ResultadoCorrecaoComponent],
  templateUrl: './minhas-redacoes.component.html',
  styleUrl: './minhas-redacoes.component.scss'
})
export class MinhasRedacoesComponent implements OnInit {
  private readonly transitionMs = 260;
  private transitionTimeoutId: number | null = null;
  private analiseSub: Subscription | null = null;

  redacoes: Redacao[] = [];
  isLoading = false;
  error: string | null = null;

  // View/transition state
  listHidden = false; // vira display:none após animação de entrada no detalhe
  listAnimatingOut = false;
  listAnimatingIn = false;
  detailMounted = false; // controla *ngIf do detalhe para permitir animação
  detailAnimatingIn = false;
  detailAnimatingOut = false;

  analiseSelecionada: ResultadoCorrecao | null = null;
  carregandoAnalise = false;
  redacaoIdSelecionada: string | null = null;
  detailError: string | null = null;

  constructor(
    private redacaoService: RedacaoService,
    private analiseService: AnaliseService,
    private correcaoService: CorrecaoService
  ) {}

  ngOnInit() {
    this.carregarRedacoes();
  }

  carregarRedacoes() {
    this.isLoading = true;
    this.error = null;

    this.redacaoService.listarRedacoes(20).subscribe({
      next: (redacoes) => {
        this.redacoes = redacoes;
        this.isLoading = false;
      },
      error: (err) => {
        this.error = err.message || 'Erro ao carregar redações';
        this.isLoading = false;
      }
    });
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'concluida':
        return 'status-success';
      case 'analisando':
        return 'status-processing';
      case 'erro':
        return 'status-error';
      default:
        return 'status-pending';
    }
  }

  getStatusLabel(status: string): string {
    switch (status) {
      case 'concluida':
        return 'Concluída';
      case 'analisando':
        return 'Analisando';
      case 'erro':
        return 'Erro';
      default:
        return 'Pendente';
    }
  }

  verAnalise(redacaoId: string) {
    this.startEnterDetail();

    this.redacaoIdSelecionada = redacaoId;
    this.carregandoAnalise = true;
    this.analiseSelecionada = null;
    this.detailError = null;

    // cancelar request anterior (se existir)
    this.analiseSub?.unsubscribe();
    this.analiseSub = null;

    this.analiseSub = this.analiseService.obterAnalise(redacaoId).subscribe({
      next: (analiseCompleta) => {
        // Converter AnaliseCompleta para ResultadoCorrecao
        const resultadoBase = this.correcaoService.converterAnaliseParaResultado(analiseCompleta);
        const redacao = this.redacoes.find(r => r.id === redacaoId);
        this.analiseSelecionada = {
          ...resultadoBase,
          textoRedacao: redacao?.texto,
          tituloRedacao: redacao?.titulo,
          temaRedacao: redacao?.tema
        };
        this.carregandoAnalise = false;
      },
      error: (err) => {
        this.detailError = err.message || 'Erro ao carregar análise';
        this.carregandoAnalise = false;
      }
    });
  }

  fecharAnalise() {
    this.analiseSub?.unsubscribe();
    this.analiseSub = null;
    this.startExitDetail();
  }

  private clearTransitionTimeout() {
    if (this.transitionTimeoutId != null) {
      window.clearTimeout(this.transitionTimeoutId);
      this.transitionTimeoutId = null;
    }
  }

  private startEnterDetail() {
    this.clearTransitionTimeout();

    // garantir que lista volte a existir durante a animação
    this.listHidden = false;
    this.detailMounted = true;

    this.listAnimatingIn = false;
    this.detailAnimatingOut = false;
    this.listAnimatingOut = true;
    this.detailAnimatingIn = true;

    this.transitionTimeoutId = window.setTimeout(() => {
      this.listHidden = true; // display:none após "entrar" no detalhe
      this.listAnimatingOut = false;
      this.detailAnimatingIn = false;
      this.transitionTimeoutId = null;
    }, this.transitionMs);
  }

  private startExitDetail() {
    this.clearTransitionTimeout();

    // trazer lista de volta para animar "saindo"
    this.listHidden = false;

    this.listAnimatingOut = false;
    this.detailAnimatingIn = false;
    this.listAnimatingIn = true;
    this.detailAnimatingOut = true;

    this.transitionTimeoutId = window.setTimeout(() => {
      this.listAnimatingIn = false;
      this.detailAnimatingOut = false;
      this.detailMounted = false;

      // limpar estado do detalhe ao final
      this.analiseSelecionada = null;
      this.redacaoIdSelecionada = null;
      this.carregandoAnalise = false;
      this.detailError = null;

      this.transitionTimeoutId = null;
    }, this.transitionMs);
  }
}

