import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {
  dicasRedacao = [
    {
      titulo: 'Domínio da Modalidade Escrita',
      descricao: 'Demonstre conhecimento da norma padrão da língua portuguesa, evitando desvios gramaticais e ortográficos.',
      numero: '1'
    },
    {
      titulo: 'Compreensão do Tema',
      descricao: 'Desenvolva o tema dentro dos limites estruturais do texto dissertativo-argumentativo em prosa.',
      numero: '2'
    },
    {
      titulo: 'Organização de Argumentos',
      descricao: 'Selecione, relacione, organize e interprete informações, fatos, opiniões e argumentos em defesa de um ponto de vista.',
      numero: '3'
    },
    {
      titulo: 'Mecanismos Linguísticos',
      descricao: 'Demonstre conhecimento dos mecanismos linguísticos necessários para a construção da argumentação.',
      numero: '4'
    },
    {
      titulo: 'Proposta de Intervenção',
      descricao: 'Elabore proposta de intervenção para o problema abordado, respeitando os direitos humanos.',
      numero: '5'
    }
  ];

  ferramentas = [
    {
      titulo: 'Correção Detalhada',
      descricao: 'Receba feedback completo com desvios, comentários e sugestões de melhoria por competência.'
    },
    {
      titulo: 'Feedback por Competência',
      descricao: 'Avaliação baseada no modelo ENEM com feedback individual para cada uma das 5 competências.'
    },
    {
      titulo: 'Detecção de Erros',
      descricao: 'Identificação automática de erros ortográficos e gramaticais destacados na sua redação.'
    },
    {
      titulo: 'Acompanhamento de Progresso',
      descricao: 'Monitore sua evolução com histórico completo e médias por competência.'
    }
  ];
}

