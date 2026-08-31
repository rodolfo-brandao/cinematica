/** Rendering of the agent's Markdown answers into safe HTML. */

import { Injectable } from '@angular/core';
import DOMPurify from 'dompurify';
import { marked } from 'marked';

/**
 * Sends links to a new tab without handing the opened page a reference
 * back to this one.
 */
DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  if (node instanceof HTMLAnchorElement && node.hasAttribute('href')) {
    node.setAttribute('target', '_blank');
    node.setAttribute('rel', 'noopener noreferrer');
  }
});

@Injectable({ providedIn: 'root' })
export class Markdown {
  /**
   * Converts an answer's Markdown into sanitized HTML.
   *
   * The result is bound with `[innerHTML]`, which runs Angular's own
   * sanitizer over it as well; the two passes are deliberate, since the
   * text originates from a model rather than from this codebase.
   *
   * @param source The Markdown text to render.
   * @returns Sanitized HTML, safe to bind into the DOM.
   */
  render(source: string): string {
    const html = marked.parse(source, { async: false, gfm: true });
    return DOMPurify.sanitize(html);
  }
}
