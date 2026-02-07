import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { CadastroComponent } from './components/cadastro/cadastro.component';
import { authGuard, loginGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    component: LoginComponent,
    canActivate: [loginGuard]
  },
  {
    path: 'cadastro',
    component: CadastroComponent,
    canActivate: [loginGuard]
  },
  {
    path: 'app',
    canActivate: [authGuard],
    loadChildren: () => import('./layouts/main-layout/main-layout.routes').then(m => m.routes)
  },
  {
    path: '**',
    redirectTo: '/login'
  }
];

