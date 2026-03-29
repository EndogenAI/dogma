// eslint.config.js — ESLint flat config for the MCP Dashboard frontend.
//
// Coverage layers:
//   1. eslint-plugin-svelte  — Svelte-specific rules including structural
//      a11y concerns (button-has-type, no-target-blank) and code quality.
//   2. @typescript-eslint/parser — TypeScript-aware parsing for .ts files
//      and <script lang="ts"> blocks.
//
// Note: The Svelte compiler's own a11y warnings (aria-*, role-*, label-*)
// are already surfaced by `npm run check` (svelte-check). ESLint covers
// the structural/static layer that the compiler doesn't reach.
//
// Run:  npm run lint
// Fix:  npm run lint:fix

import sveltePlugin from 'eslint-plugin-svelte';
import tsParser from '@typescript-eslint/parser';
import svelteParser from 'svelte-eslint-parser';

export default [
  // ── Ignore build artefacts ──────────────────────────────────────────────
  {
    ignores: ['dist/**', 'node_modules/**'],
  },

  // ── TypeScript source files ──────────────────────────────────────────────
  {
    files: ['src/**/*.ts'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        project: './tsconfig.json',
        extraFileExtensions: ['.svelte'],
      },
    },
    rules: {
      'no-console': 'warn',
      'no-debugger': 'error',
    },
  },

  // ── Svelte component files ───────────────────────────────────────────────
  {
    files: ['src/**/*.svelte'],
    plugins: { svelte: sveltePlugin },
    processor: sveltePlugin.processors['.svelte'],
    languageOptions: {
      parser: svelteParser,
      parserOptions: {
        parser: tsParser,
        project: './tsconfig.json',
        extraFileExtensions: ['.svelte'],
      },
    },
    rules: {
      // ── Structural a11y rules ──────────────────────────────────────────
      //
      // Buttons without an explicit type default to type="submit", which
      // causes unexpected form-submission behaviour and fails WCAG 4.1.2.
      'svelte/button-has-type': 'error',

      // rel="noopener" is added automatically by Svelte, but target="_blank"
      // without an aria-label can disorient screen-reader users.
      'svelte/no-target-blank': 'error',

      // Inline styles make it impossible for users to override contrast /
      // spacing via user stylesheets — WCAG 1.4.4 Resize Text.
      'svelte/no-inline-styles': 'warn',

      // Raw {@html ...} bypasses the template a11y analyser entirely.
      // Flag it so every use gets a deliberate review.
      'svelte/no-at-html-tags': 'warn',

      // ── Code correctness ──────────────────────────────────────────────
      'svelte/no-unused-svelte-ignore': 'error',
      'svelte/no-dupe-else-if-blocks': 'error',
      'svelte/no-useless-mustaches': 'warn',
      'svelte/require-each-key': 'error',
      'svelte/no-at-debug-tags': 'error',
      'svelte/infinite-reactive-loop': 'error',
      'svelte/no-reactive-reassign': ['error', { props: true }],

      // ── General JS rules inside .svelte scripts ───────────────────────
      'no-console': 'warn',
      'no-debugger': 'error',
    },
  },
];
