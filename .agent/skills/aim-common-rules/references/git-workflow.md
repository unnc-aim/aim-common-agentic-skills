# Branch & Commit Rules

> Source of truth: [`README.md` §1.3 / §1.4](https://github.com/unnc-aim/.github/blob/main/profile/README.md) in `unnc-aim/.github`.

## 1. Branch naming

- Branch names are **all lowercase**, words joined by **underscores `_`**.
- **Bug-fix** branches start with `fix/` and are named after the bug:
  - `fix/vision_tracking`, `fix/arm_control_error`
- **New-feature** branches start with `feature/` and are named after the feature:
  - `feature/vision_tracking`, `feature/arm_control`
- Milestone results (no significant issues) are named by **version number** as a branch / tag, e.g. `v0.3`, `1.2.0`.
- **Only** results confirmed stable and reliable may be merged to `main`.

> The README literally says `fix/[opener's username]` (i.e. `fix/<person who opened the branch>`); in practice `fix/<bug name>` and `feature/<feature name>` are more common. Both are fine — the key is prefix + all lowercase + underscores.

## 2. Commit messages (Conventional Commits)

### 2.1 Format

```text
<type>(<scope>): <subject>
<blank line>
<body>
<blank line>
<footer>
```

Example:

```text
feat(user-auth): add login functionality

Implemented a login system with JWT authentication.
Updated the user model and added necessary endpoints.

BREAKING CHANGE: Updated the user model to include an additional "authToken" field.
```

### 2.2 Field reference

| Field | Required | Rule |
| --- | --- | --- |
| `<type>` | yes | purpose of the commit, see the table below |
| `<scope>` | no | affected module/scope, e.g. `user-auth`, `api`, `ui`; may be omitted |
| `<subject>` | yes | short description, **<=50 chars**; imperative mood (`Add` not `Added`); **lowercase first letter**; **no trailing punctuation** |
| `<body>` | no | detailed explanation, wrap each line at **<=72 chars**; cover why / how / context |
| `<footer>` | no | `BREAKING CHANGE: ...` for breaking changes; `Closes #123` / `Refs #456` to reference issues |

### 2.3 type values

| type | meaning |
| --- | --- |
| `feat` | new feature |
| `fix` | bug fix |
| `docs` | documentation only |
| `style` | code formatting (no functional change, e.g. whitespace, formatting) |
| `refactor` | refactoring (no bug fix or feature) |
| `test` | adding / modifying tests |
| `chore` | misc (build tools, config files, etc.) |
| `perf` | performance improvement |
| `ci` | CI-related changes |
| `build` | build system or external dependency changes |

## 3. PR workflow

- All **stable** repos must not push directly to `main` → create a branch + Pull Request.
- The default branch is always `main` (**never** `master`).
- No build artifacts in the repo (exclude them via `.gitignore`).
