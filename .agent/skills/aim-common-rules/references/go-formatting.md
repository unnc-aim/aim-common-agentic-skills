# Go Formatting

> Source of truth: [`standard.go.md`](https://github.com/unnc-aim/.github/blob/main/profile/standard.go.md) in `unnc-aim/.github`. One-line rule: **gofmt output is the standard — never hand-format Go code.**

## 1. Tool: gofmt

- `gofmt` / `go fmt` output is the final format. Indentation is **tabs**, decided by gofmt — the team's 2-space rule does **not** apply to Go.
- Check: `gofmt -l .` (empty output = clean). Fix: `gofmt -w .` or `go fmt ./...`.

## 2. goimports

Import grouping and ordering is handled by `goimports`:

```bash
go install golang.org/x/tools/cmd/goimports@latest
goimports -l .   # check
goimports -w .   # fix
```

## 3. Editor integration

- VS Code: install `golang.go` — it formats with gofmt / goimports on save by default (the skill's `assets/.vscode/settings.json` enables format-on-save for Go).

## 4. Naming

- Follow Effective Go: exported identifiers `PascalCase`, unexported `camelCase`, no underscores inside identifiers.
