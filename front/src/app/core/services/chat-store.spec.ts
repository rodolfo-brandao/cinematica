import { HttpErrorResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { Observable, Subject } from 'rxjs';

import { QueryResponse } from '../models/chat';
import { ChatStore } from './chat-store';
import { CinematicaApi } from './cinematica-api';

/** A CinematicaApi whose in-flight response the test drives by hand. */
class FakeApi {
  readonly questions: string[] = [];
  last = new Subject<QueryResponse>();

  query(question: string): Observable<QueryResponse> {
    this.questions.push(question);
    this.last = new Subject<QueryResponse>();
    return this.last.asObservable();
  }

  answer(text: string): void {
    this.last.next({ question: '', answer: text });
    this.last.complete();
  }

  fail(status: number): void {
    this.last.error(new HttpErrorResponse({ status }));
  }
}

describe('ChatStore', () => {
  let store: ChatStore;
  let api: FakeApi;

  beforeEach(() => {
    localStorage.clear();
    api = new FakeApi();
    TestBed.configureTestingModule({
      providers: [{ provide: CinematicaApi, useValue: api }],
    });
    store = TestBed.inject(ChatStore);
  });

  it('opens a thread and records the answer', () => {
    store.send('Who directed Arrival?');

    expect(store.isPending()).toBe(true);
    expect(store.threads().length).toBe(1);
    expect(store.messages().length).toBe(1);

    api.answer('Denis Villeneuve.');

    expect(store.isPending()).toBe(false);
    expect(store.messages().length).toBe(2);
    expect(store.messages()[1].content).toBe('Denis Villeneuve.');
    expect(store.threads()[0].title).toBe('Who directed Arrival?');
  });

  it('ignores a second question while one is in flight', () => {
    store.send('First?');
    store.send('Second?');

    expect(api.questions).toEqual(['First?']);
  });

  it('reports an unreachable API separately from an agent failure', () => {
    store.send('First?');
    api.fail(0);

    expect(store.messages()[1].failure).toBe('network');

    // The dev-server proxy reports a downed backend as 502, so a gateway
    // status has to read as unreachable rather than as an agent error.
    store.send('Second?');
    api.fail(502);

    expect(store.messages()[3].failure).toBe('network');

    store.send('Third?');
    api.fail(500);

    expect(store.messages()[5].failure).toBe('server');
  });

  it('re-asks the question behind a failed turn, replacing it', () => {
    store.send('Who directed Arrival?');
    api.fail(500);

    store.retry(store.messages()[1].id);

    expect(api.questions).toEqual([
      'Who directed Arrival?',
      'Who directed Arrival?',
    ]);
    expect(store.messages().length).toBe(1);

    api.answer('Denis Villeneuve.');

    expect(store.messages().length).toBe(2);
    expect(store.messages()[1].failure).toBeUndefined();
  });

  it('settles back to idle when the reader cancels', () => {
    store.send('Who directed Arrival?');
    store.cancel();

    expect(store.isPending()).toBe(false);
    expect(store.messages()[1].failure).toBe('cancelled');
  });

  it('restores saved threads on the next session', () => {
    store.send('Who directed Arrival?');
    api.answer('Denis Villeneuve.');
    TestBed.tick();

    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [{ provide: CinematicaApi, useValue: new FakeApi() }],
    });
    const restored = TestBed.inject(ChatStore);

    expect(restored.threads().length).toBe(1);
    expect(restored.messages().length).toBe(2);
  });
});
