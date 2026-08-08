#!/usr/bin/env bash
set -euo pipefail

# 飞书 Webhook 通知工具
# 向配置的飞书 Webhook 发送 JSON 消息

CONFIG_FILE="${HOME}/.claude-feishu-notify.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "飞书 Webhook 通知工具"
    echo ""
    echo "用法:"
    echo "  $(basename "$0") send <title> <body>    发送通知"
    echo "  $(basename "$0") config <webhook_url>   配置 Webhook URL"
    echo "  $(basename "$0") status                 查看当前配置"
    echo "  $(basename "$0") test                   发送测试消息"
}

ensure_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo -e "${RED}错误: 未找到配置文件${NC}"
        echo "请先配置 Webhook URL:"
        echo "  $(basename "$0") config <webhook_url>"
        exit 1
    fi
}

get_webhook_url() {
    ensure_config
    local url
    url=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['webhook_url'])" 2>/dev/null)
    if [[ -z "$url" ]]; then
        echo -e "${RED}错误: 配置文件中未找到 webhook_url${NC}"
        exit 1
    fi
    echo "$url"
}

cmd_config() {
    local url="${1:-}"
    if [[ -z "$url" ]]; then
        echo -e "${RED}错误: 请提供 Webhook URL${NC}"
        echo "用法: $(basename "$0") config <webhook_url>"
        exit 1
    fi

    python3 -c "
import json
config = {'webhook_url': '$url'}
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
"
    chmod 600 "$CONFIG_FILE"
    echo -e "${GREEN}✓ Webhook URL 已配置${NC}"
    echo "  配置文件: $CONFIG_FILE"
}

cmd_status() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo -e "${YELLOW}未配置${NC}"
        echo "请运行: $(basename "$0") config <webhook_url>"
        return
    fi
    echo -e "${GREEN}已配置${NC}"
    local url
    url=$(get_webhook_url)
    # 只显示部分 URL
    echo "  Webhook: ${url:0:50}..."
    echo "  配置文件: $CONFIG_FILE"
}

cmd_send() {
    local title="${1:-}"
    local body="${2:-}"

    if [[ -z "$title" ]]; then
        echo -e "${RED}错误: 请提供 title${NC}"
        echo "用法: $(basename "$0") send <title> <body>"
        exit 1
    fi

    local url
    url=$(get_webhook_url)

    # 使用 Python 构建 JSON 并发送，避免 shell 转义问题
    local response
    response=$(python3 -c "
import urllib.request, urllib.error, json, sys

url = sys.argv[1]
title = sys.argv[2]
body = sys.argv[3]

payload = json.dumps({'title': title, 'body': body}).encode('utf-8')
req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})

try:
    resp = urllib.request.urlopen(req)
    result = resp.read().decode('utf-8')
    print(result)
except urllib.error.HTTPError as e:
    print(f'HTTP Error {e.code}: {e.read().decode()}', file=sys.stderr)
    sys.exit(1)
except urllib.error.URLError as e:
    print(f'URL Error: {e.reason}', file=sys.stderr)
    sys.exit(1)
" "$url" "$title" "$body" 2>&1)

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✓ 通知已发送${NC}"
        echo "  标题: $title"
        echo "  内容: $body"
        echo "  响应: $response"
    else
        echo -e "${RED}✗ 发送失败${NC}"
        echo "  $response"
        exit 1
    fi
}

cmd_test() {
    echo "发送测试消息..."
    cmd_send "Claude Code 测试通知" "这是一条来自 Claude Code feishu-notify 技能的测试消息。如果你看到这条消息，说明 Webhook 配置正确！"
}

# 主入口
case "${1:-}" in
    send)     cmd_send "${2:-}" "${3:-}" ;;
    config)   cmd_config "${2:-}" ;;
    status)   cmd_status ;;
    test)     cmd_test ;;
    *)        usage ;;
esac
