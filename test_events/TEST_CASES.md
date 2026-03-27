# Graph Augmentation Test Cases

A test suite for verifying **entity resolution** and **temporal invalidation** in the
augmentation pipeline. All tests operate against the sample `taskly` repository
under `sample_repo/` and the ordered event stream in `test_events/events.json`.

Run events **in order** (E01 → E10). Each test case references the event(s) that
trigger it and specifies the exact assertion to check against the graph state.

---

## Category A — Entity Resolution

These tests verify that the augmentation pipeline correctly identifies when a reference
in a PR, commit, or transcript maps to an **existing node** rather than creating a
new one.

---

### TC-01 — PR text names a file by its basename

**Triggered by**: E02 (PR-12)
**Input text**: `"I found a bug in main.py where init_db() is called before the blueprints are registered."`

**Expected graph behaviour**:
- The string `"main.py"` is resolved to the existing node **N-main** (`src/main.py`).
- **No new node** is created for `main.py`.
- An edge is drawn: `PR-12 --[REFERENCES]--> N-main`.

**Failure mode to catch**: Pipeline creates a new `CodeFile` node with label `"main.py"`
instead of matching against the already-ingested node at path `src/main.py`.

**Resolution signal**: Exact filename match (`main.py` → node where `path` ends with `/main.py`).

---

### TC-02 — PR references a file implicitly via its function name

**Triggered by**: E02 (PR-12)
**Input text**: `"Moving the init_db() call to after register_blueprint fixes the crash."`

**Expected graph behaviour**:
- `init_db()` is a function defined in `src/db.py` (not `main.py`).
- The pipeline should draw an edge: `PR-12 --[REFERENCES]--> N-db`.
- This is **in addition to** the N-main reference from TC-01 — both edges should exist.
- **No new node** is created for `init_db`.

**Failure mode to catch**: Pipeline either (a) misses the implicit reference entirely, or
(b) creates a new `Function` node for `init_db` that is disconnected from N-db.

**Resolution signal**: Function name lookup against ingested code content.

---

### TC-03 — PR references a module by a synonym/description rather than filename

**Triggered by**: E03 (PR-15)
**Input text**: `"Cleaned up the auth module. No logic changes — just extracted helper functions."`

**Expected graph behaviour**:
- `"the auth module"` is resolved to the existing node **N-auth** (`src/auth.py`).
- **No new node** is created with label `"auth module"`.
- An edge is drawn: `PR-15 --[REFERENCES]--> N-auth`.

**Failure mode to catch**: Pipeline treats `"auth module"` as a new concept and creates a
floating node disconnected from N-auth.

**Resolution signal**: Fuzzy match — `"auth module"` should resolve to the node whose
`label` is `"auth.py"` and whose file is in the `auth` module path.

---

### TC-04 — Agent transcript uses two different phrasings for the same file

**Triggered by**: E04 (T-001)
**Input**: Transcript references both `"the database model definitions"` and `"src/models.py"`.

**Expected graph behaviour**:
- Both phrasings refer to the same node **N-models** (`src/models.py`).
- The pipeline creates **one** edge: `T-001 --[REFERENCES]--> N-models`.
- It does **not** create two separate edges or two separate nodes.

**Failure mode to catch**: Pipeline resolves the two phrasings independently and either
(a) creates two edges to the same node (a benign duplicate edge — still worth flagging),
or (b) creates a new node for `"database model definitions"` separate from N-models.

**Resolution signal**: Deduplication — after resolving both phrasings to N-models,
only one edge should be written.

---

### TC-ERR-01 — PR references a file that is NOT in the graph

**Triggered by**: E10 (PR-37)
**Input text**: `"Added pydantic validation to the POST /tasks/ endpoint."`

Note: `tasks.py` **is** in the graph (N-tasks). But `"pydantic"` is a new external library,
not an existing node.

