/** Domain types for the chat feature and the Cinematica API contract. */

/**
 * The request body accepted by `POST /query`.
 * Mirrors `QueryRequest` in `src/models/agent.py`.
 */
export interface QueryRequest {
  readonly question: string;
}

/**
 * The response body returned by `POST /query`.
 * Mirrors `QueryResponse` in `src/models/agent.py`.
 */
export interface QueryResponse {
  readonly question: string;
  readonly answer: string;
}

/** Who authored a message within a thread. */
export type MessageRole = 'user' | 'assistant';

/**
 * Why an assistant turn produced no answer. `network` means the API was
 * unreachable (typically `make api` is not running), `server` means the
 * agent itself failed, and `cancelled` means the user aborted the wait.
 */
export type MessageFailure = 'network' | 'server' | 'cancelled';

/** A single turn in a thread. */
export interface ChatMessage {
  readonly id: string;
  readonly role: MessageRole;
  readonly content: string;
  readonly createdAt: number;
  /** Present only on assistant turns that did not produce an answer. */
  readonly failure?: MessageFailure;
}

/**
 * A saved conversation. Threads exist purely for the user's own history:
 * the agent is stateless, so every question is sent to `/query` on its
 * own, without the preceding turns.
 */
export interface ChatThread {
  readonly id: string;
  readonly title: string;
  readonly messages: readonly ChatMessage[];
  readonly updatedAt: number;
}
