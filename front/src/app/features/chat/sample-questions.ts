/** Starter questions shown on the empty state. */

/** A suggested question, labelled by the kind of reasoning it exercises. */
export interface SampleQuestion {
  readonly kind: string;
  readonly question: string;
}

/**
 * One question per capability the agent actually has, mirroring the
 * taxonomy its planning stage classifies against (multi-hop, analytical,
 * thematic) plus the on-demand TMDb ingestion path.
 */
export const SAMPLE_QUESTIONS: readonly SampleQuestion[] = [
  {
    kind: 'Multi-hop',
    question:
      'Which cinematographers have worked with both Denis Villeneuve ' +
      'and Christopher Nolan?',
  },
  {
    kind: 'Analytical',
    question:
      'What are the ten highest-rated science fiction movies with at ' +
      'least 50,000 IMDb votes?',
  },
  {
    kind: 'Thematic',
    question:
      'Find movies about memory, grief and the passage of time.',
  },
  {
    kind: 'Audience sentiment',
    question: 'How did audiences react to Dune: Part Two?',
  },
];
