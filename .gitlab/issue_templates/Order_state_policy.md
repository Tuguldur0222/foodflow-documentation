## Problem
The service only supports Pending -> Cancelled. The latest Week_03_FoodFlow.docx
FR-13 explicitly allows Pending and Confirmed cancellation. W06 is a documented
subset; its implementation does not yet cover Confirmed.

## Acceptance criteria
- Implement the agreed SRS Pending/Confirmed rule with a complete transition table.
- Define payment/refund ownership separately from cancellation.
- Add state-transition and unauthorized-cancellation tests.
- Align the SRS, HTTP contract and public docstrings.

Status: local issue draft; no GitLab issue ID or URL exists yet.
