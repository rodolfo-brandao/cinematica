# Cinematica Front-end

Angular chat interface for the Cinematica agent API.

## Running

The API must be running first (`make api` from the repository root, on
port 8000). Then, from the repository root:

```bash
make front
```

The app is served at `http://localhost:4200`. Requests to `/query` are
forwarded to the API by the dev-server proxy in
[`proxy.conf.json`](proxy.conf.json), so the backend needs no CORS
configuration and the front-end needs no base URL.

## Layout

```
src/app/
├── core/
│   ├── models/chat.ts        # API contract + chat domain types
│   └── services/
│       ├── cinematica-api.ts # The only HTTP access to POST /query
│       ├── chat-store.ts     # Threads, selection, the in-flight ask
│       ├── thread-storage.ts # Conversation history in local storage
│       ├── markdown.ts       # Answer Markdown -> sanitized HTML
│       └── theme.ts          # Light/dark selection
└── features/chat/            # Chat page and its components
```

## Two constraints worth knowing

**Answers are slow.** A question crosses five LangGraph stages, each its
own Claude call, plus a tool loop and up to three query retries — 30-90
seconds is normal. The proxy timeouts are set accordingly, and the UI
shows elapsed time with a cancel button rather than a progress bar: the
API answers in a single response, so the client cannot know which stage
is running.

**The agent is stateless.** `POST /query` takes one question and reads
none of the preceding turns. The sidebar's conversations are a local
history for the reader's benefit only; each question is still sent on
its own.

## Commands

| Command | Purpose |
| --- | --- |
| `npm start` | Dev server with the API proxy |
| `npm run build` | Production build into `dist/` |
| `npm test` | Unit tests (Vitest) |

Conventions for this codebase live in
[`.claude/rules/front-writing.md`](../.claude/rules/front-writing.md).
