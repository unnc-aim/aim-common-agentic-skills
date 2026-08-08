# Remote SSH Execution Skill

通过 SSH ControlMaster 在远程服务器上执行命令和管理文件的 Claude Code skill。

## 功能特性

- 🔗 使用 SSH ControlMaster 维持持久连接
- 🔄 支持配置和切换多个远程主机
- ⚡ 连接复用，提高执行效率
- 🛡️ 安全的配置管理（不存储密码）
- 📝 清晰的连接状态显示

## 安装要求

- `jq` - JSON 处理工具
  # macOS
  brew install jq

  # Ubuntu/Debian
  apt-get install jq

- SSH 密钥认证已配置（无密码登录）

## 快速开始

### 1. 配置 ~/.ssh/config（推荐，自动导入）

```sshconfig
Host dev
  HostName dev-server.com
  User ubuntu
  Port 22
```

首次执行 `list` 或 `connect` 时会自动导入以上 Host。

### 2. 手动添加远程主机（可选）

```bash
.claude/skills/remote-exec/remote-exec.sh add dev user@dev-server.com
.claude/skills/remote-exec/remote-exec.sh add prod admin@prod-server.com 2222
```

### 3. 连接到主机

```bash
.claude/skills/remote-exec/remote-exec.sh connect dev
```

### 4. 执行远程命令

```bash
.claude/skills/remote-exec/remote-exec.sh exec whoami
.claude/skills/remote-exec/remote-exec.sh exec "ls -la /var/www"
```

### 5. 切换主机

```bash
.claude/skills/remote-exec/remote-exec.sh switch prod
```

### 6. 断开连接

```bash
.claude/skills/remote-exec/remote-exec.sh disconnect
```

## 命令参考

| 命令 | 说明 | 示例 |
|------|------|------|
| `add <name> <address> [port]` | 手动添加新主机（可选） | `add dev user@host.com 22` |
| `remove <name>` | 删除主机配置 | `remove dev` |
| `connect <name>` | 建立连接 | `connect dev` |
| `disconnect [name]` | 断开连接 | `disconnect` 或 `disconnect dev` |
| `switch <name>` | 切换活动主机 | `switch prod` |
| `list` | 列出所有主机 | `list` |
| `status` | 显示当前连接 | `status` |
| `exec <command>` | 执行远程命令 | `exec pwd` |

## 在 Claude Code 中使用

当你在 Claude Code 会话中提到远程执行或使用 `/remote-exec` 命令时，这个 skill 会被激活。

激活后，Claude 会：
1. 检查你的连接状态
2. 如果需要，引导你配置和连接主机
3. 将所有需要在远程执行的命令通过 `exec` 包装
4. 清晰地区分本地和远程操作

### 示例对话

**你:** 在我的开发服务器上检查 nginx 日志

**Claude:**
```bash
# 检查连接状态
.claude/skills/remote-exec/remote-exec.sh status

# 如果未连接，连接到 dev
.claude/skills/remote-exec/remote-exec.sh connect dev

# 查看 nginx 日志
.claude/skills/remote-exec/remote-exec.sh exec "tail -n 50 /var/log/nginx/error.log"
```

## 文件操作

### 读取文件

```bash
.claude/skills/remote-exec/remote-exec.sh exec cat /etc/nginx/nginx.conf
```

### 写入文件

```bash
# 小文件
.claude/skills/remote-exec/remote-exec.sh exec "echo 'Hello' > /tmp/test.txt"

# 多行文件
.claude/skills/remote-exec/remote-exec.sh exec "cat > /tmp/config.txt << 'EOF'
line 1
line 2
line 3
EOF"
```

### 编辑文件

```bash
.claude/skills/remote-exec/remote-exec.sh exec "sed -i 's/old/new/g' /path/to/file"
```

## 配置文件

配置存储在 `~/.claude-remote-exec.json`：

```json
{
  "hosts": {
    "dev": {
      "address": "user@dev-server.com",
      "port": 22
    },
    "prod": {
      "address": "admin@prod-server.com",
      "port": 2222
    }
  },
  "active": "dev"
}
```

## SSH ControlMaster 说明

这个 skill 使用 SSH ControlMaster 功能来维持持久连接：

- **ControlMaster=yes** - 创建主连接
- **ControlPath=/tmp/claude-ssh-%r@%h:%p** - Socket 文件位置
- **ControlPersist=yes** - 保持连接存活
- **ServerAliveInterval=60** - 每 60 秒发送心跳
- **ConnectTimeout=10** - 10 秒连接超时

这意味着：
- 首次连接后，后续命令执行更快
- 不需要重复认证
- 连接会自动保持活跃
- 断开连接会清理所有资源

## 限制

- 不支持交互式命令（如 `vim`, `top`, `htop`）
- 需要 SSH 密钥认证（不支持密码提示）
- 大文件传输建议使用 `scp` 或 `rsync`

## 故障排除

### 连接失败

```bash
# 检查 SSH 密钥
ssh -T user@host.com

# 检查 socket 文件
ls -la /tmp/claude-ssh-*

# 手动清理 socket
rm /tmp/claude-ssh-*
```

### jq 未安装

```bash
# macOS
brew install jq

# Linux
sudo apt-get install jq  # Debian/Ubuntu
sudo yum install jq      # CentOS/RHEL
```

## 安全建议

- 使用 SSH 密钥而非密码
- 为不同环境使用不同的 SSH 密钥
- 定期轮换 SSH 密钥
- 在生产环境执行命令前务必确认
- 配置文件权限自动设置为 600

## 许可证

MIT
