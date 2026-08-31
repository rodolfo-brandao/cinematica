import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { CinematicaApi } from './cinematica-api';

describe('CinematicaApi', () => {
  let api: CinematicaApi;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(CinematicaApi);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('posts the question to the proxied /query path', () => {
    let received: string | null = null;
    api.query('Who directed Arrival?').subscribe((response) => {
      received = response.answer;
    });

    const request = httpMock.expectOne('/query');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      question: 'Who directed Arrival?',
    });

    request.flush({
      question: 'Who directed Arrival?',
      answer: 'Denis Villeneuve.',
    });

    expect(received).toBe('Denis Villeneuve.');
  });

  it('aborts the request when the caller unsubscribes', () => {
    const subscription = api.query('Anything?').subscribe();
    const request = httpMock.expectOne('/query');

    subscription.unsubscribe();

    expect(request.cancelled).toBe(true);
  });
});
