# Remote SSH Execution Skill

Execute commands and manage files on remote servers via SSH with persistent connections.

## Trigger

Activate this skill when the user mentions:
- Remote execution, SSH, or remote server operations
- Using `/remote-exec` command
- Wanting to run commands on a remote machine
- Working with files on a remote server

## Capabilities

This skill enables Claude to:
1. Manage SSH connections to multiple remote hosts
2. Execute commands on remote servers through SSH ControlMaster
3. Read and write files on remote systems
4. Switch between different remote environments (dev, staging, prod, etc.)

## Core Commands

The skill provides a wrapper script `remote-exec.sh` with these commands:

- `add <name> <ssh-address> [port]` — Add a new SSH host
- `remove <name>` — Remove a host configuration
- `connect <name>` — Establish persistent SSH connection
- `disconnect [name]` — Close SSH connection
- `switch <name>` — Switch to a different host
- `list` — Show all configured hosts and connection status
- `status` — Display current active connection
- `exec <command...>` — Execute command on active remote host

## Usage Instructions

### Initial Setup

When the skill is first activated:

1. Check if the user has configured any hosts:
   ```bash
   .claude/skills/remote-exec/remote-exec.sh list
   ```

2. If no hosts exist, guide the user to add one:
   ```bash
   .claude/skills/remote-exec/remote-exec.sh add <name> <user@hostname> [port]
   ```

3. Connect to the host:
   ```bash
   .claude/skills/remote-exec/remote-exec.sh connect <name>
   ```

### Executing Commands

Once connected, wrap all remote commands with the exec subcommand:

```bash
.claude/skills/remote-exec/remote-exec.sh exec <command>
```

Examples:
```bash
# Check current directory
.claude/skills/remote-exec/remote-exec.sh exec pwd

# List files
.claude/skills/remote-exec/remote-exec.sh exec ls -la

# Run a script
.claude/skills/remote-exec/remote-exec.sh exec bash /path/to/script.sh

# Complex commands with pipes
.claude/skills/remote-exec/remote-exec.sh exec "ps aux | grep nginx"
```

### File Operations

**Reading files:**
```bash
.claude/skills/remote-exec/remote-exec.sh exec cat /path/to/file
```

**Writing files:**
```bash
# Small files
.claude/skills/remote-exec/remote-exec.sh exec "echo 'content' > /path/to/file"

# Larger files using heredoc
.claude/skills/remote-exec/remote-exec.sh exec "cat > /path/to/file << 'EOF'
file content here
multiple lines
EOF"
```

**Editing files:**
Use sed or similar tools through exec:
```bash
.claude/skills/remote-exec/remote-exec.sh exec "sed -i 's/old/new/g' /path/to/file"
```

### Switching Hosts

To work with multiple environments:

```bash
# Switch to production
.claude/skills/remote-exec/remote-exec.sh switch prod

# Now all exec commands run on prod
.claude/skills/remote-exec/remote-exec.sh exec whoami
```

## Behavior Guidelines

1. **Always check connection status** before executing commands
2. **Clearly distinguish** between local and remote operations in your responses
3. **Use absolute paths** when possible for remote file operations
4. **Handle errors gracefully** — if connection fails, guide user to reconnect
5. **Inform the user** which host commands are being executed on
6. **Quote complex commands** properly to avoid shell interpretation issues

## Example Workflow

```bash
# User asks: "Check the nginx logs on my dev server"

# 1. Check status
.claude/skills/remote-exec/remote-exec.sh status

# 2. If not connected, connect
.claude/skills/remote-exec/remote-exec.sh connect dev

# 3. Execute the command
.claude/skills/remote-exec/remote-exec.sh exec "tail -n 50 /var/log/nginx/error.log"
```

## Security Notes

- SSH keys should be configured for passwordless authentication
- The script uses SSH ControlMaster for connection reuse
- Socket files are created with restricted permissions (600)
- No passwords are stored in configuration files
- Always verify the target host before executing destructive commands

## Limitations

- Requires `jq` to be installed locally for config management
- Requires SSH key-based authentication (no password prompts)
- Interactive commands (like `vim`, `top`) won't work through exec
- Large file transfers should use `scp` or `rsync` directly

## allowed-tools

- `Bash(*)` — Required for executing SSH commands and managing connections
