/** Persistence of chat threads in the browser's local storage. */

import { Injectable } from '@angular/core';

import { ChatMessage, ChatThread } from '../models/chat';

const STORAGE_KEY = 'cinematica.threads';

/**
 * Caps what is written back, so a long-lived history can never grow past
 * the ~5MB local-storage quota and start throwing on every save.
 */
const MAX_STORED_THREADS = 50;

@Injectable({ providedIn: 'root' })
export class ThreadStorage {
  /**
   * Reads the saved threads, most recently updated first.
   *
   * Every access is guarded: local storage throws outright in some
   * privacy modes, and the stored payload is user-editable, so anything
   * unreadable or malformed degrades to an empty history rather than
   * breaking the app on boot.
   *
   * @returns The saved threads, or an empty list when unavailable.
   */
  load(): readonly ChatThread[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);

      if (!raw) {
        return [];
      }

      const parsed: unknown = JSON.parse(raw);

      if (!Array.isArray(parsed)) {
        return [];
      }

      return parsed
        .filter(isChatThread)
        .sort((left, right) => right.updatedAt - left.updatedAt);
    } catch {
      return [];
    }
  }

  /**
   * Writes the threads back, silently giving up when storage is
   * unavailable — losing history is preferable to breaking a session.
   *
   * @param threads The threads to persist.
   */
  save(threads: readonly ChatThread[]): void {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(threads.slice(0, MAX_STORED_THREADS)),
      );
    } catch {
      // Quota exceeded or storage blocked; history is best-effort.
    }
  }
}

/** Narrows an unknown parsed value to a usable `ChatThread`. */
function isChatThread(value: unknown): value is ChatThread {
  if (typeof value !== 'object' || value === null) {
    return false;
  }

  const candidate = value as Partial<ChatThread>;

  return (
    typeof candidate.id === 'string' &&
    typeof candidate.title === 'string' &&
    typeof candidate.updatedAt === 'number' &&
    Array.isArray(candidate.messages) &&
    candidate.messages.every(isChatMessage)
  );
}

/** Narrows an unknown parsed value to a usable `ChatMessage`. */
function isChatMessage(value: unknown): value is ChatMessage {
  if (typeof value !== 'object' || value === null) {
    return false;
  }

  const candidate = value as Partial<ChatMessage>;

  return (
    typeof candidate.id === 'string' &&
    (candidate.role === 'user' || candidate.role === 'assistant') &&
    typeof candidate.content === 'string' &&
    typeof candidate.createdAt === 'number'
  );
}
