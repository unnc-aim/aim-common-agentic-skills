# Repository Naming Convention (Comprehensive)

> Source of truth: [`README.md` §1.1](https://github.com/unnc-aim/.github/blob/main/profile/README.md) in `unnc-aim/.github`. This doc breaks it into an actionable checklist + decision tree + known inconsistencies.

The org's repository naming has **3 cases**. First decide which category your repo belongs to, then apply the matching pattern.

---

## 1. The three naming patterns

### 1.1 Competition repos `[year][match abbr]_[robot (optional)]_[package]`

For **one-off** repos tied to "a given year / match / robot". Segments are joined by underscore `_`; the `[year][match abbr]` part is a single run-together alphanumeric token (**no** underscore between year and match abbreviation). Casing per segment:

- Year: two digits (`26` = 2026, `25` = 2025)
- Match abbreviation: ALL CAPS (`RC` / `UC` / `UL`, …)
- Robot name, when present: run-together PascalCase (`Sentry`, `Infantry`, `NormalHero`, `R1`, `R2`)
- Package segment: lowercase `snake_case`

- `26RC_R2_ws` — 2026 Robocon main match, R2 robot main workspace
- `26RC_R2_kfs_tracker` — 2026 Robocon R2 KFS visual tracking (ROS package name follows the same rule)
- `26RC_R1_arm_controller` — 2026 Robocon R1 arm controller
- `26RC_interfaces` — 2026 Robocon common interfaces (the **robot segment may be omitted** when shared across robots)
- `26UL_Sentry_ws` — 2026 RM UL sentry robot main workspace (named robots are PascalCase, e.g. `Sentry`)
- `25RM_raw_rm_vision` — 2025 RoboMaster vision main repo

> **ROS package-name rule**: if it is a ROS Package, the `<name>` in `package.xml` must match the "package" segment of the repo name, and words within the package name are also `_`-separated. `26RC_interfaces` is an exception using `rc_interfaces` (see §6 known inconsistencies).

### 1.2 Internal / academic-year repos `aim-[4-digit year]-[package]`

For AIM-internal **non-competition**, single-academic-year or long-term repos. Overall **kebab-case**, segments joined by hyphen `-` (different from the competition repos' underscores).

- `aim-2526-py-coursework` — 2025-2026 academic year Python national-day assessment (package segment `-`-separated)
- `aim-2526-navigation-final-assessment` — 2025-2026 academic year navigation group final assessment
- `aim-rookie-courses` — freshman course materials (**long-term** repos may omit the year segment)

> ⚠️ **Segment-order inconsistency**: the written spec says `aim-[year]-[package]`, but existing team repos actually use `aim-[topic]-[year]-[name]` (e.g. `aim-py-2526-courseworks`). **New repos should follow the written spec `aim-2526-xxx`**; the team should reconcile the two. See §6.

### 1.3 External / reusable repos `BrandingRepo` or `package_name`

For open / general-purpose / reusable complete projects, wheels, libs. Free naming:

- Repos with a branding component may omit the `aim-xxxx` prefix and just use the repo name: `RoboMark`
- ROS2 packages may use the `package_name` form: `Camera2Topic`, `ros2_hik_camera`
- Sub-convention: ROS2 hardware / feature drivers commonly use the `ros2_[device/feature]` prefix (snake_case), and `<name>` **drops the `ros2_` prefix**:
  - `ros2_hik_camera` → `<name>hik_camera</name>`
  - `ros2_mvcam_manager`, `ros2_speaker_service`

---

## 2. Token dictionary

| Token | Meaning | Appears in |
| --- | --- | --- |
| `26RC` / `YYRC` | 2-digit year + Robocon (main match) | Competition |
| `25RM` / `YYUL` | 2-digit year + RoboMaster University League | Competition |
| `24UC` / `YYUC` | 2-digit year + UNNC Cup (in-school match) | Competition |
| `R1` / `R2` | Robot number within a match (e.g. R1 = arm, R2 = main robot) | Competition |
| `Sentry` / `NormalHero` | Robot NAME (as opposed to a number) — PascalCase, words run together (no `_`) | Competition |
| `2526` | 4-digit academic year 2025-2026 | `aim-*` only |
| `aim-` | Team-internal, non-competition (courses / training / assessment) | Internal |
| `ros2_` | Reusable ROS2 ecosystem package (driver / feature) | Reusable |
| (no prefix) | External / branding / lib | Reusable |

## 3. Casing & separator quick reference

| Repo type | Casing | Segment separator |
| --- | --- | --- |
| Competition | lowercase `snake_case` + PascalCase robot segment (`Sentry`, `R1`) | underscore `_` |
| Internal / academic-year (`aim-*`) | kebab-case (all lowercase) | hyphen `-` |
| Reusable ROS package | snake_case | underscore `_` |
| Branding / vendor SDK / docs | free (often PascalCase + hyphens) | free |

Branch names: all lowercase, words joined by `_`; default branch `main` (never `master`).

---

## 4. Decision tree (use this when naming a new repo)

```text
Is this repo a one-off for a specific year/match?
├─ yes → competition: [year][match abbr]_[robot (optional)]_[package]   e.g. 26RC_R2_controller
│         · shared across robots → may omit the robot segment            e.g. 26RC_interfaces
│         · robot segment: number (R1/R2) or PascalCase robot name       e.g. 26UL_Sentry_ws
│         · it's a ROS package → <name> matches the "package" segment
│
└─ no  → is it AIM-internal, non-competition (course/training/assessment/long-term)?
   ├─ yes → aim-[year]-[package] (kebab)                  e.g. aim-2526-py-coursework
   │         · long-term libs may omit the year segment   e.g. aim-rookie-courses
   │
   └─ no  → external / general-purpose / reusable lib:
            · brand/project name: free naming             e.g. RoboMark
            · ROS2 driver/feature package: ros2_[device/feature]   e.g. ros2_hik_camera
            · other ROS package: package_name             e.g. dji_referee_protocol
```

## 5. General content rules (go with naming — don't forget)

- **No build artifacts** in any repo — exclude them via `.gitignore` (e.g. ROS2 `build/ install/ log/`, C++ `*.o *.a build/`, Python `__pycache__/ *.pyc dist/ build/ .venv/`).
- Default branch is always `main` (**never** `master`).
- Stable repos must not push directly to `main` — use a branch + Pull Request (branch naming in [git-workflow.md](git-workflow.md)).
- Single ROS-package repos: the repo's "package" segment == the `<name>` in `package.xml` / `setup.py`.
- Every repo should have a readable `README.md`.

---

## 6. Known inconsistencies / anti-examples (team to reconcile)

> These are deviations of existing repos from the written spec, listed for decision-making; **new repos should not repeat them**.

| Repo | Problem | Suggestion |
| --- | --- | --- |
| `aim-*-2526-coursework(s)` | Segment order reversed (actual `aim-topic-year-name` vs spec `aim-year-name`); `coursework` singular/plural inconsistent | Use `aim-2526-xxx` for new repos; unify singular/plural |
| `screw_gripper_controller` | No README; `<name>` is `clapper_control`, mismatching the repo name (violates package-name consistency) | Align repo name and package name (pick one) |
| `26RC_interfaces` | `<name>` is `rc_interfaces` (the package segment `interfaces` is too generic) | Acceptable exception, but be aware |
| `Vision-VSCode-Radar-2025` | Actually a 2025 RM radar (competition), but uses branding-style PascalCase + `-2025` suffix | Legacy; name new competition repos as `25RM_*` |
| `26UL_engineer_*`, `26RM_engineer_controller_serial`, `26UL_balanced_infantry_control`, `26UL_pb2025_sentry_*` | Robot-name words lowercase (`engineer`, `balanced_infantry`, `sentry`) — the robot segment should be PascalCase (e.g. `26UL_Engineer_arm`) | Rename in a batch when convenient |
| `dji_referee_protocol` | RM-specific yet treated as a reusable package (no prefix) | Acceptable "reusable" classification, but make it deliberate |
