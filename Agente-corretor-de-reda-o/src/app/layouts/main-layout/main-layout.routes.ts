import { Routes } from '@angular/router';
import { MainLayoutComponent } from './main-layout.component';
import { HomeComponent } from '../../components/home/home.component';
import { RedacaoComponent } from '../../components/redacao/redacao.component';
import { MinhasRedacoesComponent } from '../../components/minhas-redacoes/minhas-redacoes.component';
import { PerfilComponent } from '../../components/perfil/perfil.component';

export const routes: Routes = [
  {
    path: '',
    component: MainLayoutComponent,
    children: [
      {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full'
      },
      {
        path: 'home',
        component: HomeComponent
      },
      {
        path: 'redacao',
        component: RedacaoComponent
      },
      {
        path: 'analises',
        component: MinhasRedacoesComponent
      },
      {
        path: 'redacoes',
        redirectTo: 'analises',
        pathMatch: 'full'
      },
      {
        path: 'perfil',
        component: PerfilComponent
      },
      {
        path: '**',
        redirectTo: 'home'
      }
    ]
  }
];

