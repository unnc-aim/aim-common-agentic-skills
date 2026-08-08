#!/usr/bin/env bash
set -euo pipefail

# Remote SSH Execution Manager
# Manages SSH ControlMaster connections for remote command execution

CONFIG_FILE="${HOME}/.claude-remote-exec.json"
CONTROL_PATH_TEMPLATE="/tmp/claude-ssh-%r@%h:%p"
SSH_CONFIG_FILE="${HOME}/.ssh/config"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

error() {
	echo -e "${RED}Error: $*${NC}" >&2
	exit 1
}

success() {
	echo -e "${GREEN}$*${NC}"
}

warn() {
	echo -e "${YELLOW}$*${NC}"
}

# Save host entry to JSON config
set_host() {
	local name="$1"
	local address="$2"
	local port="$3"
	local tmp

	tmp=$(mktemp)
	jq --arg name "$name" --arg address "$address" --argjson port "$port" \
		'.hosts[$name] = {"address": $address, "port": $port}' \
		"$CONFIG_FILE" >"$tmp" && mv "$tmp" "$CONFIG_FILE"
}

# Resolve an SSH alias via ssh -G and print "address|port"
resolve_ssh_alias() {
	local alias="$1"
	local config_dump
	local user
	local host
	local port
	local address

	config_dump=$(ssh -G "$alias" 2>/dev/null || true)
	[[ -z "$config_dump" ]] && return 1

	user=$(printf '%s\n' "$config_dump" | awk '$1=="user" {print $2; exit}')
	host=$(printf '%s\n' "$config_dump" | awk '$1=="hostname" {print $2; exit}')
	port=$(printf '%s\n' "$config_dump" | awk '$1=="port" {print $2; exit}')

	[[ -z "$host" ]] && return 1

	if [[ -n "$user" ]]; then
		address="${user}@${host}"
	else
		address="$host"
	fi

	if [[ -z "$port" || ! "$port" =~ ^[0-9]+$ ]]; then
		port=22
	fi

	printf '%s|%s\n' "$address" "$port"
}

# List explicit (non-wildcard) Host aliases from ~/.ssh/config
get_ssh_aliases() {
	[[ -f "$SSH_CONFIG_FILE" ]] || return 0

	awk '
        BEGIN { IGNORECASE = 1 }
        /^[[:space:]]*#/ { next }
        tolower($1) == "host" {
            for (i = 2; i <= NF; i++) {
                if ($i ~ /[*?!]/ || $i == "") {
                    continue
                }
                print $i
            }
        }
    ' "$SSH_CONFIG_FILE" | sort -u
}

# Check if alias exists in ~/.ssh/config Host entries
ssh_config_has_alias() {
	local alias="$1"
	get_ssh_aliases | grep -Fx "$alias" >/dev/null 2>&1
}

# Import configured SSH aliases from ~/.ssh/config into local config
sync_ssh_hosts() {
	local aliases
	aliases=$(get_ssh_aliases)

	[[ -z "$aliases" ]] && return 0

	local imported=0
	while IFS= read -r alias; do
		[[ -z "$alias" ]] && continue

		local existing
		existing=$(get_config ".hosts.\"$alias\"")
		[[ -n "$existing" ]] && continue

		local resolved
		resolved=$(resolve_ssh_alias "$alias") || continue

		local address="${resolved%%|*}"
		local port="${resolved##*|}"
		set_host "$alias" "$address" "$port"
		imported=$((imported + 1))
	done <<<"$aliases"

	if [[ "$imported" -gt 0 ]]; then
		success "Imported $imported host(s) from ~/.ssh/config"
	fi
}

# Initialize config file if it doesn't exist
init_config() {
	if [[ ! -f "$CONFIG_FILE" ]]; then
		echo '{"hosts":{},"active":null}' >"$CONFIG_FILE"
		chmod 600 "$CONFIG_FILE"
	fi

	sync_ssh_hosts
}

# Read config value using jq
get_config() {
	local key="$1"
	jq -r "$key // empty" "$CONFIG_FILE" 2>/dev/null || echo ""
}

