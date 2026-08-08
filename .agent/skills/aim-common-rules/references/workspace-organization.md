# Competition Workspace Organization (Submodules)

> Reference workspace: `unnc-aim/26RC_R2_ws`. Source of truth for the team's actual layout.

## 1. The rule

A competition **workspace** repo (suffix `_ws`, e.g. `26RC_R2_ws`) aggregates many repos as **git submodules** under `src/` (ROS2 colcon layout). When you add a submodule whose repo name carries the **competition prefix** (`26RC_`, `26RC_R2_`, …), **place it at a path with the prefix stripped.** The prefix is redundant inside a workspace whose own name already encodes the year / match / robot.

| Repo (GitHub) | Submodule path | What is stripped |
| --- | --- | --- |
| `26RC_R2_arm_controller` | `src/arm_controller` | full `26RC_R2_` |
| `26RC_R2_web_spoiler` | `src/web_spoiler` | full `26RC_R2_` |
| `26RC_R2_engineer_moveit_config` | `src/engineer_moveit_config` | full `26RC_R2_` |
| `26RC_R2_tof_receiver_v2` | `src/tof_receiver_v2` | full `26RC_R2_` |
| `26RC_R2_controller` | `src/r2_controller` | `26RC_` (keeps robot `R2` → `r2`) |
| `26RC_R2_moveit_config` | `src/r2_moveit_config` | `26RC_` (keeps `r2`) |
| `26RC_interfaces` | `src/rc_interfaces` | `26` + lowercased `RC` → `rc` |
| `Camera2Topic` | `src/Camera2Topic` | (no prefix — unchanged) |
| `ros2_hik_camera` | `src/ros2_hik_camera` | (no prefix — unchanged) |

## 2. How to add — the `<path>` argument is the key

`git submodule add <url> <path>` — pass the **stripped** path explicitly:

```bash
# inside 26RC_R2_ws/
git submodule add https://github.com/unnc-aim/26RC_R2_arm_controller.git src/arm_controller
```

Do **not** let the prefix leak into the workspace:

```bash
# WRONG — redundant prefix; pollutes package / node / topic names
git submodule add https://github.com/unnc-aim/26RC_R2_arm_controller.git src/26RC_R2_arm_controller
```

## 3. Why

- The workspace name `26RC_R2_ws` already states year / match / robot; repeating `26RC_R2_` on every `src/` subdir is noise.
- The stripped directory name becomes the ROS package name — it must match `<name>` in `package.xml` (see [repo-naming.md](repo-naming.md) §1.1) — yielding shorter, cleaner node / topic paths.
- One source of truth for the competition context (the workspace), not N.

## 4. The nuance — how much to strip

Two sub-behaviors coexist in the reference workspace:

- **Drop the full `26RC_R2_`** → bare package name (the common case): `arm_controller`, `web_spoiler`, `engineer_moveit_config`.
- **Drop only `26RC_`, keep the robot token (lowercased)** when it disambiguates: `26RC_R2_controller` → `r2_controller` (so the main robot controller is not just `controller`).

Principle: **strip at least the year+match token (`26RC`); keep the shortest name that is still unambiguous inside the workspace.** Default to dropping the full `26RC_R2_` prefix; retain the robot token only when removing it would collide or lose meaning.

## 5. Consistency requirements

- The submodule **directory name must equal** the ROS package `<name>` in its `package.xml`.
- The competition prefix lives **only** in the GitHub repo name — never inside the workspace tree and never in `package.xml`.
- Non-competition / reusable packages (`Camera2Topic`, `ros2_hik_camera`, …) keep their repo name as the submodule directory (no stripping).

## 6. Anti-example in the wild

`src/aruco_controller` (repo `26RC_R2_aruco_controller`) carries `<name>rc26_r2_aruco_controller</name>` in its `package.xml` — the prefix leaked back in and got mangled to lowercase `rc26`. The directory is correct (`aruco_controller`); the `<name>` is wrong and should be `aruco_controller`. Do not repeat this: once the prefix is stripped at the directory level, `<name>` must follow.
