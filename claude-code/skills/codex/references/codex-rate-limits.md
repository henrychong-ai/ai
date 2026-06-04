# Checking Codex Usage / Rate Limits

The Codex **MCP exposes no usage endpoint** — `mcp__codex__codex` returns only `{threadId, content}`, and the model can't introspect account quota. Rate limits live in the **CLI** layer: every turn writes a `token_count` event (carrying a `rate_limits` snapshot) into the newest session rollout at `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`.

## The two windows
- `primary` — 5-hour (`window_minutes: 300`)
- `secondary` — weekly (`window_minutes: 10080`)

Each carries `used_percent` and `resets_at` (Unix epoch, UTC).

## Read the latest snapshot
```bash
f=$(find ~/.codex/sessions -name 'rollout-*.jsonl' | xargs ls -t | head -1); grep -h rate_limit "$f" | tail -1 | python3 -m json.tool
```

## Get a live reading
The snapshot **only refreshes when a turn runs**, so the command above reads the *last* session's value. For a current reading, trigger one turn first:
- **Minimal MCP ping:** `mcp__codex__codex` with `prompt:"reply ok"`, `config.model_reasoning_effort:"none"`, `sandbox:"read-only"`, `approval-policy:"never"` — then run the command above.
- **Interactive:** run `codex` → `/status` (shows both windows live).

This is the **OpenAI / ChatGPT-plan** quota — entirely separate from Anthropic/Claude rate limits.
