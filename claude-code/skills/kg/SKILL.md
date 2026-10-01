---
name: kg
description: Works with a Neo4j knowledge graph through the MCP server `kg` (npm package @henrychong-ai/mcp-neo4j-knowledge-graph) — setup, search strategy (semantic_search for discovery, open_nodes for exact names, search_nodes for keywords), the write protocol (exact-name dedup, batch create or add observations, relations), session capture into the graph, capture standards, observation format, entity naming and classification, data conventions (lowercase-kebab entityType and relation types, domains), MCP response-size limits and oversized entities, and read-only Cypher diagnostics. Use when setting up the knowledge-graph MCP server, searching or recalling from the knowledge graph, creating or updating entities, observations or relations, or when asked to "capture this session to the KG", "save this to the knowledge graph", or "kg capture". Replaces the retired /kg command.
---

# Knowledge Graph (KG)

A persistent, temporally versioned knowledge graph in Neo4j, reached through the MCP server registered as `kg` (`@henrychong-ai/mcp-neo4j-knowledge-graph`, 2.9.2 checked 2026-10-01). Tools are named here by their server tool names (`semantic_search`, `open_nodes`); your coding agent exposes them under its own prefix for the `kg` server.

## Setup

1. **Node.js 24+ and Neo4j 5**, with the vector index the server creates on first run. Run your own with Docker or Neo4j Desktop (package README → "Storage Backend"), or use a hosted Neo4j instance.
2. **Embedding provider** for `semantic_search`: OpenAI, Cloudflare Workers AI, or any OpenAI-compatible endpoint (README → "Embeddings & Reranking Setup"). Without one the server runs keyword-only. Every client must use the same embedding model and dimension as the graph's vector index.
3. **Register the server as `kg`** in your coding agent's MCP configuration, user scope:

   ```json
   {
     "mcpServers": {
       "kg": {
         "command": "npx",
         "args": ["-y", "@henrychong-ai/mcp-neo4j-knowledge-graph"],
         "env": {
           "NEO4J_URI": "bolt://<your-neo4j-host>:7687",
           "NEO4J_USERNAME": "neo4j",
           "NEO4J_PASSWORD": "<from your secret manager>",
           "NEO4J_DATABASE": "neo4j",
           "NEO4J_VECTOR_DIMENSIONS": "1024",
           "EMBEDDING_API_KEY": "<from your secret manager>",
           "EMBEDDING_MODEL": "<model>",
           "EMBEDDING_DIMENSIONS": "1024"
         }
       }
     }
   }
   ```

   TOML-configured agents use the same keys under `[mcp_servers.kg]` and `[mcp_servers.kg.env]`. The variable is `NEO4J_USERNAME`; `NEO4J_USER` is silently ignored.
4. **Keep secrets out of config files:** launch the server through your secret manager's runner (e.g. 1Password `op run -- npx -y @henrychong-ai/mcp-neo4j-knowledge-graph`) with secret references in `env`.
5. **Shared graph:** when several clients share one graph, set `WRITE_EMBEDDINGS_LOCALLY=false` on every interactive client and let one server-side instance own embedding writes (README → "Multi-Surface MCP Client Setup").
6. **Verify:** restart the agent, then call `semantic_search` with a test query; it should return results or an empty list, not a connection error.

After upgrading the package, clear the npx cache (`rm -rf ~/.npm/_npx/*/node_modules/@henrychong-ai`) and restart the client.

## Tools

| Tool | Use | Key parameters |
|------|-----|----------------|
| `semantic_search` | Discovery by meaning (default search) | `query`, `limit` (default 10, or 5 when a reranker is configured), `entity_types`, `domain` |
| `open_nodes` | Exact-name fetch; dedup check before every write | `names: [...]` |
| `search_nodes` | Keyword/substring match over names, types and observations | `query`, `domain` or `include_null_domain` |
| `create_entities_batch` | Create new entities | `entities: [{name, entityType, domain?, observations: [...]}]` |
| `add_observations_batch` | Append facts to existing entities | `observations: [{entityName, observations: [...]}]` |
| `update_entities_batch` | Change type/domain, add or remove observations | `updates: [{name, entityType?, domain?, addObservations?, removeObservations?}]` |
| `create_relations_batch` | Link entities (both must exist) | `relations: [{from, to, relationType, strength?, confidence?, metadata?}]` |
| `delete_observations`, `delete_entities`, `delete_relations` | Removal (confirm with the user first) | see tool schema |
| `flag_oversized_entities` | Size report, never full bodies | `limit`, `warn_ratio`, `include_ok` |
| `get_entity_history`, `get_graph_at_time` | Version history and point-in-time state | `entityName`; `timestamp` (ms) |

Parameter-name trap: single `add_observations` takes `{entityName, contents}`, while `add_observations_batch` takes `{entityName, observations}`. Prefer the batch tools for all writes.

## Search Strategy

1. **Discover** with `semantic_search` and a natural-language query. Leave `min_similarity` unset: its default is 0 (disabled), and the server's normalised cosine scores cluster too tightly for an absolute floor to separate relevant from irrelevant hits (package README, checked 2026-10-01). Narrow with `entity_types` or `domain` instead.
2. **Confirm** candidate names with `open_nodes`. It returns the entities plus only the relations *between the requested names*, so request an entity together with its neighbours to see those links.
3. **Keyword fallback** with `search_nodes` when you know a literal term but not the exact name.
4. **Escalate** beyond the graph to project documentation, then the web.

