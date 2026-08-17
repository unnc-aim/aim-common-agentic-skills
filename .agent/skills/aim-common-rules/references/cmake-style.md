# CMake Style

> Source of truth: [`standard.cmake.md`](https://github.com/unnc-aim/.github/blob/main/profile/standard.cmake.md) in `unnc-aim/.github`. One-line rule: **lowercase commands, 2-space indent, everything attached to a target.**

## 1. Style rules

- Commands are **lowercase**: `add_executable`, `target_link_libraries`.
- Indentation: **2 spaces**.
- Variables and target names: `snake_case`.

## 2. Modern CMake checklist

- Attach dependencies and flags to targets: `target_link_libraries`, `target_include_directories`, `target_compile_options`.
- Do **not** use global-scope commands: `include_directories`, `add_definitions`, `link_directories`.
- When a target grows, add sources with `target_sources(<target> PRIVATE ...)` instead of one long `add_executable` list.
- Wrap include dirs for installed targets with `$<BUILD_INTERFACE:>` / `$<INSTALL_INTERFACE:>`.

## 3. ROS2 / ament_cmake note

The same rules apply to ROS2 packages built with `ament_cmake`: keep commands lowercase, 2-space indent, and attach dependencies per target (`ament_target_dependencies(<target> ...)`), never globally.