# Update config value using jq
set_config() {
	local key="$1"
	local value="$2"
	local tmp=$(mktemp)

	# If value starts with "del(", use it as a filter expression
	if [[ "$value" == del\(* ]]; then
		jq "$key | $value" "$CONFIG_FILE" >"$tmp" && mv "$tmp" "$CONFIG_FILE"
	else
		jq "$key = $value" "$CONFIG_FILE" >"$tmp" && mv "$tmp" "$CONFIG_FILE"
	fi
}

# Get control socket path for a host
get_control_path() {
	local name="$1"
	local address=$(get_config ".hosts.\"$name\".address")
	local port=$(get_config ".hosts.\"$name\".port // 22")

	if [[ -z "$address" ]]; then
		error "Host '$name' not found in config"
	fi

	# Parse user@host from address
	local user_host="$address"
	echo "$CONTROL_PATH_TEMPLATE" | sed "s/%r@%h:%p/${user_host}:${port}/"
}

# Check if connection is active
is_connected() {
	local name="$1"
	local address=$(get_config ".hosts.\"$name\".address")
	local port=$(get_config ".hosts.\"$name\".port // 22")

	if [[ -z "$address" ]]; then
		return 1
	fi

	ssh -O check -o ControlPath="$(get_control_path "$name")" \
		-p "$port" "$address" 2>/dev/null
	return $?
}

# Command: add <name> <ssh-address> [port]
cmd_add() {
	[[ $# -lt 2 ]] && error "Usage: $0 add <name> <ssh-address> [port]"

	local name="$1"
	local address="$2"
	local port="${3:-22}"

	init_config

	# Check if name already exists
	local existing=$(get_config ".hosts.\"$name\"")
	if [[ -n "$existing" ]]; then
		warn "Host '$name' already exists. Updating..."
	fi

	set_host "$name" "$address" "$port"
	success "Added host '$name': $address:$port"
}

# Command: remove <name>
cmd_remove() {
	[[ $# -lt 1 ]] && error "Usage: $0 remove <name>"

	local name="$1"
	init_config

	local existing=$(get_config ".hosts.\"$name\"")
	if [[ -z "$existing" ]]; then
		error "Host '$name' not found"
	fi

	# Disconnect if currently connected
	if is_connected "$name"; then
		warn "Disconnecting active connection to '$name'..."
		cmd_disconnect "$name"
	fi

	# Remove active if this was the active host
	local active=$(get_config ".active")
	if [[ "$active" == "$name" ]]; then
		set_config ".active" "null"
	fi

	# Delete the host from config
	local tmp=$(mktemp)
	jq "del(.hosts.\"$name\")" "$CONFIG_FILE" >"$tmp" && mv "$tmp" "$CONFIG_FILE"
	success "Removed host '$name'"
}

# Command: connect <name>
cmd_connect() {
	[[ $# -lt 1 ]] && error "Usage: $0 connect <name>"

	local name="$1"
	init_config

	local address=$(get_config ".hosts.\"$name\".address")
	local port=$(get_config ".hosts.\"$name\".port // 22")

	if [[ -z "$address" ]]; then
		local resolved
		if ssh_config_has_alias "$name"; then
			resolved=$(resolve_ssh_alias "$name" || true)
		else
			resolved=""
		fi

		if [[ -n "$resolved" ]]; then
			address="${resolved%%|*}"
			port="${resolved##*|}"
			set_host "$name" "$address" "$port"
			success "Auto-added '$name' from ~/.ssh/config"
		else
			error "Host '$name' not found. Add it with '$0 add' or define it in ~/.ssh/config."
		fi
	fi

	# Check if already connected
	if is_connected "$name"; then
		warn "Already connected to '$name'"
		set_config ".active" "\"$name\""
		return 0
	fi

	echo "Connecting to $name ($address:$port)..."

	# Establish ControlMaster connection
	ssh -fN \
		-o ControlMaster=yes \
		-o ControlPath="$(get_control_path "$name")" \
		-o ControlPersist=yes \
		-o ServerAliveInterval=60 \
		-o ConnectTimeout=10 \
		-p "$port" \
		"$address" || error "Failed to connect to '$name'"

	set_config ".active" "\"$name\""
	success "Connected to '$name'"
}

# Command: disconnect [name]
cmd_disconnect() {
	init_config

	local name="${1:-$(get_config ".active")}"

	if [[ -z "$name" || "$name" == "null" ]]; then
		error "No active connection. Specify a host name."
	fi

	local address=$(get_config ".hosts.\"$name\".address")
	local port=$(get_config ".hosts.\"$name\".port // 22")

	if [[ -z "$address" ]]; then
		error "Host '$name' not found"
	fi

	if ! is_connected "$name"; then
		warn "Not connected to '$name'"
		return 0
	fi

	echo "Disconnecting from $name..."

	ssh -O exit \
		-o ControlPath="$(get_control_path "$name")" \
		-p "$port" \
		"$address" 2>/dev/null || true

	# Clean up socket file
	local socket=$(get_control_path "$name")
	[[ -S "$socket" ]] && rm -f "$socket"

	# Clear active if this was the active host
	local active=$(get_config ".active")
	if [[ "$active" == "$name" ]]; then
		set_config ".active" "null"
	fi

	success "Disconnected from '$name'"
}

# Command: switch <name>
cmd_switch() {
	[[ $# -lt 1 ]] && error "Usage: $0 switch <name>"

	local name="$1"
	init_config

	local address=$(get_config ".hosts.\"$name\".address")
	if [[ -z "$address" ]]; then
		error "Host '$name' not found"
	fi

	if ! is_connected "$name"; then
		warn "Not connected to '$name'. Connecting..."
		cmd_connect "$name"
	else
		set_config ".active" "\"$name\""
		success "Switched to '$name'"
	fi
}

# Command: list
cmd_list() {
	init_config

	local hosts=$(get_config ".hosts | keys[]")
	local active=$(get_config ".active")

	if [[ -z "$hosts" ]]; then
		echo "No hosts configured. Add one with '$0 add', or define aliases in ~/.ssh/config."
		return 0
	fi

	echo "Configured hosts:"
	echo

	while IFS= read -r name; do
		local address=$(get_config ".hosts.\"$name\".address")
		local port=$(get_config ".hosts.\"$name\".port // 22")
		local status="disconnected"
		local marker=""

		if is_connected "$name"; then
			status="${GREEN}connected${NC}"
		else
			status="${RED}disconnected${NC}"
		fi

		if [[ "$name" == "$active" ]]; then
			marker=" ${GREEN}[active]${NC}"
		fi

		echo -e "  $name: $address:$port - $status$marker"
	done <<<"$hosts"
}

# Command: status
cmd_status() {
	init_config

	local active=$(get_config ".active")

	if [[ -z "$active" || "$active" == "null" ]]; then
		echo "No active connection"
		return 0
	fi

	local address=$(get_config ".hosts.\"$active\".address")
	local port=$(get_config ".hosts.\"$active\".port // 22")

	if is_connected "$active"; then
		success "Active connection: $active ($address:$port)"
	else
		warn "Active host '$active' is not connected"
		echo "Run: $0 connect $active"
	fi
}

# Command: exec <command...>
cmd_exec() {
	[[ $# -lt 1 ]] && error "Usage: $0 exec <command...>"

	init_config

	local active=$(get_config ".active")

	if [[ -z "$active" || "$active" == "null" ]]; then
		error "No active connection. Use '$0 connect <name>' first."
	fi

	local address=$(get_config ".hosts.\"$active\".address")
	local port=$(get_config ".hosts.\"$active\".port // 22")

	if ! is_connected "$active"; then
		error "Not connected to '$active'. Run: $0 connect $active"
	fi

	# Execute command on remote host
	ssh -o ControlPath="$(get_control_path "$active")" \
		-p "$port" \
		"$address" \
		"$@"
}

# Main command dispatcher
main() {
	# Check for jq dependency
	if ! command -v jq &>/dev/null; then
		error "jq is required but not installed. Install it with: brew install jq"
	fi

	local cmd="${1:-}"

	case "$cmd" in
	add)
		shift
		cmd_add "$@"
		;;
	remove)
		shift
		cmd_remove "$@"
		;;
	connect)
		shift
		cmd_connect "$@"
		;;
	disconnect)
		shift
		cmd_disconnect "$@"
		;;
	switch)
		shift
		cmd_switch "$@"
		;;
	list)
		cmd_list
		;;
	status)
		cmd_status
		;;
	exec)
		shift
		cmd_exec "$@"
		;;
	*)
		cat <<EOF
Remote SSH Execution Manager

Usage: $0 <command> [options]

Commands:
  add <name> <ssh-address> [port]  Add a new SSH host configuration
  remove <name>                     Remove a host configuration
  connect <name>                    Connect to a host (establishes ControlMaster)
  disconnect [name]                 Disconnect from a host (defaults to active)
  switch <name>                     Switch active connection to another host
  list                              List all configured hosts and their status
  status                            Show current active connection
  exec <command...>                 Execute command on active remote host

Examples:
  $0 add dev user@dev.example.com
    # Or put aliases in ~/.ssh/config and use them directly
  $0 connect dev
  $0 exec whoami
  $0 exec ls -la /var/www
  $0 switch prod
  $0 disconnect

EOF
		[[ -n "$cmd" ]] && error "Unknown command: $cmd"
		exit 0
		;;
	esac
}

main "$@"
