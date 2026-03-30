/**
 * console-buffer.ts
 *
 * Purpose:
 * - Capture browser console activity into a bounded in-memory ring-like buffer.
 * - Provide filtered read access for MCP inspector tools.
 */

export type ConsoleLevel = 'debug' | 'info' | 'log' | 'warn' | 'error';

export type ConsoleEntry = {
  id: number;
  timestamp: string;
  level: ConsoleLevel;
  message: string;
  args: string[];
};

export type ConsoleBufferApi = {
  getEntries: (level?: ConsoleLevel) => ConsoleEntry[];
  clear: () => void;
};

export type ConsoleBufferOptions = {
  maxEntries?: number;
};

const DEFAULT_MAX_ENTRIES = 250;
const MAX_ALLOWED_ENTRIES = 1000;
const MAX_STRING_LENGTH = 400;
const REDACTION_PATTERNS: RegExp[] = [
  /Bearer\s+[A-Za-z0-9._\-]+/gi,
  /github_pat_[A-Za-z0-9_]+/g,
  /\bsk-[A-Za-z0-9]+\b/g,
];
const CONSOLE_BUFFER_STATE_KEY = Symbol.for('dogma.consoleBuffer.state');

type SharedConsoleBufferState = {
  initialized: boolean;
  maxEntries: number;
  counter: number;
  entries: ConsoleEntry[];
};

function getSharedState(): SharedConsoleBufferState {
  const globalScope = globalThis as typeof globalThis & {
    [CONSOLE_BUFFER_STATE_KEY]?: SharedConsoleBufferState;
  };

  if (!globalScope[CONSOLE_BUFFER_STATE_KEY]) {
    globalScope[CONSOLE_BUFFER_STATE_KEY] = {
      initialized: false,
      maxEntries: DEFAULT_MAX_ENTRIES,
      counter: 0,
      entries: [],
    };
  }

  return globalScope[CONSOLE_BUFFER_STATE_KEY] as SharedConsoleBufferState;
}

const sharedState = getSharedState();

let initialized = sharedState.initialized;
let maxEntries = sharedState.maxEntries;
let counter = sharedState.counter;

const entries: ConsoleEntry[] = sharedState.entries;

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function truncate(value: string, limit = MAX_STRING_LENGTH): string {
  if (value.length <= limit) return value;
  return `${value.slice(0, limit - 1)}...`;
}

function redactSecrets(value: string): string {
  let redacted = value;
  for (const pattern of REDACTION_PATTERNS) {
    redacted = redacted.replace(pattern, '[REDACTED]');
  }
  return redacted;
}

function safeStringify(value: unknown): string {
  if (typeof value === 'string') {
    return truncate(redactSecrets(value));
  }

  if (value instanceof Error) {
    return truncate(redactSecrets(value.stack ?? `${value.name}: ${value.message}`));
  }

  if (value === null || value === undefined) {
    return String(value);
  }

  if (typeof value === 'function') {
    return '[function]';
  }

  if (typeof value === 'object') {
    const seen = new WeakSet<object>();
    try {
      return truncate(
        redactSecrets(
          JSON.stringify(value, (_, inner: unknown) => {
          if (typeof inner === 'function') return '[function]';
          if (typeof inner === 'bigint') return String(inner);
          if (inner && typeof inner === 'object') {
            if (seen.has(inner as object)) return '[circular]';
            seen.add(inner as object);
          }
          return inner;
          })
        )
      );
    } catch {
      return '[unserializable object]';
    }
  }

  return truncate(String(value));
}

function appendEntry(level: ConsoleLevel, args: unknown[]): void {
  // Redact + normalize captured args before exposing them through inspector tools.
  const normalizedArgs = args.map((arg) => safeStringify(arg));
  const message = truncate(redactSecrets(normalizedArgs.join(' ')));

  entries.push({
    id: ++counter,
    timestamp: new Date().toISOString(),
    level,
    message,
    args: normalizedArgs,
  });

  const overflow = entries.length - maxEntries;
  if (overflow > 0) {
    entries.splice(0, overflow);
  }
}

function initConsoleBuffer(options: ConsoleBufferOptions = {}): void {
  // Guard against duplicate wrapping under Vite HMR/module reloads.
  if (initialized) return;

  maxEntries = clamp(
    options.maxEntries ?? DEFAULT_MAX_ENTRIES,
    10,
    MAX_ALLOWED_ENTRIES
  );

  const levels: ConsoleLevel[] = ['debug', 'info', 'log', 'warn', 'error'];

  for (const level of levels) {
    const original = console[level].bind(console) as (...data: unknown[]) => void;

    console[level] = ((...args: unknown[]) => {
      appendEntry(level, args);
      original(...args);
    }) as typeof console[typeof level];
  }

  initialized = true;
  sharedState.initialized = true;
  sharedState.maxEntries = maxEntries;
}

export function installConsoleBuffer(
  options: ConsoleBufferOptions = {}
): ConsoleBufferApi {
  // Install once globally and return read/clear helpers for callers.
  initConsoleBuffer(options);

  return {
    getEntries(level?: ConsoleLevel): ConsoleEntry[] {
      if (!level) return [...entries];
      return entries.filter((entry) => entry.level === level);
    },
    clear(): void {
      entries.length = 0;
    },
  };
}