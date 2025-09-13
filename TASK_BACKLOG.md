# TASK_BACKLOG (chimera-infra-new)

version: 1
updated: 2025-09-12

```yaml
repo: chimera-infra-new
sprint:
  name: PoC Coaching Endpoint v2.2
  dates: [2025-09-13, 2025-09-20]
owners:
  - jonathan
labels:
  - infra
  - fastapi
  - cognitive-core
  - security
  - tests

tasks:
  - id: rules_4_1_to_4_6
    title: Expand rules 4.1–4.6 for demo narrative
    status: in_progress
    priority: high
    labels: [cognitive-core, coaching]
    acceptance_criteria:
      - Unit tests for each micro-cue template
      - Deterministic behavior with time_since_last_cue_ms budgeting
      - Documented rule mapping in README

  - id: schema_validation
    title: JSON schema + pydantic validators for protocol v2.2
    status: pending
    priority: medium
    labels: [fastapi, validation]
    acceptance_criteria:
      - JSON schema generated and published in repo
      - pydantic model validators for constraints

  - id: logging_obs
    title: Structured logging + request/response sampling toggles
    status: pending
    priority: medium
    labels: [observability]
    acceptance_criteria:
      - uvicorn access logs + app logs in JSONL
      - redact tokens; sampling rate configurable via env

  - id: rate_limiting
    title: Simple in-memory rate limiting per IP/token
    status: pending
    priority: low
    labels: [security]
    acceptance_criteria:
      - 429 on burst traffic; config via env

  - id: docker_compose
    title: Docker Compose sample for local + prod-like run
    status: pending
    priority: low
    labels: [docker]
    acceptance_criteria:
      - compose up exposes port 8080, healthcheck passes
```
