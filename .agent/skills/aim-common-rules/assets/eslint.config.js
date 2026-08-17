// ESLint flat config for TypeScript projects.
// Division of labor: ESLint owns code quality, Prettier owns formatting
// (see .prettierrc in the same directory) — do not add formatting rules here.
// Dev dependencies: pnpm add -D eslint @eslint/js typescript-eslint
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
);
