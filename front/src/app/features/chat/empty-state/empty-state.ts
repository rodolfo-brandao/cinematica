/** The opening screen of a conversation that has no turns yet. */

import { ChangeDetectionStrategy, Component, output } from '@angular/core';

import { SAMPLE_QUESTIONS } from '../sample-questions';

@Component({
  selector: 'app-empty-state',
  templateUrl: './empty-state.html',
  styleUrl: './empty-state.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EmptyState {
  readonly samples = SAMPLE_QUESTIONS;

  /** Emitted with the chosen question, to pre-fill the composer. */
  readonly select = output<string>();
}
