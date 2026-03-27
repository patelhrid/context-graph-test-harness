# Ground Truth: Expected Graph State After Each Event

This file is the oracle. After running each event through the augmentation pipeline,
the graph state should match the snapshot below. Use this for automated assertion.

---

## After E01 — Initial Ingestion

### Active nodes
| node_id   | type        | path                    |
|-----------|-------------|-------------------------|
| N-main    | CodeFile    | src/main.py             |
| N-auth    | CodeFile    | src/auth.py             |
| N-tasks   | CodeFile    | src/tasks.py            |
| N-models  | CodeFile    | src/models.py           |
| N-db      | CodeFile    | src/db.py               |
| N-readme  | MarkdownDoc | README.md               |
| N-arch    | MarkdownDoc | docs/ARCHITECTURE.md    |

### Active function/class nodes (children of file nodes)
| node_id         | type     | name          | parent  |
|-----------------|----------|---------------|---------|
| N-init_db       | Function | init_db       | N-db    |
| N-get_db        | Function | get_db        | N-db    |
| N-generate_token| Function | generate_token| N-auth  |
| N-verify_token  | Function | verify_token  | N-auth  |
| N-login         | Function | login         | N-auth  |
| N-list_tasks    | Function | list_tasks    | N-tasks |
| N-create_task   | Function | create_task   | N-tasks |
| N-delete_task   | Function | delete_task   | N-tasks |
| N-Task          | Class    | Task          | N-models|

### Active facts
| fact_id | node     | claim                                        |
|---------|----------|----------------------------------------------|
| F01     | N-readme | Database is PostgreSQL                       |
| F02     | N-readme | Server runs on port 3000                     |
| F03     | N-readme | Auth uses JWT tokens                         |
| F04     | N-readme | Frontend framework is React                  |
| F05     | N-readme | Deployment target is AWS EC2                 |
| F06     | N-arch   | Auth uses JWT tokens (ADR-002)               |
| F07     | N-arch   | Frontend framework is React (ADR-004)        |

### Invalidated facts
_(none)_

---

## After E02 — PR-12

