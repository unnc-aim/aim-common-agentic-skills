# 飞书 Webhook 通知 Skill

任务完成后自动向飞书发送通知。

## 安装

通过项目根目录的 `install.sh` 统一安装，或手动复制：

```bash
mkdir -p ~/.claude/skills/feishu-notify
cp feishu-notify.sh ~/.claude/skills/feishu-notify/
chmod +x ~/.claude/skills/feishu-notify/feishu-notify.sh
```

## 配置

安装后需要手动配置飞书 Webhook URL：

```bash
~/.claude/skills/feishu-notify/feishu-notify.sh config "https://www.feishu.cn/flow/api/trigger-webhook/你的webhook地址"
```

配置会保存到 `~/.claude-feishu-notify.json`。

## 使用

```bash
# 发送通知
~/.claude/skills/feishu-notify/feishu-notify.sh send "标题" "内容"

# 查看配置状态
~/.claude/skills/feishu-notify/feishu-notify.sh status

# 发送测试消息
~/.claude/skills/feishu-notify/feishu-notify.sh test
```

## 在 Claude Code 中使用

告诉 Claude "完成后通知飞书" 或 "发飞书通知"，Claude 会自动生成通知内容并发送。
