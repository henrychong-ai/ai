# kg — TODO

Open items, unverified facts and pending decisions. Last reviewed 2026-10-01.

## Verify
- [ ] Run every query in `references/cypher-patterns.md` against a Neo4j 5 instance populated by the server; not executed on 2026-10-01 (no instance available to the author at the time).
- [ ] Walk through the Setup section on a clean machine and confirm the minimal `env` block is sufficient for keyword and semantic search.

## Re-check on each server release
- [ ] Tool names and parameter shapes (notably `add_observations` `contents` versus `add_observations_batch` `observations`, `update_entities_batch` `updates`), `semantic_search` defaults, and create-on-existing-name upsert behaviour. Last checked against 2.9.2 on 2026-10-01.
