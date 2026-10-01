# KG Data Model, Relationship Vocabulary and Cypher Diagnostics

## Data Model (server 2.9.2, checked 2026-10-01)

The MCP server stores a temporally versioned graph. Direct Cypher must respect it:

- **Entities:** `(:Entity {id, name, entityType, domain, observations, version, createdAt, updatedAt, validFrom, validTo, embedding})`. `observations` is usually stored as a JSON-encoded string, not a list. The **live** version of a name has `validTo IS NULL`; older versions stay in the graph as history.
- **Relations:** one relationship type, `[:RELATES_TO {relationType, strength, confidence, metadata, validFrom, validTo}]`. The semantic type lives in the `relationType` property, so match on `r.relationType`, never on a Neo4j relationship label such as `[:USES]`.
- **Every query** filters `validTo IS NULL` on entities and relations, otherwise it counts history as duplicates.

**Write through the MCP tools only.** A direct Cypher write skips version closing, relationship carry-over and embedding generation, which corrupts history and leaves the entity invisible to `semantic_search`. Use Cypher for read-only diagnostics. For damaged version history (duplicate live versions, duplicated relationships) see the package README section "Versioning safety & graph repair".

## Relationship Vocabulary

Write `relationType` in lowercase-kebab-case as an active verb from the source to the target. Reuse a type from this list before inventing one. Relations created before the convention may use UPPER_SNAKE spellings (`DEPENDS_ON`); match case-insensitively when auditing.

| Group | Types |
|-------|-------|
| Technical | `uses`, `implements`, `requires`, `depends-on`, `integrates-with`, `configures`, `extends`, `executes` |
| Structural | `contains`, `part-of`, `references`, `indexes` |
| Data flow | `provides`, `consumes`, `stores-in`, `accesses`, `converts` |
| Organisational | `works-for`, `manages`, `owns`, `advises`, `founded` |
| Enablement | `enables`, `supports`, `enhances` |
| Comparison | `alternative-to`, `competes-with`, `supersedes` |
| Action and problem-solving | `applies-to`, `causes`, `follows`, `focuses-on`, `solves`, `constrains`, `guides`, `captures-from` |
| Social and personal | `relationship`, `studied-at`, `collaborated-with` |
| Infrastructure | `hosted-on`, `secured-by` |
| Monitoring | `monitors`, `validates`, `documents` |
| Creation and location | `created-by`, `located-in` |

Optional `strength` and `confidence` (0.0–1.0) and `metadata` (e.g. `{source, last_verified}`) can be set per relation; confidence decays over time unless reinforced.

## Read-Only Diagnostics

### Inventory

```cypher
// Live entities by type
MATCH (n:Entity) WHERE n.validTo IS NULL
RETURN n.entityType AS type, count(*) AS entities ORDER BY entities DESC;

// Live entities by domain
MATCH (n:Entity) WHERE n.validTo IS NULL
RETURN coalesce(n.domain, '(null)') AS domain, count(*) AS entities ORDER BY entities DESC;

// Relation types in use
MATCH (:Entity)-[r:RELATES_TO]->(:Entity) WHERE r.validTo IS NULL
RETURN r.relationType AS type, count(*) AS relations ORDER BY relations DESC;
```

### Lookup

```cypher
// Live entity by exact name
MATCH (n:Entity {name: $name}) WHERE n.validTo IS NULL
RETURN n.name, n.entityType, n.domain, n.observations;

// Name contains (case-insensitive)
MATCH (n:Entity) WHERE n.validTo IS NULL AND toLower(n.name) CONTAINS toLower($term)
RETURN n.name, n.entityType LIMIT 25;

// Live neighbourhood of one entity
MATCH (n:Entity {name: $name})-[r:RELATES_TO]-(m:Entity)
WHERE n.validTo IS NULL AND r.validTo IS NULL AND m.validTo IS NULL
RETURN startNode(r).name AS source, r.relationType AS type, endNode(r).name AS target;
```

### Graph health

```cypher
// Isolated live entities (no live relations)
MATCH (n:Entity) WHERE n.validTo IS NULL
  AND NOT EXISTS { MATCH (n)-[r:RELATES_TO]-() WHERE r.validTo IS NULL }
RETURN n.name, n.entityType ORDER BY n.name LIMIT 50;

// Lowest-degree live entities
MATCH (n:Entity) WHERE n.validTo IS NULL
OPTIONAL MATCH (n)-[r:RELATES_TO]-() WHERE r.validTo IS NULL
RETURN n.name, count(r) AS degree ORDER BY degree ASC LIMIT 20;

// Names with more than one live version (repair: package README)
MATCH (n:Entity) WHERE n.validTo IS NULL
WITH n.name AS name, count(*) AS live WHERE live > 1
RETURN name, live;

// Near-duplicate names differing only by case or surrounding spaces
MATCH (n:Entity) WHERE n.validTo IS NULL
WITH toLower(trim(n.name)) AS key, collect(n.name) AS names WHERE size(names) > 1
RETURN key, names;

// entityType values breaking the lowercase-kebab convention
MATCH (n:Entity) WHERE n.validTo IS NULL AND NOT n.entityType =~ '^[a-z0-9]+(-[a-z0-9]+)*$'
RETURN n.entityType, count(*) AS entities ORDER BY entities DESC;
```

### Paths

```cypher
// Shortest live path between two entities (up to 5 hops)
MATCH (a:Entity {name: $start}), (b:Entity {name: $end})
WHERE a.validTo IS NULL AND b.validTo IS NULL
MATCH p = shortestPath((a)-[:RELATES_TO*..5]-(b))
WHERE all(r IN relationships(p) WHERE r.validTo IS NULL)
RETURN [x IN nodes(p) | x.name] AS path;

// Common live neighbours of two entities
MATCH (a:Entity {name: $first})-[r1:RELATES_TO]-(c:Entity)-[r2:RELATES_TO]-(b:Entity {name: $second})
WHERE a.validTo IS NULL AND b.validTo IS NULL AND c.validTo IS NULL
  AND r1.validTo IS NULL AND r2.validTo IS NULL
RETURN DISTINCT c.name, c.entityType;
```

## Direct Access

Run read-only diagnostics with `cypher-shell` against your own Neo4j instance, supplying the password from your secret manager rather than typing it into shell history:

```bash
# Neo4j in a local Docker container named neo4j
docker exec -it neo4j cypher-shell -u neo4j

# Query file against a reachable host, password injected as NEO4J_PASSWORD
cypher-shell -a bolt://<your-neo4j-host>:7687 -u neo4j -p "$NEO4J_PASSWORD" -f query.cypher
```