**Expected graph behaviour**:
- `tasks.py` mention is resolved to **N-tasks** — edge `PR-37 --[MODIFIES]--> N-tasks`.
- `"pydantic"` is flagged as a new external dependency but **not** forced to resolve
  to any existing node. Pipeline may create a new `ExternalLib` node if the schema
  supports it, or skip it.
- The pipeline does **not** crash or hallucinate a match to an existing node.

**Failure mode to catch**: Pipeline incorrectly maps `"pydantic"` to an existing node
(e.g., N-models, since both relate to data) due to embedding similarity being too greedy.

---

## Category B — Temporal Invalidation

These tests verify that when a new event asserts a fact that **contradicts** an existing
graph fact, the old fact is correctly invalidated (marked stale/superseded) and the
new fact becomes the active one. At no point should both conflicting facts be
simultaneously "active" in the graph.

---

### TC-05 — Direct contradiction: server port changed

**Triggered by**: E05 (PR-21)

**Before (active facts)**:
- F02: `README.md` states `"Server runs on port 3000"` ✅ active

**After event E05**:
- F08: `README.md` states `"Server runs on port 8080"` ✅ active (new)
- F02: `"Server runs on port 3000"` ❌ invalidated (superseded by F08)

**Assertion**:
```
graph.active_facts_about("server port") == ["Server runs on port 8080"]
graph.invalidated_facts_about("server port") == ["Server runs on port 3000"]
```

**Failure mode to catch**: Both F02 and F08 are simultaneously "active", causing
a retrieval query like `"what port does the server run on?"` to return contradictory results.

**Invalidation signal**: The PR body explicitly mentions the port change; F02 and F08
share the same subject (`N-readme`) and the same predicate category (`server_port`).

---

### TC-06 — Contradiction via agent transcript: auth mechanism changed

**Triggered by**: E06 (T-002)

**Before (active facts)**:
- F03: `README.md` states `"Auth uses JWT tokens"` ✅ active
- F06: `ARCHITECTURE.md` states `"Auth uses JWT tokens (ADR-002)"` ✅ active

**After event E06**:
- F09: `auth.py` (and implicitly README) states `"Auth uses session-based auth (Flask-Session + Redis)"` ✅ active
- F03: ❌ invalidated
- F06: ❌ invalidated

**Assertion**:
```
graph.active_facts_about("authentication mechanism") == ["Auth uses session-based auth (Flask-Session + Redis)"]
graph.invalidated_facts() includes F03 and F06
```

**Failure mode to catch**: F06 (from ARCHITECTURE.md) survives invalidation because
the agent transcript didn't explicitly touch `docs/ARCHITECTURE.md`. The pipeline must
infer that the ADR is now stale even though the file wasn't directly referenced.

**Key design question this surfaces**: Does invalidation propagate across nodes that
assert the same logical fact, or only the node directly modified?

---

### TC-07 — Same event invalidates a fact across two different nodes

**Triggered by**: E06 (T-002) — same event as TC-06.

Both F03 (asserted by N-readme) and F06 (asserted by N-arch) state the same logical
fact: "auth uses JWT". A single transcript event should invalidate **both**.

**Assertion**:
```
graph.nodes_asserting_stale_fact("auth uses JWT") == [N-readme, N-arch]
```

**Failure mode to catch**: Only F03 is invalidated (because README is the more obvious
source), while F06 quietly remains active on the ARCHITECTURE node — causing the
graph to return contradictory results depending on which node a retrieval query hits first.

---

### TC-08 — Contradiction: database technology changed

**Triggered by**: E07 (PR-29)

**Before (active facts)**:
- F01: `README.md` states `"Database is PostgreSQL"` ✅ active

**After event E07**:
- F10: `README.md` states `"Database is MongoDB"` ✅ active
- F01: ❌ invalidated

**Assertion**:
```
graph.active_facts_about("database") == ["Database is MongoDB"]
```

**Additional edge to verify**:
- N-models and N-db were heavily modified in PR-29. The pipeline should update their
  `last_modified` metadata and potentially re-embed their summaries to reflect that
  they no longer describe a relational schema.

