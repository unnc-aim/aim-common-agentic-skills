# Python Formatting

> Source of truth: [`standard.py.md`](https://github.com/unnc-aim/.github/blob/main/profile/standard.py.md) in `unnc-aim/.github`. One-line rule: **all Python code must follow [PEP 8](https://peps.python.org/pep-0008/); format with autopep8 before committing.**

## 1. Tool: autopep8

The team standard explicitly uses **autopep8** (not black / ruff / yapf). autopep8 follows PEP 8 by default, with default `max-line-length = 79`.

### Editor integration

- **VS Code**: install the [autopep8 extension](https://marketplace.visualstudio.com/items?itemName=ms-python.autopep8) (`ms-python.autopep8`) and enable `Format On Save`.

  ```jsonc
  // .vscode/settings.json
  {
    "[python]": {
      "editor.defaultFormatter": "ms-python.autopep8",
      "editor.formatOnSave": true
    },
    "autopep8.args": ["--max-line-length=79"]
  }
  ```

- **PyCharm**: in `Preferences → Tools → Actions on Save`, check `Reformat code`.

### Command line

```bash
# install
pip install autopep8

# format in place, recursively
autopep8 --in-place --recursive --max-line-length 79 .

# show diff only, do not write (CI / gate)
autopep8 --diff --max-line-length 79 src/main.py
```

## 2. Canonical config (copy & use)

Copy the `[flake8]` / `[autopep8]` sections from [assets/setup.cfg](../assets/setup.cfg) into your repo-root `setup.cfg` (line length **79**, matching the `aim-py-2526-courseworks` CI). Key points:

- `max-line-length = 79` (**do not** casually change to 99/100, or the `aim-py-2526-courseworks` CI will fail — it runs bare `autopep8`, i.e. 79).
- Ignore `E203` (whitespace before slice) and `W503` (line break before a binary operator) — consistent with modern tooling / relaxed PEP 8.
- ROS2 `ament_python` repos already have `[develop]` / `[install]` sections in `setup.cfg`: **merge** them in, do not overwrite.

> `flake8` is for checking; `autopep8` is for formatting. Both read `max-line-length` from the `[flake8]` section. flake8 is not enforced by the team, but it is harmless and useful for local self-checks.

## 3. CI (existing reference)

`unnc-aim/aim-py-2526-courseworks/.github/workflows/ci.yml` already uses autopep8 to gate unformatted code:

```yaml
- run: pip install autopep8 pytest
- run: autopep8 --diff src/main/__init__.py > autopep8.out || true
- run: if [ -s autopep8.out ]; then echo "::error::code is not formatted"; exit 1; fi
```

New repos can copy this pattern: treat any non-empty `autopep8 --diff` output as a failure.

## 4. PEP 8 naming quick reference (autopep8 does not check naming — review manually)

| Object | Style | Example |
| --- | --- | --- |
| Module / package | `snake_case` / `lowercase` | `vision_utils`, `hik_camera` |
| Class / exception | `PascalCase` | `ImageProcessor`, `CaptureError` |
| Function / variable / method | `snake_case` | `process_frame`, `frame_count` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_FPS`, `DEFAULT_PORT` |
| Private | leading `_` | `_internal_helper` |

## 5. Import sorting with isort

autopep8 does **not** sort imports. The team standard is to sort them with **isort**. Copy the `[isort]` section from [assets/setup.cfg](../assets/setup.cfg) (it sits alongside `[flake8]` / `[autopep8]`).

### 5.1 The import order (the spec)

Group imports in this order, with a **blank line between groups**; within a group, sort alphabetically and put `import x` before `from x import y`:

1. **stdlib** — `os`, `sys`, `math`, `collections`, …
2. **third-party** — `numpy`, `cv2`, `rclpy`, `torch`, …
3. **first-party / local** — the current repo's own packages and modules

```python
# stdlib
import os
import sys
from collections import defaultdict

# third-party
import cv2
import numpy as np
import rclpy
from rclpy.node import Node

# first-party / local
from hik_camera.camera import CameraNode
from vision_utils import process_frame
```

> In ROS2 (`rclpy`-based) repos, `rclpy` and other pip / ROS deps are **third-party**; only the current repo's own packages are first-party.

### 5.2 Install & run

```bash
# install
pip install isort

# sort in place, recursively (auto-reads setup.cfg [isort])
isort .

# preview only, do not write
isort --diff .
```

### 5.3 Editor integration

- **VS Code**: the Python extension sorts imports via isort out of the box. Add to `.vscode/settings.json`:

  ```jsonc
  {
    "[python]": {
      "editor.defaultFormatter": "ms-python.autopep8",
      "editor.formatOnSave": true,
      "editor.codeActionsOnSave": {
        "source.organizeImports": "explicit"
      }
    },
    "isort.args": ["--line-length", "79"]
  }
  ```

  Trigger it manually via the command palette → **Organize Imports** (`Shift+Alt+O`).

- **PyCharm**: its built-in *Optimize Imports* (`Ctrl+Alt+O`) removes unused imports but does not match isort's grouping. For full parity, run `isort .` from the terminal before committing.

### 5.4 Config

```ini
[isort]
line_length = 79
```

Only `line_length = 79` is pinned (matching autopep8 / flake8); import grouping and multi-line wrapping use isort's defaults. (isort's default line length is already 79 — the line just makes the parity explicit.)

> Want one-import-per-line wrapping with a trailing comma (less diff churn on long imports)? That is isort's `black` profile; the team does not use black, so it is opt-in — set `multi_line_output = 3`, `include_trailing_comma = true`, `use_parentheses = true` if you want it.

### 5.5 Run order with autopep8

Run **isort first, then autopep8** — isort sets the import structure, autopep8 polishes the rest:

```bash
isort . && autopep8 --in-place --recursive --max-line-length 79 .
```

### 5.6 CI

The existing `aim-py-2526-courseworks` CI only runs autopep8. To also gate import order, add:

```yaml
- run: pip install isort
- run: isort --check-only --diff .
```

`isort --check-only` exits non-zero when any file would change — treat that as a failure.

## 6. Type checking & IntelliSense (Pylance)

**Pylance** (`ms-python.vscode-pylance`) is the VS Code Python language server — IntelliSense, go-to-definition, and **type checking**. It ships with the Python extension (`ms-python.python`) and auto-installs; install it explicitly only if IntelliSense is missing.

Pylance is the analyzer; autopep8 formats and isort sorts imports — the three compose without conflict.

Recommended settings (`.vscode/settings.json`):

```jsonc
{
  "python.languageServer": "Pylance",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,
  "python.analysis.inlayHints.variableTypes": true
}
```

- `typeCheckingMode`: `off` / `basic` / `strict`. Use **`basic`** for most repos (catches common type errors with little noise); reserve `strict` for libraries where rigor matters. Tighten a single file with a `# pyright: strict` comment if needed.
- Pylance also flags undefined names, unused imports (overlaps with isort), and signature mismatches — fix what it reports before committing.
