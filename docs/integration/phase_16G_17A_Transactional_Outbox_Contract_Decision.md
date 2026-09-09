
# PHASE 16G-R7A — Transactional Outbox Contract Decision

**Project:** PharmaTrybe Clinical Intelligence Platform  
**Phase:** 16 — Identity, Tenant, Authentication & Authorization  
**Slice:** R7A  
**Title:** Transactional Outbox Contract — Invitation Delivery  
**Version:** 1.0  
**Status:** SUPERSEDED  
**Decision Type:** Architecture / Security / Transactionality / Delivery  
**Depends On:** R7 — Invitation Transactionality and Delivery Decision  
**Implementation Status:** NOT AUTHORIZED

**SUPERSEDED — NOT AN IMPLEMENTATION AUTHORITY**

The approved R7A contract is defined exclusively by:
`PHASE_16G_R7A_TRANSACTIONAL_OUTBOX_CONTRACT_AMENDMENT.md`

---

# 1. Purpose

This document resolves the remaining R7 ambiguity concerning the transactional outbox required for invitation delivery.

R7 established that:

1. invitation creation is a database transaction;
2. external invitation delivery must occur outside the database transaction;
3. delivery failure must not roll back a successfully committed invitation;
4. invitation delivery must be provider-neutral;
5. reliable asynchronous delivery requires a transactional outbox.

R7 did not define the concrete outbox schema or lifecycle.

R7A therefore defines the minimum persistent contract required to implement the approved outbox architecture without allowing implementation-specific decisions to become undocumented architecture.

---

# 2. Architectural Principle

The transactional outbox exists to solve the following consistency problem:

```text
Database transaction
        +
External email delivery
````

External delivery cannot participate in the PostgreSQL transaction.

Therefore:

```text
Invitation Creation
        │
        ├── Hospital Invitation
        │
        └── Delivery Outbox Record
                    │
                    │ COMMIT
                    ▼
             Background Delivery
                    │
                    ▼
             External Provider
```

The database transaction establishes the durable intent to deliver.

The delivery worker performs external transmission after the transaction commits.

The external provider is never called as part of the invitation database transaction.

---

# 3. Scope

R7A covers only the persistent transactional outbox contract for invitation delivery.

It defines:

* outbox purpose;
* ownership;
* schema;
* required fields;
* status lifecycle;
* attempt semantics;
* idempotency requirements;
* transaction boundary;
* delivery separation;
* failure handling;
* retry contract;
* terminal failure handling;
* relationship to `hospital_invitations`;
* security requirements;
* audit implications.

R7A does NOT define:

* a specific email provider;
* provider credentials;
* frontend invitation UI;
* SMTP configuration;
* email template design;
* invitation acceptance implementation;
* clinical resources;
* plugin execution;
* RLS changes outside the outbox requirements;
* general-purpose messaging infrastructure.

---

# 4. Governing R7 Decisions

R7A inherits the following decisions from R7.

## 4.1 Supabase Auth

Supabase Auth remains the identity authority.

---

## 4.2 Backend Authorization

FastAPI remains the authorization authority.

Invitation creation requires the approved:

```text
professionals:invite
```

permission.

---

## 4.3 Tenant Authority

The hospital/tenant is resolved from the authenticated user's database-backed authorization context.

The client must not supply the authoritative hospital ID.

---

## 4.4 Invitation Ownership

Every invitation belongs to exactly one hospital.

---

## 4.5 Canonical Role

Invitation roles must use the existing canonical RBAC role catalogue.

No invitation-specific role vocabulary may be introduced.

---

## 4.6 External Delivery

External delivery occurs outside the database transaction.

---

## 4.7 Delivery Failure

External delivery failure must not roll back an already committed invitation.

The invitation remains a valid pending invitation unless another approved lifecycle rule changes its state.

---

# 5. Outbox Decision

## 5.1 Decision

PharmaTrybe SHALL use a **transactional database-backed outbox** for invitation delivery.

The outbox record SHALL be created in the same PostgreSQL transaction as the invitation.

The transaction SHALL commit only after both:

1. the invitation record has been successfully persisted;
2. the corresponding outbox record has been successfully persisted.

---

# 6. Transaction Boundary

The authoritative transaction is:

```text
BEGIN
  |
  +-- validate authorization
  |
  +-- validate invitation request
  |
  +-- create invitation
  |
  +-- create outbox record
  |
