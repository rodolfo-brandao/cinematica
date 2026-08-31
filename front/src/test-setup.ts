/**
 * Fills in the browser APIs the test environment does not implement.
 *
 * jsdom ships no `matchMedia`, and the `localStorage` exposed to the
 * runner is a partial stub. Both are real, fully supported APIs in every
 * browser the app targets, so they are polyfilled here rather than
 * worked around in the services themselves.
 */

if (typeof window.matchMedia !== 'function') {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: string): MediaQueryList =>
      ({
        matches: false,
        media: query,
        onchange: null,
        addEventListener: () => undefined,
        removeEventListener: () => undefined,
        addListener: () => undefined,
        removeListener: () => undefined,
        dispatchEvent: () => false,
      }) as unknown as MediaQueryList,
  });
}

if (typeof globalThis.localStorage?.clear !== 'function') {
  const entries = new Map<string, string>();

  Object.defineProperty(globalThis, 'localStorage', {
    configurable: true,
    value: {
      get length(): number {
        return entries.size;
      },
      key: (index: number): string | null =>
        [...entries.keys()][index] ?? null,
      getItem: (key: string): string | null => entries.get(key) ?? null,
      setItem: (key: string, value: string): void => {
        entries.set(key, String(value));
      },
      removeItem: (key: string): void => {
        entries.delete(key);
      },
      clear: (): void => entries.clear(),
    } satisfies Storage,
  });
}
