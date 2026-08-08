# C++ Formatting

> Source of truth: [`standard.cpp.md`](https://github.com/unnc-aim/.github/blob/main/profile/standard.cpp.md) in `unnc-aim/.github` + the `.clang-format` actually used by the team.
> Two threads: **naming rules** (manual review / clang-tidy) + **layout rules** (clang-format, automatic).

## 1. Naming rules (standard.cpp.md)

> clang-format does **not** check naming; rely on manual review or [assets/.clang-tidy](../assets/.clang-tidy) for automated checks.

| Object | Style | Example |
| --- | --- | --- |
| Functions, macro-functions | all lowercase + underscores | `void some_function();` |
| Variables | lower camelCase | `int someVariable;` |
| Classes, enums | Upper CamelCase (Pascal) | `class SomeClass {};` `enum SomeEnum {};` |
| Structs, unions | `typedef` + all lowercase + underscores + `_t` | `typedef struct {} some_struct_t;` |
| Macro variables, `const` variables | ALL UPPERCASE + underscores | `#define SOME_MACRO 0` `const int SOME_CONST = 0;` |

### Detailed rules

- **No global variables used for parameter passing**; if a global is genuinely needed, use a **static global** (`static`) instead — pass parameters via pointers / references.

### `.h` standard template

```cpp
#ifndef SOME_HEADERFILE_H
#define SOME_HEADERFILE_H

// header includes
#include "main.h"

// macro variables and macro functions
#define SOME_VARIABLE 0

// struct
typedef struct {
    int a;
    int b;
} some_struct_t;

// union
typedef union {
    struct {
        int c;
        int d;
    };
    double e;
} some_union_t;

// class (private members first, public below; constructors at the top of the member section)
class A {
private:
    int var;
public:
    A();
    ~A();
    void func();
};

// free functions
void some_function();

#endif
```

### `.cpp` standard template

```cpp
// header includes
#include "some_header.h"

// static global constants
static const int CONST_A = 1;

// global variables (static)
static int varA;

// function declarations
void some_function();

// function definitions
void some_function() {
    varA = CONST_A;
}
```

---

## 2. Layout rules: clang-format

The `.clang-format` actually used by the team (across the `ros2_hik_camera` repos): **Google base**, 2-space indent, column limit 100, opening brace on its own line for class/function/namespace/struct (Allman), pointer symbol centered.

### Canonical file (copy & use)

Copy [assets/.clang-format](../assets/.clang-format) to your repo root as `.clang-format`.

### Install

```bash
# Ubuntu
apt install clang-format          # or clang-format-14
# macOS
brew install clang-format
```

### Command line

```bash
# format in place
clang-format -i $(git ls-files '*.cpp' '*.cc' '*.hpp' '*.h')

# check only, do not change (CI / gate)
clang-format --dry-run -Werror $(git ls-files '*.cpp' '*.hpp' '*.h')
```

### VS Code integration

- Install the `xaver.clang-format` extension.
- `.vscode/settings.json`:
  ```jsonc
  {
    "editor.formatOnSave": true,
    "[cpp]":   { "editor.defaultFormatter": "xaver.clang-format" },
    "[hpp]":   { "editor.defaultFormatter": "xaver.clang-format" },
    "C_Cpp.default.cppStandard": "c++17",
    "C_Cpp.default.cStandard":   "c11"
  }
  ```
- If `.clang-format` is in the repo root, the extension reads it automatically; you can also set `"C_Cpp.formatting": "clangFormat"`.

### What clang-format can / cannot do

- ✅ Can: indentation, line wrapping, column limit, brace placement, pointer `* &` alignment, `#include` sorting, continuation-line alignment.
- ❌ Cannot: naming (casing of functions/variables/classes), in-file section order, whether globals are used — these belong to manual review or clang-tidy.

---

## 3. Automated naming checks: clang-tidy

Copy [assets/.clang-tidy](../assets/.clang-tidy) to your repo root as `.clang-tidy`; it uses `readability-identifier-naming` to check the naming table above automatically.

```bash
# generate compile_commands.json first
colcon build --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
# single file
clang-tidy -p build --config-file=.clang-tidy src/foo.cpp
# batch
run-clang-tidy -p build src/*
```

> ⚠️ **Naming conflict (team to be aware of and reconcile)**:
> The team's vendored `ros2_hik_camera/.clang-tidy` uses `lower_case` variables and a trailing `_` on class members, which **conflicts** with the written `standard.cpp.md` (`camelBack`, no suffix).
> `assets/.clang-tidy` always follows the written spec. The team should reconcile the two.

---

## 4. Known inconsistencies (suggest the team revise the written docs)

- `standard.cpp.md` examples use **4-space** indent, but the team's actual `.clang-format` (Google base) uses **2 spaces**. The `.clang-format` wins; consider updating the written examples to 2 spaces to avoid confusion.
- `.clang-format` does not explicitly set `Standard:`; the canonical file adds `Standard: c++17` (matching the `kfs_tracker` VS Code setting).