COMMIT
```

No external email provider call may occur before the commit.

If invitation creation fails:

```text
ROLLBACK
```

and no outbox record may survive.

If outbox creation fails:

```text
ROLLBACK
```

and no invitation may survive.

Therefore:

```text
Invitation exists
        ⇔
Delivery intent exists
```

for successfully committed invitation creation.

---

# 7. Outbox Ownership

The outbox is a **platform-owned persistence mechanism**.

It is not owned by:

* the frontend;
* an email provider;
* an individual plugin;
* a hospital administrator;
* Supabase Auth.

The application backend owns the lifecycle of the outbox record.

External delivery infrastructure consumes outbox records through the approved delivery abstraction.

---

# 8. Outbox Table

R7A establishes a dedicated table:

```text
invitation_delivery_outbox
```

The table exists specifically for invitation delivery.

It is not a generic event bus.

It is not a general audit table.

It is not a membership event table.

---

# 9. Outbox Schema

The minimum required schema is:

```text
invitation_delivery_outbox
---------------------------------------------
id
invitation_id
hospital_id
recipient_email
delivery_kind
payload
status
attempt_count
available_at
last_attempted_at
delivered_at
failed_at
last_error_code
last_error_message
created_at
updated_at
```

---

# 10. Field Contract

## 10.1 `id`

Type:

```text
UUID
```

Purpose:

Unique outbox record identifier.

Requirements:

* database-generated;
* immutable;
* primary key.

---

## 10.2 `invitation_id`

Type:

```text
UUID
```

Purpose:

References the invitation that created the delivery intent.

Requirements:

* NOT NULL;
* foreign key to `hospital_invitations`;
* immutable.

The relationship is:

```text
hospital_invitations
        1
        │
        │
        ▼
invitation_delivery_outbox
        1
```

For the initial implementation, one invitation creates exactly one outbox delivery record.

---

## 10.3 `hospital_id`

Type:

```text
UUID
```

Purpose:

Preserves tenant ownership of the delivery intent.

Requirements:

* NOT NULL;
* foreign key to the hospital table;
* immutable.

The value must originate from the authoritative invitation/hospital context.

It must never be accepted as an independent client-controlled tenant authority.

---

## 10.4 `recipient_email`

Type:

```text
TEXT
```

Purpose:

Stores the delivery destination associated with the invitation.

Requirements:

* NOT NULL;
* populated from the invitation;
* immutable after creation.

The outbox must not retrieve a different recipient from an untrusted client payload during delivery.

---

# 11. Delivery Kind

## 11.1 `delivery_kind`

Type:

```text
TEXT
```

Approved initial value:

```text
PROFESSIONAL_INVITATION
```

This identifies the delivery contract rather than the external provider.

The implementation must not introduce provider-specific values such as:

```text
SENDGRID_INVITATION
SMTP_INVITATION
RESEND_INVITATION
GMAIL_INVITATION
```

Provider selection remains outside this database contract.

---

# 12. Payload

## 12.1 `payload`

Type:

```text
JSONB
```

Purpose:

Stores the minimum provider-neutral delivery payload required to construct the invitation message.

The payload must contain only approved invitation delivery data.

Minimum conceptual content:

```json
{
  "invitation_id": "<uuid>",
  "recipient_email": "<email>",
  "invitation_token": "<delivery token>",
  "hospital_id": "<uuid>"
}
```

However, the raw invitation token SHALL NOT be persisted in the outbox.

Therefore the persisted implementation payload must contain only the approved non-secret representation required by the delivery mechanism.

If the invitation-link construction requires the raw token, the delivery architecture must obtain it through an approved secure mechanism rather than persisting the raw token in the outbox.

### Security rule

The following MUST NOT be stored in `payload`:

* passwords;
* JWTs;
* Supabase access tokens;
* refresh tokens;
* authentication secrets;
* API keys;
* provider credentials;
* raw authentication credentials.

The raw invitation token must not be duplicated into the outbox.

---

# 13. Token Handling

R7's approved invitation token contract remains authoritative.

The outbox must not create, regenerate, transform, or independently hash invitation tokens.

The invitation record remains the authoritative token state.

The outbox represents delivery intent.

It does not become a second invitation-token store.

---

# 14. Status Lifecycle

The outbox SHALL use the following status values:

```text
PENDING
PROCESSING
DELIVERED
FAILED
```

Lifecycle:

```text
PENDING
   │
   ▼
