/** HTTP access to the Cinematica agent API. */

import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { QueryRequest, QueryResponse } from '../models/chat';

/**
 * Same-origin path, forwarded to the FastAPI backend by the dev-server
 * proxy declared in `proxy.conf.json`.
 */
const QUERY_PATH = '/query';

@Injectable({ providedIn: 'root' })
export class CinematicaApi {
  private readonly http = inject(HttpClient);

  /**
   * Asks the agent one natural-language question about the film graph.
   *
   * No client-side timeout is applied: a single answer crosses five
   * LangGraph stages, each its own Claude call, so 30-90s is the normal
   * range rather than a symptom of a hung request. Unsubscribing from
   * the returned observable aborts the request.
   *
   * @param question The natural-language question to ask.
   * @returns The question paired with the agent's answer.
   */
  query(question: string): Observable<QueryResponse> {
    const body: QueryRequest = { question };
    return this.http.post<QueryResponse>(QUERY_PATH, body);
  }
}
