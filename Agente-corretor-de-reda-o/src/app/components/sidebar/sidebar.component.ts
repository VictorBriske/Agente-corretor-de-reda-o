import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent {
  @Input() isCollapsed = false;
  @Output() toggleCollapse = new EventEmitter<void>();

  currentRoute = '';

  constructor(
    public authService: AuthService,
    private router: Router
  ) {
    // Detectar mudanças de rota
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: any) => {
        const url = event.urlAfterRedirects;
        if (url.startsWith('/app/')) {
          this.currentRoute = url.replace('/app/', '');
        } else {
          this.currentRoute = '';
        }
      });

    // Definir rota inicial
    const url = this.router.url;
    if (url.startsWith('/app/')) {
      this.currentRoute = url.replace('/app/', '');
    }
  }

  onToggleCollapse() {
    this.toggleCollapse.emit();
  }

  isActive(route: string): boolean {
    if (route === 'home' && (this.currentRoute === '' || this.currentRoute === 'home')) {
      return true;
    }
    return this.currentRoute === route;
  }
}

