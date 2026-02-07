import { Component, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';
import { AnaliseService } from '../../services/analise.service';
import { RedacaoService } from '../../services/redacao.service';
import { CorrecaoService } from '../../services/correcao.service';
import { ResultadoCorrecao } from '../../models/correcao.model';
import { ResultadoCorrecaoComponent } from '../resultado-correcao/resultado-correcao.component';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'app-minhas-analises',
  standalone: true,
  imports: [CommonModule, ResultadoCorrecaoComponent],
  templateUrl: './minhas-analises.component.html',
  styleUrl: './minhas-analises.component.scss'
})
export class MinhasAnalisesComponent implements OnInit {
  private readonly transitionMs = 260;
  private transitionTimeoutId: number | null = null;
  private analiseSub: Subscription | null = null;

  analises: any[] = [];
  isLoading = false;
  error: string | null = null;

  // View/transition state
  listHidden = false;
  listAnimatingOut = false;
  listAnimatingIn = false;
  detailMounted = false;
  detailAnimatingIn = false;
  detailAnimatingOut = false;

  analiseSelecionada: ResultadoCorrecao | null = null;
  carregandoAnalise = false;
  analiseIdSelecionada: string | null = null;
  detailError: string | null = null;

  constructor(
    private analiseService: AnaliseService,
    private redacaoService: RedacaoService,
    private correcaoService: CorrecaoService
  ) {}

  ngOnInit() {
    this.carregarAnalises();
  }

  carregarAnalises() {
    this.isLoading = true;
    this.error = null;

    // Por enquanto, vamos usar um array vazio até implementar o endpoint
    // TODO: Implementar endpoint de listagem de análises no backend
    this.analiseService.listarAnalises(20).subscribe({
      next: (analises) => {
        this.analises = analises || [];
        this.isLoading = false;
      },
      error: (err) => {
        // Se o endpoint não existir, apenas mostrar lista vazia
        this.analises = [];
        this.error = null;
        this.isLoading = false;
      }
    });
  }

  verAnaliseCompleta(redacaoId: string) {
    this.startEnterDetail();

    this.analiseIdSelecionada = redacaoId;
    this.carregandoAnalise = true;
    this.analiseSelecionada = null;
    this.detailError = null;

    this.analiseSub?.unsubscribe();
    this.analiseSub = null;

    this.analiseSub = forkJoin({
      analise: this.analiseService.obterAnalise(redacaoId),
      redacao: this.redacaoService.obterRedacao(redacaoId).pipe(catchError(() => of(null)))
    }).subscribe({
      next: ({ analise, redacao }) => {
        const resultadoBase = this.correcaoService.converterAnaliseParaResultado(analise);
        this.analiseSelecionada = {
          ...resultadoBase,
          textoRedacao: (redacao as any)?.texto,
          tituloRedacao: (redacao as any)?.titulo,
          temaRedacao: (redacao as any)?.tema
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

    this.listHidden = false;
    this.detailMounted = true;

    this.listAnimatingIn = false;
    this.detailAnimatingOut = false;
    this.listAnimatingOut = true;
    this.detailAnimatingIn = true;

    this.transitionTimeoutId = window.setTimeout(() => {
      this.listHidden = true;
      this.listAnimatingOut = false;
      this.detailAnimatingIn = false;
      this.transitionTimeoutId = null;
    }, this.transitionMs);
  }

  private startExitDetail() {
    this.clearTransitionTimeout();

    this.listHidden = false;

    this.listAnimatingOut = false;
    this.detailAnimatingIn = false;
    this.listAnimatingIn = true;
    this.detailAnimatingOut = true;

    this.transitionTimeoutId = window.setTimeout(() => {
      this.listAnimatingIn = false;
      this.detailAnimatingOut = false;
      this.detailMounted = false;

      this.analiseSelecionada = null;
      this.analiseIdSelecionada = null;
      this.carregandoAnalise = false;
      this.detailError = null;

      this.transitionTimeoutId = null;
    }, this.transitionMs);
  }
}