Use the targeted tools above for every read; `read_graph` returns the whole graph and exceeds the response cap on any graph of useful size.

## Write Protocol

Apply to every write, including session capture.

1. **Dedup by exact name.** Call `open_nodes` once with every name you intend to write. Semantic and keyword search can miss an existing entity, so an empty search result is not proof of absence.
2. **Existing entity → `add_observations_batch`.** Calling a create tool on an existing name supersedes that entity with the new observation list, discarding the observations it held (upsert behaviour since 2.9.0). Re-creating is therefore never an update.
3. **New entity → `create_entities_batch`**, after checking near-variants of the name (case, plural, abbreviation) with `open_nodes` or `search_nodes`.
4. **Relate → `create_relations_batch`** once both endpoints exist; link each new entity to at least one existing entity so it is reachable.
5. **Read the result.** Batch writes return per-item errors and an additive `warnings[]` naming any entity that has grown into WARN or CRITICAL size; split those (see Size Limits).

Deletion is destructive and needs the user's confirmation. `delete_entities` matches by name, so it removes every entity carrying that name together with its relations: save merged content first and be ready to recreate relations.

## Session Capture Protocol

Run this when asked to capture or save a session (or part of one) to the KG. Capture only what passes the Capture Standards; a session with nothing durable gets a one-line "nothing to capture" report.

1. **Extract** candidates from the conversation (illustrative categories, not required outputs): technologies and tools, projects and systems, decisions with their rationale, problems with root cause and fix, processes and workflows, people and organisations, rules and known pitfalls.
2. **Filter** against the Capture Standards.
3. **Classify and name** each item (Entity Naming and Classification).
4. **Write** using the Write Protocol: one `open_nodes` call for all names, then batched creates, observation adds, and relations.
5. **Consolidate** only within what this session touched: when a write reveals a near-duplicate, add the missing facts to the primary entity and propose the merge and deletion to the user instead of deleting on your own.
6. **Report** concisely: entities created and updated (names), relations added, size warnings, and any proposed merges awaiting approval.

## Capture Standards

**Capture:** project-specific implementations and configuration, decisions with context and rationale, root causes and fixes, pitfalls and workarounds, conventions, people and organisation facts relevant to the work, and insights that change how future work is done.

**Leave out:** public knowledge (standard definitions, generic best practice, anything a web search returns), conversational filler, transient session state, facts already captured, and secrets or credential values (record where the secret lives, never the value). Keep other people's personal data out of the graph unless you have a basis to store it; reference the system of record instead.

## Observation Format

The graph is read by agents, so optimise for retrieval and density rather than prose.

- One self-contained fact per observation, understandable without the rest of the entity.
- Prefix point-in-time facts with the date (`2026-10-01: ...`) and state what a new fact supersedes.
- Dense and structured is welcome (`tool: pandoc | use: pdf→md | status: prod`), but keep the searchable domain terms spelled out: `semantic_search` embeds observation text, so heavy abbreviation reduces recall.
- Prefer appending a correcting observation; remove an observation only when it is wrong.

## Entity Naming and Classification

- **Names:** the exact proper name for real things (`Neo4j`, an organisation, a person's full name); a descriptive, searchable title for rules and incidents (`KG: open_nodes Before create_entities`). Reuse an existing name exactly; encode a version or date in a name only when the version is the subject.
- **entityType:** lowercase-kebab-case and specific. Common values (illustrative, not exhaustive): `person`, `organization`, `technology`, `project`, `system-architecture`, `process`, `concept`, `workflow-rule`, `incident`. Reuse an existing type before inventing one; check with `semantic_search` filtered by `entity_types`.

## Data Conventions

- **entityType:** `lowercase-kebab-case` (`api-service`, `workflow-rule`), never `Api_Service` or `Workflow Rule`.
- **domain:** optional free-form namespace for partitioning a shared graph. Default is `null` (uncategorised). Agree the set of values with everyone who writes to the graph and reuse them exactly. Filter reads with `domain`, or `include_null_domain: true` for uncategorised entities only.
- **relationType:** `lowercase-kebab-case` active verbs (`uses`, `depends-on`, `applies-to`); vocabulary in `references/cypher-patterns.md`.

## Size Limits

- MCP clients cap each tool response, commonly at 25,000 tokens (`MAX_MCP_OUTPUT_TOKENS`).
- An entity whose own observations exceed the cap can no longer be opened by `open_nodes`, which breaks dedup. Run `flag_oversized_entities` when an entity has grown large or a write returns a size warning, then split it: group observations by theme into more specific sibling entities, link them with relations, and remove the moved observations from the parent.
- Request large entities from `open_nodes` a few names at a time.

## References

- `references/cypher-patterns.md` — the server's Neo4j data model, relationship vocabulary, read-only Cypher diagnostics (counts, isolated entities, duplicate names, paths), and direct database access.
- `TODO.md` — open items for this skill.