PROCESSING
   │
   ├──────────────► DELIVERED
   │
   └──────────────► FAILED
                         │
                         │ retry if eligible
                         ▼
                     PENDING
```

---

# 15. `PENDING`

`PENDING` means:

> The invitation delivery intent has been durably committed but has not yet been successfully processed.

Every newly created outbox record begins in:

```text
PENDING
```

---

# 16. `PROCESSING`

`PROCESSING` means:

> A delivery worker currently owns processing of the outbox record.

A worker must not process the same outbox item concurrently with another worker.

The implementation must use database-safe claiming semantics.

---

# 17. `DELIVERED`

`DELIVERED` means:

> The delivery abstraction has reported successful external transmission.

When an item reaches:

```text
DELIVERED
```

the worker must record:

```text
delivered_at
```

The outbox record must not be delivered again during normal processing.

---

# 18. `FAILED`

`FAILED` means:

> Delivery could not be completed and the record is no longer eligible for automatic retry.

A failed outbox record remains available for operational inspection.

The invitation itself is not automatically deleted merely because delivery failed.

---

# 19. Attempt Count

`attempt_count` records the number of actual delivery attempts.

Rules:

* starts at `0`;
* increments when an external delivery attempt begins;
* must not increment merely because a worker reads the row;
* must not reset after a retry;
* is monotonically increasing.

Example:

```text
PENDING
attempt_count = 0

attempt
    ↓

PROCESSING
attempt_count = 1

failure
    ↓

PENDING

attempt
    ↓

PROCESSING
attempt_count = 2
```

---

# 20. Retry Policy

R7A establishes the retry mechanism but does not introduce provider-specific retry behavior.

Automatic retries SHALL be bounded.

A delivery failure must be classified as either:

```text
RETRYABLE
```

or:

```text
NON_RETRYABLE
```

## Retryable examples

Examples may include temporary:

* provider outage;
* network failure;
* timeout;
* transient service-unavailable response.

## Non-retryable examples

Examples may include:

* permanently invalid destination;
* provider rejection indicating permanent failure;
* malformed delivery request.

The implementation must not retry indefinitely.

---

# 21. Maximum Attempts

The initial implementation SHALL use:

```text
MAX_ATTEMPTS = 3
```

After the third unsuccessful retryable delivery attempt:

```text
status = FAILED
```

No further automatic delivery attempts are permitted.

This value is part of the R7A contract and must not be changed by implementation preference.

---

# 22. Retry Scheduling

Retryable failures return the record to:

```text
PENDING
```

with a future:

```text
available_at
```

value.

The worker must not immediately spin on a failed record.

The implementation must apply bounded backoff.

Initial schedule:

```text
Attempt 1 failure
        ↓
5 minutes

Attempt 2 failure
        ↓
30 minutes

Attempt 3 failure
        ↓
