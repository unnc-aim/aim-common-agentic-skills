# Docs Style (Markdown / YAML / JSON)

> Source of truth: [`standard.docs.md`](https://github.com/unnc-aim/.github/blob/main/profile/standard.docs.md) in `unnc-aim/.github`. One-line rule: **2-space indent in YAML and JSON; every Markdown code fence declares its language.**

## 1. YAML

- **2-space** indent, **tabs forbidden** (tabs are invalid in YAML).
- Quote strings only when necessary; keep keys unquoted when possible.

## 2. JSON

- **2-space** indent; end the file with a single newline.

## 3. Markdown

- Every fenced code block declares its language (`bash`, `cpp`, `python`, …).
- End files with a single newline; keep a blank line before/after lists and tables.

## 4. .editorconfig (copy & use)

Enforce all of the above per repo by copying [`assets/.editorconfig`](../assets/.editorconfig) to the repo root. Pair it with the `editorconfig.editorconfig` VS Code extension (already in the team's recommended list, `profile/README.md` §1.6).
