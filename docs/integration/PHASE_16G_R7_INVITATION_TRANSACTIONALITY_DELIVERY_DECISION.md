---
# R7 — Invitation Transactionality and Delivery Architecture Decision

**Phase:** 16 / 6F Authentication and Identity  
**Slice:** R7  
**Status:** APPROVED  
**Date:** 2026-08-19  
**Implementation Status:** COMPLETE — VALIDATED  
**Depends on:** R2 Authentication, R3 Identity/Tenant Schema, R4 RBAC, R5 Authorization Context, R6 Identity Events  
**Next slice after approval:** R7 Implementation  
**Supersedes:** No previous R7 decision document exists

---

# 1. Purpose

This document defines the missing architectural contract for professional invitation creation, invitation token handling, invitation acceptance, membership creation, lifecycle events, and external invitation delivery.

R7 is intentionally separated from implementation.

No implementation decision should be inferred from the current repository merely because a behavior already exists in code.

The current implementation contains invitation behavior such as token hashing, expiry, email comparison, membership creation, and acceptance. Those behaviors are treated as **existing implementation evidence**, not automatically approved architecture.

This document establishes the contract that implementation must follow.

---

# 2. Architectural Status

At the time of original drafting, R7 was blocked because the approved Phase 16 documentation did not define:

- invitation token generation;
- token persistence;
- token hashing;
- expiry duration;
- identity binding;
- duplicate invitation semantics;
- invitation acceptance transaction boundaries;
- invitation acceptance events;
- external delivery abstraction;
- delivery failure behavior;
- retry semantics.

Those decisions must be resolved before production implementation.

The concrete transactional-outbox implementation details are now governed exclusively by the approved amendment `PHASE_16G_R7A_TRANSACTIONAL_OUTBOX_CONTRACT_AMENDMENT.md`. That amendment supersedes the historical pending statements in this section and any other R7A-specific wording in this document.

---

# 3. Existing Approved Architecture

The following principles are inherited and are NOT reopened by R7.

## 3.1 Identity Authority

Supabase Auth remains the identity/session authority.

The authenticated Supabase JWT `sub` remains the canonical authenticated user identity.

---

## 3.2 Backend Authorization Authority

FastAPI remains responsible for application authorization.

Frontend roles and permissions are presentation state only.

JWT role claims are not authorization authority.

Request-body or query-string hospital identifiers are not tenant authority.

---

## 3.3 Tenant Model

A professional has exactly one active hospital membership.

The active membership determines the professional's hospital context.

---

## 3.4 RBAC

Invitation creation is protected by:

```text
professionals:invite
````

The permission belongs to the canonical R4 permission catalogue.

Invitation role assignment must use one of the six canonical backend roles:

```text
HOSPITAL_ADMIN
CLINICIAN
PHARMACIST
LABORATORY_SCIENTIST
INFECTIOUS_DISEASE_SPECIALIST
RESEARCHER
```

The database role catalogue remains authoritative. 

---

## 3.5 Identity Schema

The existing `hospital_invitations` model contains:

```text
id
hospital_id
email
invited_by
role_code
token_hash
status
expires_at
accepted_at
created_at
```

The existing schema validates:

* hospital relationship;
* unique token hash;
* invitation status;
* expiry;
* acceptance timestamp.

No R7 decision may silently alter this schema unless a separate schema decision is approved. 

---

## 3.6 R6 Membership Event

R6 already approves:

```text
MEMBERSHIP_CREATED
```

for the initial hospital-registration membership.

R7 must define a separate event for membership creation resulting from invitation acceptance.

R6 semantics must not be changed.

---

# 4. R7 Scope

R7 covers only:

```text
Hospital administrator
        |
        | professionals:invite
        v
Invitation creation
        |
        v
Secure invitation token
        |
        v
External delivery abstraction
        |
        v
Authenticated invitee
        |
        v
Invitation acceptance
        |
        v
Professional profile
        |
        v
Hospital membership
        |
        v
Canonical role
        |
        v