**Failure mode to catch**: The fact-level invalidation works (F01 → stale), but the
node-level metadata for N-models and N-db still says "SQLAlchemy / PostgreSQL",
causing a semantic mismatch between graph facts and node embeddings.

---

### TC-09 — Contradiction: frontend framework changed

**Triggered by**: E08 (T-003)

**Before (active facts)**:
- F04: `README.md` states `"Frontend framework is React"` ✅ active
- F07: `ARCHITECTURE.md` states `"Frontend framework is React (ADR-004)"` ✅ active

**After event E08**:
- F11: `README.md` states `"Frontend framework is Vue 3"` ✅ active
- F04: ❌ invalidated
- F07: ❌ invalidated

**Assertion**:
```
graph.active_facts_about("frontend framework") == ["Frontend framework is Vue 3"]
graph.invalidated_facts() includes F04 and F07
```

This is structurally identical to TC-06/TC-07 but for a different domain. Include it
to verify the invalidation logic generalises and isn't hardcoded to the auth case.

---

### TC-10 — Contradiction: deployment target changed

**Triggered by**: E09 (PR-34)

**Before (active facts)**:
- F05: `README.md` states `"Deployment target is AWS EC2"` ✅ active

**After event E09**:
- F12: `README.md` states `"Deployment target is GCP Cloud Run"` ✅ active
- F05: ❌ invalidated

**Assertion**:
```
graph.active_facts_about("deployment") == ["Deployment target is GCP Cloud Run"]
```

**Additional check — new nodes**:
Two new files are created in this PR: `Dockerfile` and `cloudbuild.yaml`. These are
genuine new nodes (not duplicates of anything). Verify:
- N-dockerfile and N-cloudbuild are **created** (not erroneously matched to existing nodes).
- Edges: `PR-34 --[ADDS]--> N-dockerfile` and `PR-34 --[ADDS]--> N-cloudbuild`.

---

## Summary Table

| TC ID      | Category              | Event  | What is tested                                               | Key failure mode                          |
|------------|-----------------------|--------|--------------------------------------------------------------|-------------------------------------------|
| TC-01      | Entity Resolution     | E02    | Filename in PR text → existing node                          | Duplicate node created for `main.py`      |
| TC-02      | Entity Resolution     | E02    | Function name → owning file node                             | Implicit reference missed or floated      |
| TC-03      | Entity Resolution     | E03    | Module synonym → existing node                               | Floating concept node created             |
| TC-04      | Entity Resolution     | E04    | Two phrasings in same transcript → same node, one edge       | Two edges or two nodes created            |
| TC-ERR-01  | Entity Resolution     | E10    | Unknown library does not match existing nodes                | Greedy embedding match to wrong node      |
| TC-05      | Temporal Invalidation | E05    | Single fact updated, old one invalidated                     | Both port facts simultaneously active     |
| TC-06      | Temporal Invalidation | E06    | Auth fact invalidated across README node                     | Old JWT fact survives on README           |
| TC-07      | Temporal Invalidation | E06    | Same logical fact invalidated across two nodes               | ADR node's JWT fact survives              |
| TC-08      | Temporal Invalidation | E07    | DB fact invalidated + node metadata stale                    | Node embeddings diverge from active facts |
| TC-09      | Temporal Invalidation | E08    | Frontend fact invalidated across README + ADR                | One of the two sources not invalidated    |
| TC-10      | Temporal Invalidation | E09    | Deployment fact invalidated + genuinely new nodes created    | New files incorrectly entity-resolved     |

---

## Evaluation scoring

For each test case, score:
- **PASS**: assertion holds exactly.
- **SOFT FAIL**: assertion approximately holds but with a benign side effect (e.g., a duplicate edge rather than a duplicate node).
- **HARD FAIL**: assertion fails in a way that would corrupt retrieval results (e.g., two contradictory facts both active, or a wrong entity resolution that pollutes an existing node).

Target for MVP: **0 HARD FAILs** on TC-05 through TC-10. Entity resolution
soft-fails are acceptable at this stage but should be logged for Phase 2.