### New edges (TC-01, TC-02)
- `PR-12 --[REFERENCES]--> N-main`      ← TC-01: "main.py" resolved to existing file node
- - `PR-12 --[REFERENCES]--> N-init_db`   ← TC-02: "init_db()" resolved to function node inside N-db
 
  - ### Node count delta: +0 (no new nodes should be created)
  - ### Active facts: unchanged from E01
 
  - ---

  ## After E03 — PR-15

  ### New edges (TC-03)
  - `PR-15 --[REFERENCES]--> N-auth`   ← TC-03: "auth module" resolved to existing file node
 
  - ### Node count delta: +0
  - ### Active facts: unchanged
 
  - ---

  ## After E04 — T-001

  ### New edges (TC-04)
  - `T-001 --[REFERENCES]--> N-models`   ← ONE edge only (both phrasings resolve to same node)
 
  - ### Node count delta: +0
  - ### Active facts: unchanged
 
  - ---

  ## After E05 — PR-21

  ### New edges
  - `PR-21 --[MODIFIES]--> N-main`
  - - `PR-21 --[MODIFIES]--> N-readme`
   
    - ### Fact changes (TC-05)
    - | fact_id | status      | claim                      |
    - |---------|-------------|----------------------------|
    - | F02     | INVALIDATED | Server runs on port 3000   |
    - | F08     | ACTIVE      | Server runs on port 8080   |
   
    - ### Active facts after E05
    - F01 ✅ F03 ✅ F04 ✅ F05 ✅ F06 ✅ F07 ✅ F08 ✅
    - F02 ❌
   
    - ---

    ## After E06 — T-002

    ### New edges
    - `T-002 --[MODIFIES]--> N-auth`
   
    - ### Fact changes (TC-06, TC-07)
    - | fact_id | status      | claim                                                |
    - |---------|-------------|------------------------------------------------------|
    - | F03     | INVALIDATED | Auth uses JWT tokens                                 |
    - | F06     | INVALIDATED | Auth uses JWT tokens (ADR-002)                       |
    - | F09     | ACTIVE      | Auth uses session-based auth (Flask-Session + Redis) |
   
    - ### Active facts after E06
    - F01 ✅ F04 ✅ F05 ✅ F07 ✅ F08 ✅ F09 ✅
    - F02 ❌ F03 ❌ F06 ❌
   
    - ---

    ## After E07 — PR-29

    ### New edges
    - `PR-29 --[MODIFIES]--> N-models`
    - - `PR-29 --[MODIFIES]--> N-db`
      - - `PR-29 --[MODIFIES]--> N-tasks`
        - - `PR-29 --[MODIFIES]--> N-readme`
         
          - ### Fact changes (TC-08)
          - | fact_id | status      | claim                  |
          - |---------|-------------|------------------------|
          - | F01     | INVALIDATED | Database is PostgreSQL |
          - | F10     | ACTIVE      | Database is MongoDB    |
         
          - ### Node metadata updates required
          - - N-models: re-embed summary (no longer "SQLAlchemy ORM / Task class", now "PyMongo dataclass")
            - - N-db: re-embed summary (no longer "PostgreSQL via SQLAlchemy", now "MongoDB Atlas via PyMongo")
              - - N-Task (class node): mark stale or re-ingest — the Task class no longer inherits from SQLAlchemy Base
               
                - ### Active facts after E07
                - F04 ✅ F05 ✅ F07 ✅ F08 ✅ F09 ✅ F10 ✅
                - F01 ❌ F02 ❌ F03 ❌ F06 ❌
               
                - ---

                ## After E08 — T-003

                ### New edges
                - `T-003 --[MODIFIES]--> N-readme`
               
                - ### Fact changes (TC-09)
                - | fact_id | status      | claim                                |
                - |---------|-------------|--------------------------------------|
                - | F04     | INVALIDATED | Frontend framework is React          |
                - | F07     | INVALIDATED | Frontend framework is React (ADR-004)|
                - | F11     | ACTIVE      | Frontend framework is Vue 3          |
               
                - ### Active facts after E08
                - F05 ✅ F08 ✅ F09 ✅ F10 ✅ F11 ✅
                - F01 ❌ F02 ❌ F03 ❌ F04 ❌ F06 ❌ F07 ❌
               
                - ---

                ## After E09 — PR-34

                ### New nodes (TC-10)
                | node_id        | type       | path             |
                |----------------|------------|------------------|
                | N-dockerfile   | ConfigFile | Dockerfile       |
                | N-cloudbuild   | ConfigFile | cloudbuild.yaml  |

                ### New edges
                - `PR-34 --[ADDS]-->     N-dockerfile`
                - - `PR-34 --[ADDS]-->     N-cloudbuild`
                  - - `PR-34 --[MODIFIES]--> N-readme`
                   
                    - ### Fact changes (TC-10)
                    - | fact_id | status      | claim                              |
                    - |---------|-------------|------------------------------------|
                    - | F05     | INVALIDATED | Deployment target is AWS EC2       |
                    - | F12     | ACTIVE      | Deployment target is GCP Cloud Run |
                   
                    - ### Active facts after E09 (final state)
                    - F08 ✅ F09 ✅ F10 ✅ F11 ✅ F12 ✅
                    - F01 ❌ F02 ❌ F03 ❌ F04 ❌ F05 ❌ F06 ❌ F07 ❌
                   
                    - ---

                    ## After E10 — PR-37

                    ### New edges (TC-ERR-01)
                    - `PR-37 --[MODIFIES]--> N-tasks`
                   
                    - ### New nodes
                    - - None — pydantic is an external lib. If created, must be typed `ExternalDependency`,
                      -   and must NOT be matched to any existing node (especially not N-models).
                     
                      -   ### Active facts: unchanged from E09
                     
                      -   ---

                      ## Final graph summary (after all events)

                      ### File/doc nodes: 9
                      N-main, N-auth, N-tasks, N-models, N-db, N-readme, N-arch, N-dockerfile, N-cloudbuild

                      ### Function/class nodes (surviving after migrations)
                      Note: after E07 (MongoDB migration), SQLAlchemy-specific nodes like N-Task should be
                      re-ingested or marked stale. The exact set depends on your re-ingestion strategy.

                      ### Active facts: 5
                      | fact_id | claim                                                |
                      |---------|------------------------------------------------------|
                      | F08     | Server runs on port 8080                             |
                      | F09     | Auth uses session-based auth (Flask-Session + Redis) |
                      | F10     | Database is MongoDB                                  |
                      | F11     | Frontend framework is Vue 3                          |
                      | F12     | Deployment target is GCP Cloud Run                   |

                      ### Invalidated facts: 7
                      F01, F02, F03, F04, F05, F06, F07

                      ### A query like "what is the tech stack?" must return ONLY the 5 active facts above.
                      ### It must NOT return any of the 7 invalidated facts.