Membership lifecycle event
```

R7 does NOT cover:

* frontend session lifecycle;
* frontend route guards;
* RLS;
* clinical resource ownership;
* persistent audit architecture;
* plugin authorization;
* clinical authorization;
* general email infrastructure;
* password recovery;
* account deactivation;
* invitation UI redesign.

Those remain later boundaries.

---

# 5. Invitation Creation Contract

## 5.1 Authorization

Only an authenticated professional whose database-backed authorization context grants:

```text
professionals:invite
```

may create an invitation.

The hospital/tenant is obtained from the authenticated user's active membership.

The client MUST NOT choose the authoritative hospital through:

```text
hospital_id
organization_id
tenant_id
```

in the request body or query string.

---

# 6. Invitation Role Contract

The requested invitation role must be validated against the canonical R4 role catalogue.

Invalid or unknown role codes MUST fail closed.

The system MUST NOT:

* invent roles;
* accept arbitrary role strings;
* trust frontend role definitions;
* trust JWT role claims.

---

# 7. Token Contract

## 7.1 Proposed Decision

**APPROVED**

Each invitation shall use a cryptographically secure random opaque token.

The implementation SHOULD generate at least:

```text
32 random bytes
```

and encode the resulting token using a URL-safe representation.

The raw token is the secret presented through the invitation link.

---

## 7.2 Raw Token Persistence

The raw invitation token MUST NOT be persisted in the database.

Only a cryptographic hash of the token shall be persisted:

```text
token
   |
   v
SHA-256
   |
   v
token_hash
```

The existing schema already provides `token_hash` and does not provide a raw-token column. 

---

## 7.3 Token Exposure

The raw token may be returned only as part of the invitation-delivery operation required to construct the invitation URL.

It MUST NOT:

* be logged;
* be stored in application logs;
* be stored in `membership_events.details`;
* be stored in audit metadata;
* be returned by invitation lookup endpoints;
* be persisted in plaintext.

---

# 8. Invitation Expiry

## Proposed Decision

**APPROVED**

Invitation validity period:

```text
7 days
```

`expires_at` shall be stored as an absolute timestamp.

All expiry comparisons shall use UTC-aware timestamps.

An invitation is invalid when:

```text
now >= expires_at
```

An expired invitation MUST NOT be accepted.

The seven-day value currently exists in implementation, but this document intentionally converts it from implementation behavior into an explicit architectural decision only if approved.

---

# 9. Invitation Status

The invitation lifecycle shall distinguish at minimum:

```text
PENDING
ACCEPTED
EXPIRED
```

## PENDING

The invitation has been created and has not been accepted or invalidated.

## ACCEPTED

The invitation has been successfully consumed.

`accepted_at` records the acceptance timestamp.

## EXPIRED

The invitation's validity period has elapsed.

An expired invitation cannot be accepted.

---

# 10. Identity Binding

## Proposed Decision

**APPROVED**

Invitation acceptance requires an authenticated Supabase identity.

The authenticated identity's email shall be compared with the invitation email.

The comparison shall be normalized consistently before comparison.

Conceptually:

```text
authenticated Supabase identity
        |
        v
authenticated email
        |
        | must match
        v
invitation.email
```

A mismatch MUST result in rejection.

The client MUST NOT be allowed to substitute another:

```text
auth_user_id
professional_id
hospital_id
```

to bypass this binding.

---

# 11. Existing Professional Profile

Acceptance MUST NOT silently create a second professional profile for an authenticated identity that already has a profile.

If the authenticated `auth_user_id` already has a professional profile, acceptance shall fail closed unless a separately approved account-linking workflow exists.

R7 does not introduce account merging.

---

# 12. Existing Active Membership

Because the approved identity architecture permits only one active hospital membership per professional, acceptance MUST verify the existing membership state before creating a new active membership.

If the professional already has an active hospital membership:

```text
REJECT
```

The system MUST NOT create a second active membership.

The existing database constraint remains an additional safety boundary.

---

# 13. Duplicate Invitation Semantics

## Proposed Decision

**APPROVED**

A duplicate invitation means:

> A `PENDING` invitation exists for the same normalized email address within the same hospital.

If such an invitation exists, creation shall fail with a conflict response rather than silently creating another pending invitation.

Recommended behavior:

```text
HTTP 409 Conflict
```

The response MUST NOT expose invitation tokens.

---

## 13.1 Different Hospital

A pending invitation to the same email from another hospital is not automatically cancelled or overwritten.

The invitation remains associated with its originating hospital.

Acceptance is still subject to:

* authenticated identity binding;
* one-active-membership rule;
* invitation validity;
* canonical role validation.

---

## 13.2 Accepted Invitations

An accepted invitation is not considered a pending duplicate.

A new invitation MUST nevertheless fail if accepting it would violate the professional's one-active-membership rule.

---

## 13.3 Expired Invitations

Expired invitations do not block creation of a new pending invitation.

The implementation may either:

* explicitly transition the old invitation to `EXPIRED`; or
* treat it as expired during duplicate evaluation.

No additional lifecycle state should be invented without approval.

---

# 14. Invitation Acceptance Transaction

Invitation acceptance MUST be atomic.

The following operations belong to one database transaction:

```text
BEGIN
    |
    +-- validate invitation
    |
    +-- validate expiry
    |
    +-- validate authenticated identity
    |
    +-- validate existing professional profile
    |
    +-- create professional profile
    |
    +-- create hospital membership
    |
    +-- assign canonical role
    |
    +-- create membership lifecycle event
    |
    +-- mark invitation ACCEPTED
    |
