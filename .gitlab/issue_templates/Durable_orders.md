## Problem
The reconstructed service loses orders and keys on process/instance restart.
ADR-002 in PHTBB4.pdf is Proposed and describes PostgreSQL durability with a
Redis cache. The teaching module does not implement that design.

## Acceptance criteria
- Agree on owner/key uniqueness and the 24-hour key retention policy.
- Persist order creation and deduplication atomically.
- Verify restart recovery and concurrent replay with integration tests.
- Document Redis outage behavior and transaction boundaries.

## Evidence
foodflow/order_service.py; test_instances_start_empty.

Status: local issue draft; no GitLab issue ID or URL exists yet.