FAILED
```

These intervals are operational contract values for R7A.

---

# 23. `available_at`

`available_at` represents the earliest time at which a pending outbox item may be processed.

Rules:

* initial value is the creation time;
* retryable failures set it to a future time;
* workers must not process records before `available_at`.

---

# 24. Failure Recording

When delivery fails, the worker records:

```text
last_error_code
last_error_message
```

Requirements:

* error information must be safe for operational diagnostics;
* secrets must never be written;
* access tokens must never be written;
* raw invitation tokens must never be written;
* provider credentials must never be written.

---

# 25. `last_error_code`

Contains a normalized application/provider-independent failure category where possible.

Examples:

```text
DELIVERY_TIMEOUT
PROVIDER_UNAVAILABLE
INVALID_RECIPIENT
PERMANENT_PROVIDER_REJECTION
UNKNOWN_DELIVERY_ERROR
```

The implementation must not expose provider secrets or raw response credentials.

---

# 26. `last_error_message`

Contains a sanitized diagnostic message.

It must not contain:

* raw invitation tokens;
* JWTs;
* passwords;
* API keys;
* authorization headers;
* refresh tokens.

---

# 27. Idempotency

The outbox must be idempotent with respect to delivery processing.

The authoritative identity of a delivery intent is:

```text
outbox.id
```

The same outbox record must not create multiple successful deliveries during normal worker operation.

The worker must claim records atomically before attempting delivery.

---

# 28. Duplicate Worker Protection

Multiple delivery workers may exist.

Therefore the implementation must prevent:

```text
Worker A ──┐
           ├── same outbox record
Worker B ──┘
```

from being processed concurrently.

The database must provide the authoritative claim/locking mechanism.

The frontend must never participate in outbox processing.

---

# 29. Delivery Abstraction

The outbox worker must communicate through a provider-neutral abstraction.

Conceptually:

```text
Outbox Worker
      │
      ▼
InvitationDeliveryService
      │
      ▼
Delivery Provider
```

The worker must not contain provider-specific business logic.

---

# 30. Provider Independence

The initial architecture must permit the external provider to be replaced without changing:

* invitation schema;
* outbox schema;
* invitation authorization;
* invitation acceptance;
* tenant resolution;
* RBAC.

The provider is an implementation dependency of the delivery abstraction.

---

# 31. Transactional Separation

The following is explicitly forbidden:

```text
BEGIN TRANSACTION

create invitation

send email

COMMIT
```

The following is required:

```text
BEGIN TRANSACTION

create invitation

create outbox record

COMMIT

        ↓

worker

        ↓

delivery provider
```

---

# 32. Delivery Failure and Identity State

A failed email delivery must NOT roll back:

* hospital creation;
* professional creation;
* invitation creation;
* membership state;
* role state.

Those database changes have already committed.

The outbox represents delivery intent independently of the committed identity state.

---

# 33. Invitation State

Delivery status and invitation lifecycle status are separate concepts.

The outbox must not silently redefine:

```text
hospital_invitations.status
```

A delivery failure does not automatically mean that the invitation itself is invalid.

Unless a later approved lifecycle decision states otherwise:

```text
delivery FAILED
        ≠
invitation REVOKED
```

---

# 34. Invitation Acceptance

R7A does not change invitation acceptance semantics.

Acceptance remains governed by R7.

The outbox must not:

* activate memberships;
* assign roles;
* create professional profiles;
* modify RBAC;
* mark invitations accepted.

Only the invitation acceptance workflow performs those actions.

---

# 35. Membership Events

R7A does not modify R6.

The R6 event:

```text
MEMBERSHIP_CREATED
```

remains the approved event for initial hospital registration.

R7A does not introduce:

```text
MEMBERSHIP_ACTIVATED
```

or:

```text
INVITATION_ACCEPTED
```

unless separately approved.

The outbox is not a membership-event system.

---

# 36. Audit Boundary

The outbox is not a replacement for the persistent audit architecture.

Operational delivery information belongs in the outbox.

Clinical and security audit events remain governed by the appropriate audit architecture.

The implementation must not treat:

```text
outbox row
```

as equivalent to:

```text
audit event
```

---

# 37. Tenant Isolation

Every outbox record is tenant-bound through:

```text
hospital_id
```

Workers must preserve tenant context when processing delivery records.

A delivery worker must never:

* infer tenant ownership from client input;
* process an outbox record under another hospital;
* modify another hospital's invitation;
* expose another hospital's recipient information.

---

# 38. RLS and Backend Authority

R7A does not weaken existing RLS or backend authorization.

The backend remains authoritative for invitation creation.

The outbox worker is trusted backend infrastructure.

No frontend authorization decision may determine whether an outbox item can be processed.

---

# 39. Security Requirements

The implementation MUST ensure:

* no raw invitation token is persisted in the outbox;
* no JWT is persisted in the outbox;
* no password is persisted in the outbox;
* no refresh token is persisted in the outbox;
* no provider credential is persisted in the outbox;
* no client-supplied tenant authority is trusted;
* no client-supplied actor authority is trusted;
* delivery processing is backend-only;
* delivery records are tenant-bound;
* retry processing is bounded;
* failed delivery does not create unauthorized membership state.

---

# 40. Migration Requirement

The outbox requires a database migration.

The migration must create:

```text
invitation_delivery_outbox
```

with:

* primary key;
* required foreign keys;
* required NOT NULL constraints;
* status constraint;
* attempt-count constraint;
* timestamps;
* indexes required for worker polling;
* uniqueness required to enforce one delivery intent per invitation.

---

# 41. Uniqueness

The database must enforce:

```text
UNIQUE(invitation_id)
```

for the initial invitation delivery workflow.

Therefore:

```text
one invitation
        ↓
