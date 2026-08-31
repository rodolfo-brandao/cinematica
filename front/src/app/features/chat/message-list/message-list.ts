/** The scrolling transcript of the active thread. */

import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  afterRenderEffect,
  input,
  output,
  viewChild,
} from '@angular/core';

import { ChatMessage } from '../../../core/models/chat';
import { MessageBubble } from '../message-bubble/message-bubble';
import { ThinkingIndicator } from '../thinking-indicator/thinking-indicator';

/**
 * How close to the bottom counts as "following along". Beyond this, the
 * reader has scrolled up deliberately and should not be yanked back down
 * when an answer lands.
 */
const STICKY_THRESHOLD_PX = 120;

@Component({
  selector: 'app-message-list',
  imports: [MessageBubble, ThinkingIndicator],
  templateUrl: './message-list.html',
  styleUrl: './message-list.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MessageList {
  readonly messages = input.required<readonly ChatMessage[]>();
  readonly pending = input.required<boolean>();

  /** Re-emitted from a failed turn's retry button. */
  readonly retry = output<string>();

  private readonly scroller =
    viewChild.required<ElementRef<HTMLElement>>('scroller');

  /** Whether the reader was at the bottom before the latest render. */
  private wasAtBottom = true;

  constructor() {
    afterRenderEffect(() => {
      // Tracked so the transcript follows new turns and the waiting
      // indicator as they appear.
      this.messages();
      this.pending();

      const element = this.scroller().nativeElement;

      if (this.wasAtBottom) {
        element.scrollTop = element.scrollHeight;
      }

      this.wasAtBottom = isAtBottom(element);
    });
  }

  /** Re-evaluates stickiness as the reader scrolls by hand. */
  onScroll(): void {
    this.wasAtBottom = isAtBottom(this.scroller().nativeElement);
  }
}

/** Whether an element is scrolled to (or very near) its bottom. */
function isAtBottom(element: HTMLElement): boolean {
  const distance =
    element.scrollHeight - element.scrollTop - element.clientHeight;

  return distance <= STICKY_THRESHOLD_PX;
}
