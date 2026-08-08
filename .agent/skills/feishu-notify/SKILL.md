# Feishu Notify Skill

任务完成后向飞书 Webhook 发送通知。

## Trigger

Activate this skill when:
- The user asks to send a feishu/飞书 notification
- The user uses `/feishu-notify` command
- The user requests notification after task completion
- Claude completes a specific task and the user has previously instructed to notify via feishu

## Capabilities

This skill enables Claude to:
1. Send notifications to a configured Feishu webhook
2. Configure the Feishu webhook URL
3. Check webhook configuration status
4. Auto-generate meaningful title and body summarizing the completed task

## Setup

First-time setup requires configuring the webhook URL:

```bash
~/.claude/skills/feishu-notify/feishu-notify.sh config <webhook_url>
```

Check current configuration:
```bash
~/.claude/skills/feishu-notify/feishu-notify.sh status
```

## Usage in Claude Code

### Sending a notification after completing a task

When the user asks you to notify after a task, or when you complete a task that the user wants to be notified about:

1. Generate a concise, meaningful title and body based on what was accomplished
2. Send the notification:

```bash
~/.claude/skills/feishu-notify/feishu-notify.sh send "<title>" "<body>"
```

The JSON payload sent to the webhook is:
```json
{
  "title": "<generated title>",
  "body": "<generated body>"
}
```

### Guidelines for generating notification content

- **title**: A short summary of the task (e.g., "代码重构完成", "Bug 修复: 登录页面", "新功能已部署")
- **body**: A brief description of what was done, key changes, or results. Keep it informative but concise.

### Examples

```bash
# After fixing a bug
~/.claude/skills/feishu-notify/feishu-notify.sh send "Bug 修复完成" "修复了用户登录时 token 过期未刷新的问题，已提交到 main 分支"

# After deploying
~/.claude/skills/feishu-notify/feishu-notify.sh send "部署完成" "v2.1.0 已成功部署到生产环境，包含 3 个新功能和 2 个 bug 修复"

# Test the webhook
~/.claude/skills/feishu-notify/feishu-notify.sh test
```

## Configuration

Configuration is stored at `~/.claude-feishu-notify.json`:
```json
{
  "webhook_url": "https://www.feishu.cn/flow/api/trigger-webhook/..."
}
```

## Behavior Guidelines

1. **Always check configuration** before sending — run `status` if unsure
2. **Generate content in the user's language** — match the language the user is using
3. **Keep notifications concise** — title under 20 chars, body under 200 chars
4. **Include actionable info** — what was done, which branch, what changed
5. **Don't send duplicate notifications** — only send once per completed task

## Limitations

- Requires Python 3 (uses urllib, no external dependencies)
- Webhook URL must be configured manually before first use
- Network access required to reach Feishu API

## allowed-tools

- `Bash(*)` — Required for executing the notification script
