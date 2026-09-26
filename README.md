# AIM Agentic Skills

精选的 agent skills 集合，用于增强 AI 辅助开发体验。支持 Claude Code / Cursor / Codex 等主流 agent。

## 快速安装

推荐用开源的 [skills](https://github.com/vercel-labs/skills) CLI（`npx skills`）安装——它会自动识别你本地所有 agent，并把整个 skill 目录装好：

```bash
# 安装单个 aim-common-rules skill（全局，所有项目可用）
npx skills add unnc-aim/aim-common-agentic-skills --skill aim-common-rules -g

# 查看仓库内所有可用 skill（不实际安装）
npx skills add unnc-aim/aim-common-agentic-skills --list

# 更新到最新版本
npx skills update
```

> `npx skills` 通过每个 skill 的 `SKILL.md` frontmatter（`name` / `description`）识别 skill。本仓库 4 个 skill（`aim-common-rules` / `remote-exec` / `dji-referee` / `feishu-notify`）均已适配，用上面的命令即可安装任意一个。

## Skills 列表

### 1. AIM Common Rules - 战队仓库与代码规范

UNNC AIM 战队的仓库命名、分支 / Conventional Commits、Python (autopep8 / PEP 8)、C++ (clang-format / clang-tidy)、TypeScript (Prettier / ESLint / pnpm)、Go (gofmt)、CMake 与 Markdown / YAML / JSON 通用风格规范，附带可直接拷贝的规则文件。Agent 会在创建 / 命名仓库、核对 ROS2 包名、写 commit message、格式化代码等场景自动调用。规范的原始文档位于 [unnc-aim/.github](https://github.com/unnc-aim/.github) `profile/`。

**Features：**

- Git Regulation: 无论自己动手还是让 AI 代劳，干活这件事和每一个 commit 的主体都是你本人。AI 立的功、犯的错，一律记在使用 AI 的**你**的头上；提交前自查 diff，亲手提交；禁止把 AI 加为 Co-Author——责任归你，署名也只归你。
- 仓库命名决策树（赛用 / 学年 / 可复用）+ 已知反例
- 分支命名 + Conventional Commits 模板
- Agent Git 行为规范：未经用户当次任务明确要求绝不 `git commit` / `git push`；未经明确许可绝不直接调用 `gh` CLI（含只读子命令）；禁止给 commit 添加 AI 的 `Co-Authored-By` 署名（即使被明确允许提交）；代码任务结束时自动建议单行 commit message（≤50 字符、美式英语），只建议、不执行
- Python：autopep8 + isort + Pylance 配置（line length 79）
- C++：`.clang-format` / `.clang-tidy` 模板
- TypeScript：Prettier（2 空格）+ ESLint，包管理器 pnpm（特殊场景除外，模板齐全）
- Go：gofmt / goimports；CMake：命令小写 + 2 空格 + modern CMake
- Markdown / YAML / JSON 通用风格 + `.editorconfig` 模板
- VS Code 推荐插件 + `.vscode/settings.json` 基线

**安装（推荐，支持所有 agent）：**

```bash
npx skills add unnc-aim/aim-common-agentic-skills --skill aim-common-rules -g
```

[查看详细文档 →](.claude/skills/aim-common-rules/SKILL.md)

---

### 2. Remote Exec - 远程 SSH 执行

通过 SSH ControlMaster 在远程服务器上执行命令和管理文件。

**特性：**

- SSH ControlMaster 持久连接
- 多主机配置和切换
- 连接复用，提高效率
- 安全的配置管理
- 连接状态监控

**快速开始：**

```bash
# 添加远程主机
~/.claude/skills/remote-exec/remote-exec.sh add dev user@dev-server.com

# 连接
~/.claude/skills/remote-exec/remote-exec.sh connect dev

# 执行命令
~/.claude/skills/remote-exec/remote-exec.sh exec whoami
```

[查看详细文档 →](.claude/skills/remote-exec/README.md)

---

### 3. DJI Referee - RoboMaster 协议查询

RoboMaster 裁判系统通信协议智能查询工具，**零依赖，即开即用**。

**特性：**

- 精确文档切片（104 个结构化切片）
- 关键词智能匹配
- 毫秒级查询响应
- 零依赖（纯 Python 标准库）
- 支持添加新文档

**快速开始：**

```bash
# 无需安装任何依赖，直接使用！
python3 ~/.claude/skills/dji-referee/query_simple.py "如何获取机器人血量"
python3 ~/.claude/skills/dji-referee/query_simple.py 0x0003
python3 ~/.claude/skills/dji-referee/query_simple.py --list

# 添加新文档到知识库
python3 ~/.claude/skills/dji-referee/add_document.py add <文档路径> --name <文档名>
```

[查看详细文档 →](.claude/skills/dji-referee/README.md)

---

### 4. Feishu Notify - 飞书 Webhook 通知

任务完成后自动向飞书发送通知，让你随时掌握 Claude Code 的工作进展。

**特性：**

- 飞书 Webhook 推送通知
- Claude 自动生成通知内容（title + body）
- 零依赖（纯 Python 标准库）
- 安全的配置管理

**快速开始：**

```bash
# 配置 Webhook URL（安装后需手动配置一次）
~/.claude/skills/feishu-notify/feishu-notify.sh config "https://www.feishu.cn/flow/api/trigger-webhook/你的地址"

# 发送测试消息
~/.claude/skills/feishu-notify/feishu-notify.sh test

# 手动发送通知
~/.claude/skills/feishu-notify/feishu-notify.sh send "标题" "内容"
```

[查看详细文档 →](.claude/skills/feishu-notify/README.md)

---

## 使用指南

### AIM Common Rules Skill

战队仓库与代码规范。安装后 Agent 会在相关场景自动调用；也可手动 `/aim-common-rules`。适合：

- 创建 / 命名新仓库、核对 ROS2 包名
- 新建分支、撰写 Conventional Commits
- 配置 Python / C++ 格式化（拷贝 `assets/` 下的规则文件到仓库根目录）

### Remote Exec Skill

用于在远程服务器上执行命令，适合：

- 远程开发和调试
- 多环境管理（dev/staging/prod）
- 自动化部署脚本
- 远程日志查看

**示例场景：**

```bash
# 场景 1: 检查生产服务器状态
remote-exec.sh connect prod
remote-exec.sh exec "systemctl status nginx"

# 场景 2: 查看远程日志
remote-exec.sh exec "tail -f /var/log/app.log"

# 场景 3: 切换到开发环境
remote-exec.sh switch dev
remote-exec.sh exec "git pull && npm install"
```

### DJI Referee Skill

用于查询 RoboMaster 协议文档，适合：

- 快速查找命令码定义
- 理解通信协议格式
- 开发裁判系统相关功能
- 学习协议规范

**示例场景：**

```bash
# 场景 1: 查找特定命令码
python3 query_simple.py 0x0003

# 场景 2: 自然语言查询
python3 query_simple.py "图传链路的波特率是多少"

# 场景 3: 浏览所有命令码
python3 query_simple.py --list
```

### Feishu Notify Skill

用于任务完成后发送飞书通知，适合：

- 长时间任务完成提醒
- CI/CD 流程通知
- 部署完成通知
- 任何需要异步通知的场景

**示例场景：**

```bash
# 场景 1: 配置 Webhook
feishu-notify.sh config "https://www.feishu.cn/flow/api/trigger-webhook/xxx"

# 场景 2: 任务完成后通知
feishu-notify.sh send "部署完成" "v2.0 已部署到生产环境"

# 场景 3: 在 Claude Code 中使用
# 告诉 Claude "完成后通知飞书"，Claude 会自动生成内容并推送
```

## 技术栈

### AIM Common Rules

- Markdown（规范文档）+ 配置文件（`.clang-format` / `.clang-tidy` / `setup.cfg` / `.vscode/*`）

### Remote Exec

- Bash
- SSH ControlMaster
- jq (JSON 处理)

### DJI Referee

- Python 3.8+（零依赖版本使用纯标准库）

### Feishu Notify

- Python 3 (标准库 urllib)
- 飞书 Webhook API

## 性能指标

| Skill | 初始化时间 | 查询延迟 | 存储空间 |
| ------- | ----------- | --------- | --------- |
| AIM Common Rules | < 1s | — | < 1MB |
| Remote Exec | < 1s | < 100ms | < 1MB |
| DJI Referee | ~30s | < 100ms | ~10MB |
| Feishu Notify | < 1s | < 500ms | < 1MB |

## 贡献

欢迎贡献新的 skills！

### 添加新 Skill

1. 在 `.agent/skills/` 下创建新目录
2. 添加 `SKILL.md` 文件，包含 `name` / `description` frontmatter（这样 `npx skills` 才能识别）
3. 实现核心功能
4. 提交 Pull Request

### Skill 结构

```bash
.agent/skills/your-skill/
├── SKILL.md           # Skill 定义（必需，含 frontmatter）
├── references/        # 详细参考文档（可选）
├── assets/            # 可拷贝的配置 / 模板文件（可选）
└── ...                # 脚本、依赖等
```

## 许可证

[MIT License](./LICENCE)

## 相关链接

- [Claude Code 文档](https://docs.anthropic.com/claude/docs)
- [Claude API](https://www.anthropic.com/api)
- [skills CLI (npx skills)](https://github.com/vercel-labs/skills)
- [战队规范原始文档 unnc-aim/.github](https://github.com/unnc-aim/.github)

## 联系方式

- GitHub Issues: [提交问题](https://github.com/unnc-aim/aim-common-agentic-skills/issues)
- Pull Requests: [贡献代码](https://github.com/unnc-aim/aim-common-agentic-skills/pulls)
