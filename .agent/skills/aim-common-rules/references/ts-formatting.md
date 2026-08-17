# TypeScript Formatting

> Source of truth: [`standard.ts.md`](https://github.com/unnc-aim/.github/blob/main/profile/standard.ts.md) in `unnc-aim/.github`. One-line rule: **format with Prettier (2-space indent) before committing; use pnpm as the package manager.**

## 1. Tool: Prettier

Prettier owns all formatting. Indentation is **2 spaces** (Prettier's default) — no tabs.

### Editor integration

- VS Code: install `esbenp.prettier-vscode`, enable **Format On Save**, and set Prettier as the default formatter for TypeScript (the skill's `assets/.vscode/settings.json` already does this).
- Any other editor: fall back to the CLI below and format before committing.

### Command line

```bash
pnpm add -D prettier
pnpm exec prettier --write .   # format everything
pnpm exec prettier --check .   # CI / pre-commit check
```

---

## 2. Package manager: pnpm

- All TypeScript / JavaScript projects use **pnpm**, except in special cases.
- One-time setup per machine: `corepack enable pnpm`.
- Pin in `package.json`: `"packageManager": "pnpm@x.y.z"` (a concrete version).
- Commit `pnpm-lock.yaml`.

---

## 3. Lint: typescript-eslint

ESLint owns code quality; Prettier owns formatting — do not duplicate formatting rules in ESLint.

```bash
pnpm add -D eslint @eslint/js typescript-eslint
pnpm exec eslint .
```

---

## 4. Canonical config (copy & use)

- [`assets/.prettierrc`](../assets/.prettierrc) — Prettier defaults made explicit; pins `tabWidth: 2`. Copy to the repo root.
- [`assets/eslint.config.js`](../assets/eslint.config.js) — minimal flat config (`@eslint/js` + `typescript-eslint` recommended). Copy to the repo root.

---

## 5. CI

```yaml
- run: corepack enable pnpm
- run: pnpm install --frozen-lockfile
- run: pnpm exec prettier --check .
- run: pnpm exec eslint .
```
