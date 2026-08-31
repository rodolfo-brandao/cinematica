/** Application state for the chat: threads, selection and the in-flight ask. */

import { HttpErrorResponse } from '@angular/common/http';
import { Injectable, computed, effect, inject, signal } from '@angular/core';
import { Subscription } from 'rxjs';

import {
  ChatMessage,
  ChatThread,
  MessageFailure,
  MessageRole,
} from '../models/chat';
import { CinematicaApi } from './cinematica-api';
import { ThreadStorage } from './thread-storage';

/** How much of the opening question becomes the thread's sidebar title. */
const MAX_TITLE_LENGTH = 48;

@Injectable({ providedIn: 'root' })
export class ChatStore {
  private readonly api = inject(CinematicaApi);
  private readonly storage = inject(ThreadStorage);

  private readonly threadList = signal<readonly ChatThread[]>(
    this.storage.load(),
  );
  private readonly selectedId = signal<string | null>(null);
  private readonly pending = signal(false);

  /** The in-flight request, kept so it can be aborted by `cancel`. */
  private subscription: Subscription | null = null;

  readonly threads = this.threadList.asReadonly();
  readonly activeThreadId = this.selectedId.asReadonly();
  readonly isPending = this.pending.asReadonly();

  readonly activeThread = computed<ChatThread | null>(
    () =>
      this.threadList().find((thread) => thread.id === this.selectedId()) ??
      null,
  );
  readonly messages = computed<readonly ChatMessage[]>(
    () => this.activeThread()?.messages ?? [],
  );

  constructor() {
    // Reopen on the most recent conversation, so a reload resumes where
    // the reader left off rather than discarding visible context.
    this.selectedId.set(this.threadList()[0]?.id ?? null);
    effect(() => this.storage.save(this.threadList()));
  }

  /**
   * Sends a question to the agent, opening a thread when none is active.
   *
   * Ignored while a request is already in flight: the endpoint is
   * stateless and single-turn, so overlapping asks would race for the
   * same thread.
   *
   * @param question The natural-language question to ask.
   */
  send(question: string): void {
    const trimmed = question.trim();

    if (!trimmed || this.pending()) {
      return;
    }

    const threadId = this.ensureActiveThread(trimmed);
    this.appendMessage(threadId, this.createMessage('user', trimmed));
    this.ask(threadId, trimmed);
  }

  /**
   * Re-asks the question that produced a failed assistant turn, dropping
   * that turn first so the retry replaces it instead of stacking below.
   *
   * @param messageId The id of the failed assistant message.
   */
  retry(messageId: string): void {
    const thread = this.activeThread();

    if (!thread || this.pending()) {
      return;
    }

    const index = thread.messages.findIndex(
      (message) => message.id === messageId,
    );
    const question = index > 0 ? thread.messages[index - 1] : null;

    if (!question || question.role !== 'user') {
      return;
    }

    this.updateThread(thread.id, (current) => ({
      ...current,
      messages: current.messages.filter(
        (message) => message.id !== messageId,
      ),
    }));
    this.ask(thread.id, question.content);
  }

  /** Aborts the in-flight request, leaving the thread ready for a new ask. */
  cancel(): void {
    if (!this.pending()) {
      return;
    }

    this.subscription?.unsubscribe();
    const threadId = this.selectedId();

    if (threadId) {
      this.appendMessage(threadId, this.createFailedMessage('cancelled'));
    }

    this.settle();
  }

  /** Clears the selection, so the composer opens a fresh conversation. */
  newThread(): void {
    if (this.pending()) {
      return;
    }

    this.selectedId.set(null);
  }

  /**
   * Switches to an existing conversation.
   *
   * @param threadId The id of the thread to open.
   */
  selectThread(threadId: string): void {
    if (this.pending()) {
      return;
    }

    this.selectedId.set(threadId);
  }

  /**
   * Removes a conversation from the history.
   *
   * @param threadId The id of the thread to delete.
   */
  deleteThread(threadId: string): void {
    if (this.pending()) {
      return;
    }

    this.threadList.update((threads) =>
      threads.filter((thread) => thread.id !== threadId),
    );

    if (this.selectedId() === threadId) {
      this.selectedId.set(null);
    }
  }

  /** Issues the request and wires its outcome back into the thread. */
  private ask(threadId: string, question: string): void {
    this.pending.set(true);
    this.subscription = this.api.query(question).subscribe({
      next: (response) => {
        this.appendMessage(
          threadId,
          this.createMessage('assistant', response.answer),
        );
        this.settle();
      },
      error: (error: unknown) => {
        this.appendMessage(threadId, this.createFailedMessage(classify(error)));
        this.settle();
      },
    });
  }

  /** Marks the request finished and drops the retained subscription. */
  private settle(): void {
    this.subscription = null;
    this.pending.set(false);
  }

  /** Returns the active thread's id, creating the thread when needed. */
  private ensureActiveThread(question: string): string {
    const active = this.selectedId();

    if (active) {
      return active;
    }

    const thread: ChatThread = {
      id: crypto.randomUUID(),
      title: toTitle(question),
      messages: [],
      updatedAt: Date.now(),
    };
    this.threadList.update((threads) => [thread, ...threads]);
    this.selectedId.set(thread.id);

    return thread.id;
  }

  /** Appends a message and floats its thread to the top of the history. */
  private appendMessage(threadId: string, message: ChatMessage): void {
    this.updateThread(threadId, (thread) => ({
      ...thread,
      messages: [...thread.messages, message],
      updatedAt: message.createdAt,
    }));
  }

  /** Applies `change` to one thread and re-sorts the history by recency. */
  private updateThread(
    threadId: string,
    change: (thread: ChatThread) => ChatThread,
  ): void {
    this.threadList.update((threads) =>
      threads
        .map((thread) => (thread.id === threadId ? change(thread) : thread))
        .sort((left, right) => right.updatedAt - left.updatedAt),
    );
  }

  /** Builds a message carrying content. */
  private createMessage(role: MessageRole, content: string): ChatMessage {
    return {
      id: crypto.randomUUID(),
      role,
      content,
      createdAt: Date.now(),
    };
  }

  /** Builds an assistant turn that produced no answer. */
  private createFailedMessage(failure: MessageFailure): ChatMessage {
    return {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
      createdAt: Date.now(),
      failure,
    };
  }
}

/**
 * Statuses that mean the request never reached the agent. Status 0 is a
 * connection refused outright by the browser; the gateway statuses are
 * what a proxy in front of the API reports when the backend is down —
 * the dev-server proxy answers 502 when `make api` is not running, so
 * this is the common development case rather than an edge one.
 */
const UNREACHABLE_STATUSES = new Set([0, 502, 503, 504]);

/** Separates an unreachable API from a failure inside the agent itself. */
function classify(error: unknown): MessageFailure {
  return error instanceof HttpErrorResponse &&
    UNREACHABLE_STATUSES.has(error.status)
    ? 'network'
    : 'server';
}

/** Condenses a question into a sidebar-sized thread title. */
function toTitle(question: string): string {
  const collapsed = question.replace(/\s+/g, ' ').trim();

  return collapsed.length > MAX_TITLE_LENGTH
    ? `${collapsed.slice(0, MAX_TITLE_LENGTH).trimEnd()}…`
    : collapsed;
}
