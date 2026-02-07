import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { SidebarComponent } from '../../components/sidebar/sidebar.component';
import { LogoComponent } from '../../components/logo/logo.component';
import { AuthService } from '../../services/auth.service';
import { ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, SidebarComponent, LogoComponent],
  templateUrl: './main-layout.component.html',
  styleUrl: './main-layout.component.scss'
})
export class MainLayoutComponent implements OnInit {
  sidebarCollapsed = false;
  sidebarMobileOpen = false;

  constructor(
    public authService: AuthService,
    public theme: ThemeService,
    private router: Router
  ) {}

  ngOnInit() {
    // Fechar sidebar no mobile quando navegar
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.sidebarMobileOpen = false;
      });
  }

  onToggleSidebar() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }

  onToggleMobileSidebar() {
    this.sidebarMobileOpen = !this.sidebarMobileOpen;
  }

  onCloseMobileSidebar() {
    this.sidebarMobileOpen = false;
  }

  onLogout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  onToggleTheme() {
    this.theme.toggle();
  }
}

