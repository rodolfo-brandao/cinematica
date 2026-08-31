/** The chat screen: history rail, transcript and composer. */

import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
  viewChild,
} from '@angular/core';

import { ChatStore } from '../../../core/services/chat-store';
import { Composer } from '../composer/composer';
import { EmptyState } from '../empty-state/empty-state';
import { MessageList } from '../message-list/message-list';
import { ThreadSidebar } from '../thread-sidebar/thread-sidebar';

@Component({
  selector: 'app-chat-page',
  imports: [Composer, EmptyState, MessageList, ThreadSidebar],
  templateUrl: './chat-page.html',
  styleUrl: './chat-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatPage {
  private readonly store = inject(ChatStore);

  readonly threads = this.store.threads;
  readonly activeThreadId = this.store.activeThreadId;
  readonly messages = this.store.messages;
  readonly isPending = this.store.isPending;

  /** The question being typed, shared two-way with the composer. */
  readonly draft = signal('');

  /** Whether the history rail is open over the transcript on narrow screens. */
  readonly isSidebarOpen = signal(false);

  private readonly composer = viewChild.required(Composer);

  /** Sends the draft and clears it, keeping the caret ready for the next one. */
  send(): void {
    this.store.send(this.draft());
    this.draft.set('');
  }

  cancel(): void {
    this.store.cancel();
  }

  retry(messageId: string): void {
    this.store.retry(messageId);
  }

  /** Drops a sample question into the composer for the reader to edit or send. */
  useSample(question: string): void {
    this.draft.set(question);
    this.composer().focus();
  }

  createThread(): void {
    this.store.newThread();
    this.draft.set('');
    this.closeSidebar();
  }

  selectThread(threadId: string): void {
    this.store.selectThread(threadId);
    this.closeSidebar();
  }

  deleteThread(threadId: string): void {
    this.store.deleteThread(threadId);
  }

  toggleSidebar(): void {
    this.isSidebarOpen.update((open) => !open);
  }

  closeSidebar(): void {
    this.isSidebarOpen.set(false);
  }
}
