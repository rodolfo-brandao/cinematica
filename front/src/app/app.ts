/** Application shell. */

import { ChangeDetectionStrategy, Component } from '@angular/core';

import { ChatPage } from './features/chat/chat-page/chat-page';

@Component({
  selector: 'app-root',
  imports: [ChatPage],
  template: '<app-chat-page />',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {}