exactly one initial delivery intent
```

Duplicate outbox creation must fail safely.

The application must not rely solely on an application-level existence check.

---

# 42. Worker Query Requirements

The worker must be able to efficiently locate:

```text
PENDING
```

records where:

```text
available_at <= current_time
```

An appropriate database index must support this access pattern.

The exact SQL query and locking syntax are implementation details, provided they preserve the R7A contract.

---

# 43. Timestamps

All timestamps SHALL be stored using timezone-aware UTC semantics.

Required timestamps:

```text
created_at
updated_at
available_at
last_attempted_at
delivered_at
failed_at
```

Rules:

* `created_at` is immutable;
* `updated_at` changes on state mutation;
* `delivered_at` is populated only after successful delivery;
* `failed_at` is populated when the record becomes terminally failed;
* `last_attempted_at` reflects the most recent actual delivery attempt.

---

# 44. State Invariants

The following invariants must hold.

### Pending

```text
status = PENDING
delivered_at = NULL
failed_at = NULL
```

### Processing

```text
status = PROCESSING
delivered_at = NULL
failed_at = NULL
```

### Delivered

```text
status = DELIVERED
delivered_at IS NOT NULL
failed_at = NULL
```

### Failed

```text
status = FAILED
failed_at IS NOT NULL
```

A delivered record must never transition back to pending during normal operation.

---

# 45. Recovery

If a worker crashes while processing an outbox item, the system must not permanently lose the delivery intent.

The implementation must provide a recovery mechanism for stale:

```text
PROCESSING
```

records.

A stale processing record may be safely returned to:

```text
PENDING
```

subject to the attempt limit.

The recovery mechanism must not reset `attempt_count`.

---

# 46. No Silent Loss

The following state is forbidden:

```text
Invitation committed
+
No outbox record
```

Likewise:

```text
Outbox committed
+
Invitation does not exist
```

must be impossible through the approved transaction boundary.

---

# 47. No False Delivery Success

The system must not mark:

```text
DELIVERED
```

before the delivery abstraction reports successful external transmission.

Database insertion into the outbox is not equivalent to successful email delivery.

---

# 48. Delivery Provider Failure

If the provider fails:

```text
outbox != lost
```

The record remains available for retry while attempts remain.

If attempts are exhausted:

```text
status = FAILED
```

The invitation remains persisted for operational recovery according to R7.

---

# 49. Operational Recovery

Terminally failed records must remain inspectable.

R7A does not authorize automatic deletion of failed records.

Any administrative retry/requeue capability is outside the initial R7A implementation unless separately authorized.

---

# 50. Data Retention

R7A does not authorize an automatic retention/deletion policy for outbox records.

Records must therefore remain available until a later approved retention policy is established.

The implementation must not introduce silent deletion merely to simplify storage.

---

# 51. Testing Requirements

R7A implementation must include focused tests for:

### Transactionality

* invitation and outbox commit together;
* invitation rollback removes outbox;
* outbox insertion failure rolls back invitation.

### Uniqueness

* one invitation creates one outbox record;
* duplicate outbox creation is rejected.

### Status

* new record is `PENDING`;
* successful delivery becomes `DELIVERED`;
* retryable failure returns to `PENDING`;
* terminal failure becomes `FAILED`.

### Attempts

* starts at zero;
* increments per actual attempt;
* does not reset;
* stops after three failed attempts.

### Scheduling

* initial record is immediately available;
* retry uses approved backoff;
* worker does not process before `available_at`.

### Security

* raw invitation token is not persisted in outbox;
* JWTs are not persisted;
* credentials are not persisted;
* client cannot control tenant ownership.

### Concurrency

* two workers cannot concurrently claim the same record.

### Recovery

* stale `PROCESSING` records can recover;
* attempt count remains intact.

---

# 52. Implementation Constraints

Copilot or any implementation agent MUST NOT:

* introduce a second outbox architecture;
* create a generic event bus;
* introduce Kafka, RabbitMQ, Redis Streams, or another broker;
* select an email provider without approval;
* store raw invitation tokens in the outbox;
* change R6 membership-event semantics;
* change RBAC permissions;
* change Supabase authentication;
* modify frontend authorization;
* modify clinical resource ownership;
* modify plugin architecture;
* alter RLS outside the required outbox access policy;
* invent additional invitation lifecycle events.

---

# 53. Allowed Implementation Decisions

The implementation agent may choose implementation details that do not alter this contract, including:

* SQLAlchemy model organization;
* repository/service organization;
* worker process structure;
* exact SQL locking syntax;
* migration filename;
* test fixture structure;
* internal exception classes;
* provider adapter class names.

Such decisions must preserve all R7A invariants.

---

# 54. Explicitly Frozen Values

The following values are architectural decisions and MUST NOT be changed during implementation:

```text
Table:
invitation_delivery_outbox