COMMIT
```

If any required operation fails:

```text
ROLLBACK
```

No partial identity graph may remain.

---

# 15. Acceptance Ordering

The implementation SHOULD perform validation before creating persistent identity state.

Conceptually:

```text
1. Authenticate
2. Resolve invitation
3. Validate token
4. Validate invitation status
5. Validate expiry
6. Validate email binding
7. Validate canonical role
8. Validate existing identity/membership constraints
9. Create profile
10. Create membership
11. Assign role
12. Create membership event
13. Mark invitation accepted
14. Commit
```

The exact SQL statement ordering may vary provided the transaction remains atomic and all required invariants are enforced.

---

# 16. Invitation Acceptance Event

## Proposed Decision

**APPROVED**

Successful invitation acceptance shall create exactly one:

```text
MEMBERSHIP_CREATED_FROM_INVITATION
```

event.

This is deliberately distinct from the R6 event:

```text
MEMBERSHIP_CREATED
```

which represents initial hospital registration.

---

# 17. Event Actor

The event actor shall be the authenticated Supabase identity:

```text
actor_user_id = JWT sub
```

The actor MUST NOT come from:

* request body;
* query string;
* frontend state;
* invitation payload;
* role claim.

---

# 18. Event References

The event shall contain:

```text
membership_id
hospital_id
actor_user_id
event_type
details
created_at
```

using the existing `membership_events` schema.

---

# 19. Event Details

## Proposed Event Details

**APPROVED**

```json
{
  "event": "MEMBERSHIP_CREATED_FROM_INVITATION",
  "source": "invitation_acceptance",
  "role_code": "<canonical role>"
}
```

No sensitive authentication material may appear in the event.

Specifically prohibited:

```text
raw invitation token
token hash
JWT
access token
refresh token
password
secret
```

---

# 20. Event Atomicity

The membership event MUST be inserted into the same transaction as:

* professional profile creation;
* membership creation;
* role assignment;
* invitation acceptance.

If event insertion fails:

```text
ROLLBACK
```

The invitation MUST remain unaccepted and no partial membership may survive.

---

# 21. Invitation Delivery Architecture

## 21.1 Separation of Concerns

Invitation creation and external delivery MUST be separated.

The application domain operation is:

```text
CreateInvitation
```

The external operation is:

```text
DeliverInvitation
```

The invitation service MUST NOT directly depend on a specific email provider.

---

# 22. Delivery Abstraction

## Proposed Decision

**APPROVED**

Introduce an application-level delivery abstraction conceptually equivalent to:

```python
InvitationDelivery
```

or:

```python
InvitationDeliveryService
```

The domain layer should depend on the abstraction rather than:

```text
Resend
SendGrid
SES
SMTP
Mailgun
```

or another concrete provider.

The concrete provider can be selected later.

---

# 23. Delivery Payload

The delivery abstraction should receive only the information required to construct and send the invitation.

Conceptually:

```text
recipient_email
invitation_url
hospital_name
role
expires_at
```

The raw token may be used to construct the URL in memory but MUST NOT be logged or persisted.

---

# 24. Outbox Decision

## Proposed Decision

**APPROVED**

R7 should use a transactional outbox pattern if reliable asynchronous external delivery is required.

Conceptually:

```text
Database Transaction
        |
        +-- invitation
        |
        +-- membership state
        |
        +-- lifecycle event
        |
        +-- delivery/outbox record
        |
        COMMIT
             |
             v
       Delivery Worker
             |
             v
       Email Provider
