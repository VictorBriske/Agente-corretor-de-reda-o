import { Injectable } from '@angular/core';

export type ThemeMode = 'light' | 'dark';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private readonly storageKey = 'socratis-theme';

  private _mode: ThemeMode = 'light';

  get mode(): ThemeMode {
    return this._mode;
  }

  get isDark(): boolean {
    return this._mode === 'dark';
  }

  init(): void {
    // 1) Preferência salva
    const saved = (localStorage.getItem(this.storageKey) as ThemeMode | null);
    if (saved === 'light' || saved === 'dark') {
      this.setMode(saved, false);
      return;
    }

    // 2) Preferência do sistema
    const prefersDark = typeof window !== 'undefined'
      && window.matchMedia
      && window.matchMedia('(prefers-color-scheme: dark)').matches;

    this.setMode(prefersDark ? 'dark' : 'light', false);
  }

  toggle(): void {
    this.setMode(this.isDark ? 'light' : 'dark', true);
  }

  setMode(mode: ThemeMode, persist: boolean = true): void {
    this._mode = mode;

    const root = document.documentElement;
    root.setAttribute('data-theme', mode);

    // Ajuda o navegador com form controls/scrollbar
    root.style.colorScheme = mode;

    if (persist) {
      localStorage.setItem(this.storageKey, mode);
    }
  }
}