Delivery kind:
PROFESSIONAL_INVITATION

Statuses:
PENDING
PROCESSING
DELIVERED
FAILED

Maximum automatic attempts:
3

Retry delay after attempt 1:
5 minutes

Retry delay after attempt 2:
30 minutes

Initial delivery:
immediately eligible

Outbox uniqueness:
one outbox record per invitation

Token:
raw invitation token MUST NOT be persisted in outbox

Transaction:
invitation + outbox commit atomically
```

---

# 55. Decision Summary

R7A establishes:

```text
Invitation Request
       │
       ▼
Backend Authorization
       │
       ▼
PostgreSQL Transaction
       │
       ├── Hospital Invitation
       │
       └── Delivery Outbox
              │
              ▼
            COMMIT
              │
              ▼
       Delivery Worker
              │
              ▼
   Provider-Neutral Delivery
              │
       ┌──────┴──────┐
       ▼             ▼
   SUCCESS        FAILURE
       │             │
       ▼             ▼
  DELIVERED      RETRYABLE?
                    │
             ┌──────┴──────┐
             ▼             ▼
            YES            NO
             │             │
             ▼             ▼
          PENDING        FAILED
```

---

# 56. Architectural Consequences

The decision creates a clean separation between:

```text
Identity State
```

and:

```text
Delivery State
```

Identity state is authoritative in the transactional database.

Delivery state is represented by the outbox.

External delivery is asynchronous and replaceable.

This preserves the platform principles of:

* transactionality;
* reproducibility;
* tenant isolation;
* security;
* provider independence;
* operational recoverability;
* separation of concerns.

---

# 57. Relationship to Plugin Architecture

The invitation delivery mechanism is a platform service.

It is NOT a clinical plugin.

Email delivery must not be implemented as a:

```text
Prediction Plugin
Knowledge Plugin
Risk Plugin
Rules Plugin
Reporting Plugin
Integration Plugin
```

The Plugin Manager must not become responsible for identity invitation delivery.

This preserves the architectural principle that plugins extend PharmaTrybe without modifying or owning PharmaTrybe core behavior.

---

# 58. Relationship to Future Delivery Providers

The architecture must permit:

```text
Provider A
```

to be replaced by:

```text
Provider B
```

without changing:

* invitation persistence;
* identity state;
* tenant model;
* RBAC;
* acceptance;
* outbox schema.

The provider-specific adapter remains behind the delivery abstraction.

---

# 59. Approval Gate

This historical approval gate is superseded by the approved R7A amendment. It is retained for record history only and is not an implementation authority.

R7A is:

```text
STATUS: SUPERSEDED
IMPLEMENTATION: NOT AUTHORIZED
```

The approved R7A contract is defined exclusively by:

```text
PHASE_16G_R7A_TRANSACTIONAL_OUTBOX_CONTRACT_AMENDMENT.md
```

---

# 60. Final Decision Record

```text
SLICE:
R7A

