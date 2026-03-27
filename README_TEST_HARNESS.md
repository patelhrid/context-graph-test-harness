# Graph Augmentation Test Harness

Tests the two hardest correctness problems in the augmentation pipeline:
**entity resolution** (don't duplicate nodes) and **temporal invalidation** (don't keep stale facts active).

## Directory layout

```
sample_repo/
  src/
    main.py       ← Flask entry point (node N-main)
    auth.py       ← Auth module, JWT initially (node N-auth)
    tasks.py      ← Task CRUD endpoints (node N-tasks)
    models.py     ← ORM models, SQLAlchemy initially (node N-models)
    db.py         ← DB session management (node N-db)
  docs/
    ARCHITECTURE.md  ← ADRs (node N-arch)
  README.md          ← Stack overview (node N-readme)

test_events/
  events.json      ← Ordered event stream (E01–E10). Feed these to your pipeline in order.
  TEST_CASES.md    ← 10 test cases with inputs, assertions, and failure modes.
  GROUND_TRUTH.md  ← Expected graph state after every event. Use as oracle for assertions.
```

## How to run

1. Ingest `sample_repo/` as the initial graph (event E01).
2. Feed each subsequent event (E02–E10) through your augmentation pipeline in timestamp order.
3. After each event, compare graph state against the corresponding snapshot in `GROUND_TRUTH.md`.
4. Score each test case as PASS / SOFT FAIL / HARD FAIL per the rubric in `TEST_CASES.md`.

## The 10 test cases at a glance

| TC         | Category              | What it tests                                              |
|------------|-----------------------|------------------------------------------------------------|
| TC-01      | Entity Resolution     | PR names `main.py` → resolves to existing node            |
| TC-02      | Entity Resolution     | PR names `init_db()` → resolves to `db.py` node           |
| TC-03      | Entity Resolution     | PR says "auth module" → resolves to `auth.py` node        |
| TC-04      | Entity Resolution     | Transcript uses 2 phrasings for models → 1 node, 1 edge   |
| TC-ERR-01  | Entity Resolution     | Unknown lib (`pydantic`) does not match existing nodes     |
| TC-05      | Temporal Invalidation | Port 3000 → 8080: old fact invalidated                    |
| TC-06      | Temporal Invalidation | JWT → session auth: README fact invalidated                |
| TC-07      | Temporal Invalidation | JWT → session auth: ADR fact ALSO invalidated             |
| TC-08      | Temporal Invalidation | PostgreSQL → MongoDB: fact + node embeddings updated       |
| TC-09      | Temporal Invalidation | React → Vue: fact invalidated across README + ADR          |
| TC-10      | Temporal Invalidation | AWS → GCP: fact invalidated + genuinely new nodes created  |

## MVP pass bar

- 0 HARD FAILs on TC-05 through TC-10 (temporal invalidation is the priority).
- Entity resolution soft-fails acceptable for now; log them for Phase 2.
