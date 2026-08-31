/** The question input pinned to the bottom of a thread. */

import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  input,
  model,
  output,
  viewChild,
} from '@angular/core';

/** Ceiling for the auto-growing textarea, in pixels. */
const MAX_TEXTAREA_HEIGHT = 200;

@Component({
  selector: 'app-composer',
  templateUrl: './composer.html',
  styleUrl: './composer.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Composer {
  /** The draft question, shared two-way with the page. */
  readonly value = model.required<string>();

  /** Whether a request is in flight, which swaps send for cancel. */
  readonly pending = input.required<boolean>();

  /** Emitted when the reader submits the draft. */
  readonly send = output<void>();

  /** Emitted when the reader aborts the in-flight request. */
  readonly cancel = output<void>();

  private readonly textarea =
    viewChild.required<ElementRef<HTMLTextAreaElement>>('input');

  /** Moves the caret into the textarea, sizing it to any preset draft. */
  focus(): void {
    const element = this.textarea().nativeElement;
    element.focus();
    this.resize(element);
  }

  /** Mirrors typing into `value` and keeps the textarea sized to it. */
  onInput(event: Event): void {
    const element = event.target as HTMLTextAreaElement;
    this.value.set(element.value);
    this.resize(element);
  }

  /** Sends on Enter, reserving Shift+Enter for a literal line break. */
  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.submit();
    }
  }

  /** Emits the draft, unless it is blank or a request is already running. */
  submit(): void {
    if (this.pending() || !this.value().trim()) {
      return;
    }

    this.send.emit();
    this.resize(this.textarea().nativeElement);
  }

  /** Grows the textarea with its content, up to a fixed ceiling. */
  private resize(element: HTMLTextAreaElement): void {
    element.style.height = 'auto';
    element.style.height = `${Math.min(
      element.scrollHeight,
      MAX_TEXTAREA_HEIGHT,
    )}px`;
  }
}
