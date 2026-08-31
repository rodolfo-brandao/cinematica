/** The conversation history rail. */

import {
  ChangeDetectionStrategy,
  Component,
  inject,
  input,
  output,
} from '@angular/core';

import { ChatThread } from '../../../core/models/chat';
import { ThemeService } from '../../../core/services/theme';

@Component({
  selector: 'app-thread-sidebar',
  templateUrl: './thread-sidebar.html',
  styleUrl: './thread-sidebar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ThreadSidebar {
  readonly threads = input.required<readonly ChatThread[]>();
  readonly activeThreadId = input.required<string | null>();

  /** Locks navigation while a request is in flight, which would orphan it. */
  readonly disabled = input.required<boolean>();

  readonly create = output<void>();
  readonly select = output<string>();
  readonly remove = output<string>();

  private readonly themeService = inject(ThemeService);

  readonly theme = this.themeService.theme;

  /** Flips between the light and dark palettes. */
  toggleTheme(): void {
    this.themeService.toggle();
  }
}
