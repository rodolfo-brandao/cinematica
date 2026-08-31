/** Light/dark theme selection, persisted across sessions. */

import { Injectable, effect, signal } from '@angular/core';

const STORAGE_KEY = 'cinematica.theme';

/** The themes a reader can pick between. */
export type Theme = 'light' | 'dark';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly current = signal<Theme>(readStoredTheme() ?? systemTheme());

  readonly theme = this.current.asReadonly();

  constructor() {
    effect(() => {
      const theme = this.current();
      document.documentElement.dataset['theme'] = theme;

      try {
        localStorage.setItem(STORAGE_KEY, theme);
      } catch {
        // Storage blocked; the choice simply will not outlive the tab.
      }
    });
  }

  /** Switches to the other theme. */
  toggle(): void {
    this.current.update((theme) => (theme === 'dark' ? 'light' : 'dark'));
  }
}

/** Reads a previously chosen theme, ignoring anything unrecognized. */
function readStoredTheme(): Theme | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'light' || stored === 'dark' ? stored : null;
  } catch {
    return null;
  }
}

/** Falls back to the operating system's own preference. */
function systemTheme(): Theme {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';
}
