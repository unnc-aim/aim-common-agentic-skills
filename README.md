# Claude Skills Collection

精选的 Claude Code skills 集合，用于增强 AI 辅助开发体验。

## 📦 Skills 列表

### 1. Remote Exec - 远程 SSH 执行

通过 SSH ControlMaster 在远程服务器上执行命令和管理文件。

**特性：**
- 🔗 SSH ControlMaster 持久连接
- 🔄 多主机配置和切换
- ⚡ 连接复用，提高效率
- 🛡️ 安全的配置管理
- 📊 连接状态监控

**快速开始：**
```bash
# 添加远程主机
.claude/skills/remote-exec/remote-exec.sh add dev user@dev-server.com

# 连接
.claude/skills/remote-exec/remote-exec.sh connect dev

# 执行命令
.claude/skills/remote-exec/remote-exec.sh exec whoami
```

[查看详细文档 →](.claude/skills/remote-exec/README.md)

---

### 2. Referee - RoboMaster 协议查询

RoboMaster 裁判系统通信协议智能查询工具，基于 RAG 技术。

**特性：**
- 🎯 精确文档切片（104 个结构化切片）
- 🔍 向量语义搜索
- ⚡ 毫秒级查询响应
- 🤖 AI 增强回答（Claude Opus 4.6）
- 📊 元数据过滤和反向查询

**快速开始：**
```bash
# 安装依赖
pip3 install chromadb anthropic

# 初始化知识库
cd .claude/skills/referee
python3 vectorstore.py chunks.json

# 查询
python3 query.py "如何获取机器人血量？"
python3 query.py 0x0201
python3 query.py --list
```

[查看详细文档 →](.claude/skills/referee/README.md)

---

## 🚀 安装

### 克隆仓库

```bash
git clone https://github.com/unnc-aim/claude-skills.git
cd claude-skills
```

### 使用 Skills

每个 skill 都是独立的，可以单独使用：

```bash
# Remote Exec
.claude/skills/remote-exec/remote-exec.sh --help

# Referee
cd .claude/skills/referee
python3 query.py --help
```

## 📖 使用指南

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

### Referee Skill

用于查询 RoboMaster 协议文档，适合：
- 快速查找命令码定义
- 理解通信协议格式
- 开发裁判系统相关功能
- 学习协议规范

**示例场景：**
```bash
# 场景 1: 查找特定命令码
python3 query.py 0x0003

# 场景 2: 自然语言查询
python3 query.py "图传链路的波特率是多少"

# 场景 3: 浏览所有命令码
python3 query.py --list

# 场景 4: 无 AI 模式（快速检索）
python3 query.py --no-ai "实时射击数据"
```

## 🛠️ 技术栈

### Remote Exec
- Bash
- SSH ControlMaster
- jq (JSON 处理)

### Referee
- Python 3.8+
- ChromaDB (向量数据库)
- Anthropic API (Claude Opus 4.6)
- sentence-transformers (嵌入模型)

## 📊 性能指标

| Skill | 初始化时间 | 查询延迟 | 存储空间 |
|-------|-----------|---------|---------|
| Remote Exec | < 1s | < 100ms | < 1MB |
| Referee | ~30s | < 100ms | ~10MB |

## 🤝 贡献

欢迎贡献新的 skills！

### 添加新 Skill

1. 在 `.claude/skills/` 下创建新目录
2. 添加 `SKILL.md` 文件（skill 定义）
3. 添加 `README.md` 文件（使用文档）
4. 实现核心功能
5. 提交 Pull Request

### Skill 结构

```
.claude/skills/your-skill/
├── SKILL.md           # Skill 定义（必需）
├── README.md          # 使用文档（必需）
├── main-script.sh     # 主脚本
├── requirements.txt   # 依赖（如果需要）
└── ...                # 其他文件
```

## 📝 许可证

MIT License

## 🔗 相关链接

- [Claude Code 文档](https://docs.anthropic.com/claude/docs)
- [Claude API](https://www.anthropic.com/api)
- [RoboMaster 官网](https://www.robomaster.com/)

## 📮 联系方式

- GitHub Issues: [提交问题](https://github.com/unnc-aim/claude-skills/issues)
- Pull Requests: [贡献代码](https://github.com/unnc-aim/claude-skills/pulls)

---

**Made with ❤️ by UNNC AIM Team**