```

The database transaction therefore establishes the durable fact that delivery is required.

External email transmission does NOT occur inside the database transaction.

---

# 25. Delivery Failure

External delivery failure MUST NOT partially roll back an already committed identity transaction.

The preferred architecture is:

```text
identity transaction
        |
        v
durable delivery intent
        |
        v
commit
        |
        v
asynchronous delivery
```

If delivery fails:

```text
delivery status = FAILED
```

and the delivery mechanism may retry according to the approved retry policy.

The invitation itself remains a valid pending invitation until:

* accepted;
* expired;
* explicitly invalidated by an approved future workflow.

---

# 26. Retry Policy

The retry policy, failure classification, maximum attempts, retry intervals, and terminal failure behavior are defined exclusively by the approved R7A amendment:

`PHASE_16G_R7A_TRANSACTIONAL_OUTBOX_CONTRACT_AMENDMENT.md`

R7 does not add or reinterpret those values.

---

# 27. Provider Selection

R7 does NOT approve a specific external email provider.

Provider selection remains an implementation/deployment concern.

The architecture must remain provider-neutral.

No provider SDK should become part of the authorization or identity domain model.

---

# 28. Delivery and Authorization Boundary

External delivery MUST NOT become an authorization authority.

The delivery provider must never determine:

* hospital;
* membership;
* role;
* authorization;
* actor identity;
* tenant.

Those values remain database/application controlled.

---

# 29. Security Requirements

R7 implementation MUST preserve the following:

### MUST

* require authenticated authorization for invitation creation;
* derive tenant from the authenticated membership;
* validate canonical roles;
* use cryptographically secure invitation tokens;
* persist only token hashes;
* enforce expiry;
* bind acceptance to the authenticated identity;
* prevent multiple active memberships;
* atomically create the identity graph;
* atomically record the acceptance membership event;
* avoid logging secrets;
* avoid exposing tokens through normal API responses;
* fail closed on invalid invitation state.

### MUST NOT

* trust frontend permissions;
* trust JWT role claims;
* trust client-supplied hospital IDs;
* persist raw invitation tokens;
* place invitation tokens in membership events;
* create arbitrary roles;
* create multiple active memberships;
* send email synchronously inside the database transaction;
* make an email provider an authorization authority.

---

# 30. API Semantics

R7 implementation must preserve the existing approved route surface.

No speculative endpoints may be introduced.

The existing invitation operations are the implementation target.

Any new endpoint requires a separate API contract decision.

---

# 31. Error Semantics

The implementation should fail closed.

At minimum:

| Condition                     | Expected result                              |
| ----------------------------- | -------------------------------------------- |
| Missing authentication        | `401`                                        |
| Missing invitation permission | `403`                                        |
| Unknown role                  | `400/422`                                    |
| Invalid token                 | `400/404` according to approved API contract |
| Expired invitation            | rejection                                    |
| Already accepted invitation   | rejection                                    |
| Email mismatch                | rejection                                    |
| Existing professional profile | rejection                                    |
| Existing active membership    | rejection                                    |
| Duplicate pending invitation  | `409`                                        |
| Transaction failure           | rollback / server error                      |

Exact public error-body wording is an API implementation concern and must not reveal sensitive invitation state unnecessarily.

---

# 32. Concurrency Requirements

Invitation acceptance must be safe against concurrent requests.

Two simultaneous acceptance attempts for the same invitation MUST NOT result in:

```text
two memberships
two role assignments
two successful acceptances
```

The implementation must rely on transactional database semantics and existing uniqueness constraints rather than an application-only boolean check.

---

# 33. Observability

R7 must not log:

```text
raw invitation token
JWT
access token
refresh token
password
secrets
```

Safe operational metadata may include:

```text
invitation_id
hospital_id
role_code
delivery status
event type
failure category
timestamps
```

provided these fields do not expose authentication material.

---

# 34. Testing Contract

Before production implementation is considered complete, focused tests MUST cover:

## Invitation creation

* authorized administrator can create an invitation;
* unauthorized user cannot create an invitation;
* tenant comes from authorization context;
* client-supplied hospital ID cannot override tenant context;
* canonical role validation is enforced;
* token hash is persisted;
* raw token is not persisted.

## Expiry

* valid invitation can be accepted;
* expired invitation is rejected;
* expiry comparison is timezone-safe.

## Identity binding

* matching authenticated email succeeds;
* mismatched authenticated email fails;
* client-supplied identity cannot override JWT `sub`.

## Duplicate handling

* duplicate pending invitation is rejected;
* expired invitation does not permanently block a new invitation;
* accepted invitation is not treated as pending.

## Acceptance

* profile is created;
* membership is created;
* membership is ACTIVE;
* canonical role is assigned;
* invitation becomes ACCEPTED;
* `accepted_at` is populated.

## Transactionality

If any of:

```text
profile creation
membership creation
role assignment
event creation
invitation acceptance
```

fails:

```text
ROLLBACK
```

must occur.

No partial identity state may survive.

## Event

Exactly one:

```text
MEMBERSHIP_CREATED_FROM_INVITATION
```

event must be created.

The event must contain the correct:

```text
membership_id
hospital_id
actor_user_id
role_code
source
```

and must not contain authentication secrets.

## Delivery

* invitation delivery is invoked through the abstraction;
* provider implementation is not coupled to authorization;
* delivery failure does not create a false successful-delivery state;
* delivery is not performed inside the database transaction if the outbox architecture is approved.

## Concurrency

* two simultaneous acceptance attempts cannot produce two successful memberships.

---

# 35. Explicit Non-Changes

R7 MUST NOT modify:

```text
Supabase JWT verification architecture
R4 RBAC catalogue
R5 AuthorizationContext semantics
R6 MEMBERSHIP_CREATED semantics
Frontend authentication/session lifecycle
RLS
Clinical resource ownership
Persistent audit architecture
Plugin authorization
Clinical recommendation authorization
WHO/global knowledge scope
```

---

# 36. Migration Policy

No database migration should be created merely to implement behavior already supported by the approved schema.

A migration is required only if the approved R7 contract introduces a schema requirement not already represented by the identity schema.

The approved outbox schema is defined by `PHASE_16G_R7A_TRANSACTIONAL_OUTBOX_CONTRACT_AMENDMENT.md` before migration work begins.

No migration should be invented by implementation tooling.

---

# 37. Decision Classification

The following decisions are inherited and already approved:

| Decision                                                    | Status                           |
| ----------------------------------------------------------- | -------------------------------- |
| Supabase Auth is identity authority                         | APPROVED                         |
| JWT `sub` is authenticated identity                         | APPROVED                         |
| FastAPI is authorization authority                          | APPROVED                         |
| One active hospital membership                              | APPROVED                         |
| `professionals:invite`                                      | APPROVED                         |
| Canonical role catalogue                                    | APPROVED                         |
| Hospital-bound invitations                                  | APPROVED                         |
| Existing `hospital_invitations` schema                      | APPROVED                         |
| R6 `MEMBERSHIP_CREATED` event                               | APPROVED                         |
| R7 invitation acceptance must be transactionally consistent | APPROVED ARCHITECTURAL PRINCIPLE |

The following are NEW R7 decisions approved for implementation:

| Decision                     | Proposed value                       | Status  |
| ---------------------------- | ------------------------------------ | ------- |
| Token entropy                | ≥32 random bytes                     | APPROVED |
| Token persistence            | SHA-256 hash only                    | APPROVED |
| Expiry                       | 7 days                               | APPROVED |
| Time semantics               | UTC                                  | APPROVED |
| Identity binding             | authenticated email                  | APPROVED |
| Duplicate pending invitation | reject with conflict                 | APPROVED |
| Existing profile             | reject / no account merging          | APPROVED |
| Existing active membership   | reject                               | APPROVED |
| Acceptance event             | `MEMBERSHIP_CREATED_FROM_INVITATION` | APPROVED |
| Event details                | source + role code + event           | APPROVED |
| Delivery abstraction         | provider-neutral abstraction         | APPROVED |
| Delivery architecture        | transactional outbox                 | APPROVED |
| Email transmission           | outside DB transaction               | APPROVED |
| Delivery failure             | retryable delivery state             | APPROVED |
| Specific provider            | none approved                        | APPROVED |
| Exact retry limits           | defined by approved R7A amendment     | APPROVED |

---

# 38. Approval Gate

R7 implementation is authorized because the project owner approved the decisions in Section 37.

The approved values cover:

1. token generation;
2. token hashing;
3. expiry;
4. identity binding;
5. duplicate invitation behavior;
6. existing-profile behavior;
7. existing-membership behavior;
8. acceptance transaction boundary;
9. acceptance event type;
10. event payload;
11. delivery abstraction;
12. outbox requirement;
13. delivery failure semantics.

---

# 39. Implementation Rule After Approval

Once approved, the implementation agent MUST follow this sequence:

```text
1. Read this approved R7 contract.
2. Read all relevant Phase 16 integration documents.
3. Inspect the existing invitation implementation.
4. Write focused R7 tests first.
5. Confirm the tests fail only because of the identified R7 gaps.
6. Make the smallest production changes required.
7. Do not modify R8 or later boundaries.
8. Run focused R7 tests.
9. Run R2 regression tests.
10. Run R4 RBAC regression tests.
11. Run R5 authorization regression tests.
12. Run R6 identity-event regression tests.
13. Run compilation/type/static checks.
14. Run security searches.
15. Review the exact diff.
16. Stop at the R7 gate.
```

The implementation agent MUST NOT reinterpret this document or introduce additional security/lifecycle semantics without approval.

---

# 40. R7 Architectural Principle

The invitation system is an identity-provisioning workflow, not an email feature.

The authoritative sequence is:

```text
Authenticated Administrator
          |
          v
