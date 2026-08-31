/** The waiting state shown while the agent works on a question. */

import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  signal,
} from '@angular/core';

const TICK_INTERVAL_MS = 1000;

/**
 * How long a question usually takes. Past this, the wait is worth
 * reassuring the reader about rather than leaving unexplained.
 */
const LONG_WAIT_SECONDS = 45;

@Component({
  selector: 'app-thinking-indicator',
  templateUrl: './thinking-indicator.html',
  styleUrl: './thinking-indicator.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ThinkingIndicator implements OnDestroy {
  /**
   * Seconds spent waiting. Elapsed time is deliberately the only
   * progress reported: the API answers in a single response, so the
   * client cannot know which pipeline stage is running, and inventing a
   * stage-by-stage progress bar would be fiction.
   */
  readonly elapsed = signal(0);

  readonly isLongWait = () => this.elapsed() >= LONG_WAIT_SECONDS;

  private readonly timer = setInterval(
    () => this.elapsed.update((seconds) => seconds + 1),
    TICK_INTERVAL_MS,
  );

  ngOnDestroy(): void {
    clearInterval(this.timer);
  }
}
