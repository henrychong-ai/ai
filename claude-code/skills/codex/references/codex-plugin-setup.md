# Codex Plugin Setup (Claude Code)

Setup guide for the official **OpenAI Codex plugin for Claude Code**, which routes GPT-5.6 (Sol/Terra/Luna) work to the Codex app-server runtime. Current on this estate: `codex@openai-codex` v1.0.6, user scope, Codex CLI 0.153.4.

## Prerequisites

- **macOS** with Homebrew
- **ChatGPT Plus/Pro subscription** (browser-based auth; no API keys)
- **Node.js** 18+
- **Claude Code**

## Installation

### 1. Install the Codex CLI

```bash
brew install --cask codex
codex --version
```

### 2. Authenticate

Opens a browser for ChatGPT login; the session persists.

```bash
codex login
```

### 3. Create the config

`~/.codex/config.toml` drives model, reasoning, and service tier for every plugin call — the companion CLI passes only `--model` and `--effort` per call and inherits the rest.

```bash
mkdir -p ~/.codex
cat > ~/.codex/config.toml << 'EOF'
sandbox_mode           = "workspace-write"
approval_policy        = "never"
model                  = "gpt-5.6-sol"   # gpt-5.6-sol (flagship, default) | gpt-5.6-terra | gpt-5.6-luna
model_reasoning_effort = "xhigh"          # none | minimal | low | medium | high | xhigh
service_tier           = "default"        # "default" = standard speed; "fast" = priority routing

[features]
web_search_request = true

[sandbox_workspace_write]
network_access = true
EOF
```

Keys used by the plugin path:

| Key | Effect |
|-----|--------|
| `model` | Model when a call omits `--model` |
| `model_reasoning_effort` | Effort when a call omits `--effort`; the companion accepts `none`/`minimal`/`low`/`medium`/`high`/`xhigh` and rejects `max`/`ultra` |
| `service_tier` | **Config-global** — the plugin exposes no per-call tier flag, so switching between standard and priority routing means editing this value |

Two config shapes to keep clear of: `approvals_reviewer = "auto_review"`, which auto-approved a destructive sandbox escalation in headless `codex exec`; and a key whose type the CLI does not expect (a map where a boolean belongs, such as `features.context_management`), which crashes the runtime on parse.

### 4. Install the plugin

```bash
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex@openai-codex
```

Verify with `claude plugin list`.

### 5. Verify readiness

In a Claude Code session, run `/codex:setup`, or from a shell:

```bash
CODEX_COMPANION=$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs | sort -V | tail -1)
node "$CODEX_COMPANION" setup --json
```

Then a live round-trip:

```bash
node "$CODEX_COMPANION" task --model gpt-5.6-luna --effort low "Reply with exactly: plugin ok"
```

## Plugin Root Resolution

The plugin unpacks to `~/.claude/plugins/cache/openai-codex/codex/<version>/`. The version segment changes on every upgrade, so resolve it rather than hardcoding it. Plugin-authored commands get `${CLAUDE_PLUGIN_ROOT}`; anything outside the plugin (this skill, the `codex-relay` agent, `/autosequence`) uses the glob:

```bash
CODEX_COMPANION=$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs | sort -V | tail -1)
```

## Runtime Model

The companion CLI talks to the Codex **app-server**: a shared local daemon reached over a unix socket, started on demand by the first command and reused by later ones. There is no long-lived MCP server process inside Claude Code, so a Codex CLI reinstall no longer strands a running server on a stale binary path, and a fresh Claude Code session is not needed to pick up a new Codex build.

## Upgrading

```bash
claude plugin update codex@openai-codex   # restart Claude Code to apply
brew upgrade --cask codex                  # Codex CLI itself
```

## Troubleshooting

Start with `setup --json` and read the fields:

| Field | Meaning when false or absent |
|-------|------------------------------|
| `ready` | Something below is unmet; `nextSteps` names it |
| `codex.available` | Codex CLI missing from PATH — reinstall the cask |
| `auth.loggedIn` | ChatGPT session expired — `codex login` |
| `sessionRuntime` | Names the runtime mode and broker socket; useful when jobs never start |
| `reviewGateEnabled` | The optional stop-time review gate; toggle with `/codex:setup --enable-review-gate` |

Other symptoms:

- **A flag appears inside Codex's answer.** The companion's parser treats an unrecognised flag as prompt text. Check the flag against the subcommand's supported set.
- **A background job never finishes.** `status <job-id> --all` shows its state; `cancel <job-id>` stops it.
- **Model name rejected upstream.** Model strings pass through verbatim apart from the `spark` alias, so a typo reaches the API unchanged.
- **Anything below the companion.** `codex doctor` diagnoses the local Codex installation, config, auth, and runtime health.

Complete reinstall:

```bash
claude plugin uninstall codex@openai-codex
brew uninstall --cask codex
rm -rf ~/.codex
# then restart from step 1
```

## Legacy stdio MCP (removed 2026-09-09)

The previous transport was a stdio MCP server — `codex mcp-server -c model=… -c model_reasoning_effort=…` registered in `~/.claude.json`, exposing `mcp__codex__codex` and `mcp__codex__codex-reply`. It was removed for three reasons:

1. **Deprecated upstream.** `codex mcp-server` has printed a deprecation warning since Codex CLI 0.149.1 (24 August 2026), with removal expected in a coming minor release.
2. **Config-parse fragility.** The server loaded `~/.codex/config.toml` at startup and died on any key whose type it did not expect — a `features.context_management` map where a boolean was expected broke it outright on 2026-09-09, taking the whole Codex route down with it.
3. **Process-lifetime coupling.** A long-lived server pinned the Codex binary path for the life of the Claude Code session, so a CLI reinstall left the route broken until a fresh session respawned it.

The plugin's app-server runtime replaces all of that. Per-call parity is close but not exact: model and reasoning effort remain per-call flags, while service tier moved into `config.toml`, and reasoning levels above `xhigh` are no longer reachable through this path.

## Resources

- [Codex plugin for Claude Code](https://github.com/openai/codex-plugin-cc)
- [Codex CLI](https://github.com/openai/codex)
