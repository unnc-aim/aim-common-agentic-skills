# Branch & Commit Rules

> Source of truth: [`README.md` §1.3 / §1.4 / §1.7](https://github.com/unnc-aim/.github/blob/main/profile/README.md) in `unnc-aim/.github`.

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
- Merge PRs with a **merge commit** by default — keep the full branch history; squash / rebase only with a specific reason.
- Recommended repo settings: default branch `main`; auto-delete the head branch after merge; protect `main` (no force push, PR required).

## 4. Recommended local git config

One-time global setup for every member (written docs: `profile/README.md` §1.7):

| Command | Purpose |
| --- | --- |
| `git config --global pull.rebase true` | `git pull` rebases by default → linear history |
| `git config --global init.defaultBranch main` | new repos start on `main` (never `master`) |
| `git config --global push.autoSetupRemote true` | first `git push` on a new branch just works — no `-u` needed (git >= 2.37) |
| `git config --global commit.verbose true` | commit editor shows the full diff → better Conventional Commits |

Repo-level: copy [assets/.gitattributes](../assets/.gitattributes) to the repo root to normalize line endings across Windows / macOS / Linux (prevents CRLF noise in diffs).

## 5. AI-agent git behavior

Rules for any AI agent (Claude Code / Cursor / Codex / …) working in a team repo. They complement §1–§4 (the human workflow) and are defined in this repo rather than `profile/README.md`.

### 5.1 Never commit / push by default

- **Unless the user explicitly asks, never run or assist any `git commit` or `git push`.** This includes, but is not limited to:
  - Running `git commit` / `git push` directly (including `--force`, `--tags`, and other variants);
  - Running commands that auto-create commits on the user's behalf (e.g. scaffolding tools or package-manager init flows) without telling the user;
  - Triggering commits indirectly through hooks such as husky or lint-staged.
- Only execute when the user **explicitly asks in the current task** (e.g. "commit this", "commit and push").
- **Approval does not carry over between tasks**: the user having asked for a commit in a previous task never means you may commit unprompted in the next one. Explicit instruction is required every time.
- Read-only Git operations are unrestricted: `git status`, `git diff`, `git log`, `git branch`, `git show`, etc. can be used freely.
- If a workflow genuinely requires a commit to proceed (e.g. a tool demands a clean working tree), stop and explain to the user, then wait for confirmation.

### 5.2 Suggest a commit message at the end

- After finishing a task that changes code, append a suggested commit message **before ending the reply**, for the user to use when committing themselves.
- **Suggest only, never execute** — never feed it to `git commit` (§5.1 still applies).
- Conventional Commits format (`feat:` / `fix:` / `docs:` / `refactor:` / `chore:`, … — full type table in §2.3), with three hard constraints:
  - **Exactly one line** — subject only; never a body, never footers.
  - **No more than 50 characters for the whole line**, type prefix included (tighter than §2.2's subject-only cap — the prefix counts too).
  - **Always in American English**, regardless of the conversation language.
- Example output:

  > Suggested commit message:
  >
  > ```text
  > feat: add rate limiting to user login
  > ```

- If the task changed no files, skip the suggestion.

### 5.3 Never call the `gh` CLI without permission

- **Unless the user explicitly allows it, never invoke `gh` directly** — this applies to every subcommand: read-only ones (`gh pr view`, `gh run list`, `gh api`) just as much as mutating ones (`gh pr create`, `gh pr merge`, `gh release create`, `gh issue close`, `gh repo …`).
- `gh` acts on GitHub with the user's credentials and touches team-visible resources (PRs, issues, releases, comments, repos) — treat every call as an outward-facing action, not a local one.
- Only run a `gh` command when the user **explicitly allows it in the current task**, ideally naming the command or operation (e.g. "use `gh` to create the PR"). **Approval does not carry over between tasks.**
- If a task needs GitHub data or actions (open a PR, check CI status), state which `gh` command you would run and wait for the user's go-ahead — or let them run it themselves — instead of calling `gh` on your own.