TITLE:
Transactional Outbox Contract — Invitation Delivery

STATUS:
SUPERSEDED — NOT AN IMPLEMENTATION AUTHORITY

DECISION:
Use a PostgreSQL transactional outbox for professional invitation delivery.

TRANSACTION:
Invitation + outbox record commit atomically.

DELIVERY:
External and asynchronous.

PROVIDER:
Provider-neutral abstraction.

OUTBOX:
One delivery intent per invitation.

RAW INVITATION TOKEN:
Never persisted in the outbox.

MAX ATTEMPTS:
3

RETRY:
5 minutes, then 30 minutes.

TERMINAL FAILURE:
FAILED.

INVITATION STATE:
Not automatically rolled back or revoked by delivery failure.

R6 EVENT:
Unchanged.

RBAC:
Unchanged.

AUTHENTICATION:
Unchanged.

RLS:
Unchanged except for explicitly required outbox access controls.

FRONTEND:
Unchanged.

CLINICAL RESOURCES:
Unchanged.

PLUGINS:
Unchanged.

IMPLEMENTATION:
NOT AUTHORIZED until explicit approval.
```

---

# 61. Approval

### Architectural Approval

**Approved By:** ______________________________

**Date:** _____________________________________

**Approval Status:**

```text
[ ] APPROVED

[ ] REJECTED

[ ] APPROVED WITH AMENDMENTS
```

### Amendments

```text
________________________________________________

________________________________________________

________________________________________________
```

### Final Approval Signature

```text
Name: _________________________________________

Role: __________________________________________

Date: __________________________________________
```

---

# 62. Post-Approval Rule

Once approved, this document becomes the authoritative R7A implementation contract.

Implementation agents must:

1. read this document before implementation;
2. treat frozen values as mandatory;
3. implement only the defined R7A scope;
4. add tests before production implementation;
5. preserve existing R2/R4/R5/R6 behavior;
6. run the required regression and security checks;
7. report any implementation conflict instead of inventing a new architectural decision.

If implementation reveals a requirement not defined by this document, implementation must stop and the ambiguity must be resolved through a new architectural decision rather than being silently inferred.

---

**END OF R7A DECISION DOCUMENT**

```

### Important correction before approval

I intentionally made the **outbox schema concrete** here because that was the exact architectural hole identified by the previous Copilot. I also froze the retry policy (`3 attempts`, `5 min`, `30 min`) so Copilot cannot later claim that retry behavior remains undefined.

One point deserves particular attention before you approve it: **the raw invitation token must not be duplicated into the outbox**. The implementation needs an approved way to reconstruct/send the invitation link without storing a second plaintext token. That is a security-sensitive design constraint and should remain explicit.

Also, the plugin documents you supplied reinforce the separation: plugins are extensions of PharmaTrybe and should not own core platform authentication/identity behavior. :contentReference[oaicite:0]{index=0} The SDK likewise puts platform services such as the Plugin Manager between plugins and core workflows, rather than making plugins responsible for platform infrastructure. :contentReference[oaicite:1]{index=1}

**I would approve R7A only after reviewing the frozen values in Section 54**, particularly the retry schedule and the exact outbox payload/token handling.
```
