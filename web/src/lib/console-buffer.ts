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

let initialized = false;
let maxEntries = DEFAULT_MAX_ENTRIES;
let counter = 0;

const entries: ConsoleEntry[] = [];

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function truncate(value: string, limit = MAX_STRING_LENGTH): string {
  if (value.length <= limit) return value;
  return `${value.slice(0, limit - 1)}...`;
}

function safeStringify(value: unknown): string {
  if (typeof value === 'string') {
    return truncate(value);
  }

  if (value instanceof Error) {
    return truncate(value.stack ?? `${value.name}: ${value.message}`);
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
        JSON.stringify(value, (_, inner: unknown) => {
          if (typeof inner === 'function') return '[function]';
          if (typeof inner === 'bigint') return String(inner);
          if (inner && typeof inner === 'object') {
            if (seen.has(inner as object)) return '[circular]';
            seen.add(inner as object);
          }
          return inner;
        })
      );
    } catch {
      return '[unserializable object]';
    }
  }

  return truncate(String(value));
}

function appendEntry(level: ConsoleLevel, args: unknown[]): void {
  const normalizedArgs = args.map((arg) => safeStringify(arg));
  const message = truncate(normalizedArgs.join(' '));

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
}

export function installConsoleBuffer(
  options: ConsoleBufferOptions = {}
): ConsoleBufferApi {
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