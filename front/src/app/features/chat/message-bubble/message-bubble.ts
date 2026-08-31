/** One turn in a thread: a question, an answer, or a failed attempt. */

import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  input,
  output,
} from '@angular/core';

import { ChatMessage, MessageFailure } from '../../../core/models/chat';
import { Markdown } from '../../../core/services/markdown';

/** What to tell the reader for each way an answer can fail to arrive. */
const FAILURE_MESSAGES: Record<MessageFailure, string> = {
  network:
    'Could not reach the Cinematica API. Check that the backend is ' +
    'running on port 8000.',
  server:
    'The agent failed while answering. This is usually a transient ' +
    'error from the graph or the model API.',
  cancelled: 'Request cancelled.',
};

@Component({
  selector: 'app-message-bubble',
  templateUrl: './message-bubble.html',
  styleUrl: './message-bubble.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MessageBubble {
  readonly message = input.required<ChatMessage>();

  /** Emitted with the message id when the reader asks to try again. */
  readonly retry = output<string>();

  private readonly markdown = inject(Markdown);

  readonly isUser = computed(() => this.message().role === 'user');
  readonly failure = computed(() => this.message().failure ?? null);

  readonly failureText = computed(() => {
    const failure = this.failure();
    return failure ? FAILURE_MESSAGES[failure] : '';
  });

  /**
   * The answer as sanitized HTML. Questions are rendered as plain text
   * instead, since they are the reader's own input and carry no Markdown
   * worth interpreting.
   */
  readonly html = computed(() => this.markdown.render(this.message().content));
}
