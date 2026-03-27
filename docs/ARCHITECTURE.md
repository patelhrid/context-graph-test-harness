# Architecture Decisions

## ADR-001: Database choice
**Date**: 2025-11-01
**Decision**: Use PostgreSQL as the primary datastore.
**Rationale**: Team has existing expertise. Strong ACID guarantees needed for task ownership.
**Alternatives considered**: SQLite (rejected: no concurrent writes), MongoDB (rejected: no joins).

## ADR-002: Authentication strategy
**Date**: 2025-11-05
**Decision**: Use JWT tokens for authentication.
**Rationale**: Stateless — no server-side session store needed. Scales horizontally.
**Token lifetime**: 24 hours.

## ADR-003: Deployment target
**Date**: 2025-11-10
**Decision**: Deploy on AWS EC2, us-east-1 region.
**Rationale**: Existing AWS credits. Team familiar with EC2.
**Container strategy**: Docker image pushed to ECR, run directly on EC2.

## ADR-004: Frontend framework
**Date**: 2025-11-12
**Decision**: React for the frontend SPA.
**Rationale**: Team knows React. Large ecosystem. Works well with a REST API.