Database AuthorizationContext
          |
          v
Hospital-bound Invitation
          |
          v
Secure Time-limited Token
          |
          v
Authenticated Invitee
          |
          v
Identity Binding
          |
          v
Atomic Identity/Membership Transaction
          |
          +--> Professional Profile
          |
          +--> Active Hospital Membership
          |
          +--> Canonical Role
          |
          +--> Membership Lifecycle Event
          |
          +--> Invitation Accepted
          |
          v
Durable Delivery / Notification Mechanism
```

External email delivery is a transport mechanism.

It is not the source of truth for identity, membership, tenant, or authorization.

---

# 41. Final Gate

```text
SLICE: R7
STATUS: CLOSED

IMPLEMENTATION: COMPLETE

R2: PRESERVED
R4: PRESERVED
R5: PRESERVED
R6: PRESERVED

R8: NOT STARTED
R9: NOT STARTED
R10: NOT STARTED
R11: NOT STARTED

NO FRONTEND CHANGES
NO RLS CHANGES
NO CLINICAL OWNERSHIP CHANGES
NO PLUGIN SECURITY CHANGES

IMPLEMENTATION GATE CLOSED
```

```

### Historical review notes — superseded

The following notes are retained as historical context only. They are not implementation authority and are superseded by the approved R7A amendment.

There are **three decisions I would pay particular attention to before approving**:

1. **`MEMBERSHIP_CREATED_FROM_INVITATION` vs another event name.**  
   This is deliberately separate from R6's `MEMBERSHIP_CREATED`, so the lifecycle history can distinguish direct hospital registration from invitation-based membership creation.

2. **Email binding.**  
        The current implementation compares authenticated email to invitation email. The approved R7 contract defines the identity-binding behavior above; this historical note must not be interpreted as a pending decision.

3. **Outbox.**
        The approved R7A amendment now defines the provider-neutral delivery abstraction, transactional outbox, schema, lifecycle, retry policy, and recovery contract. This historical recommendation is superseded.

The underlying architecture already treats invitation/provisioning as part of the identity/membership dependency chain, while the existing schema already provides the invitation and membership-event persistence structures. :contentReference[oaicite:5]{index=5} :contentReference[oaicite:6]{index=6}
