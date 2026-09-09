# Phase 16G — R7A-11 Secure Invitation Token Handoff Decision

## 1. Document Status

**STATUS: APPROVED**

**IMPLEMENTATION: AUTHORIZED**

**Decision Classification:** Security / Transactional Delivery Architecture Amendment

**Decision ID:** R7A-11

This document is the approved amendment for R7A-11. It authorizes implementation only within the mechanism and lifecycle defined here.

---

## 2. Relationship to R7 and R7A

This document amends the token-handoff portion of:

```text
PHASE_16G_R7A_TRANSACTIONAL_OUTBOX_CONTRACT_AMENDMENT.md
```

It resolves a security and lifecycle gap discovered during R7 implementation-readiness validation.

The following remain authoritative and unchanged:

- R7 invitation creation and acceptance decisions;
- R7A-1 through R7A-10, except for the token-handoff details explicitly amended after approval of this document;
- Supabase Auth as the identity authority;
- FastAPI/backend authorization;
- JWT `sub` as the authenticated actor identity;
- canonical RBAC and `professionals:invite`;
- the one-active-membership invariant;
- the SHA-256 invitation-token hash requirement;
- the seven-day invitation expiry;
- the transactional invitation-plus-outbox boundary;
- external delivery outside the database transaction.

The superseded R7A document is not an authority for this decision.

---

## 3. Problem Statement

The approved R7A contract requires all of the following:

1. R7A-5 requires the provider-neutral delivery abstraction to receive an invitation URL.
2. R7A-6 assigns invitation-link construction to the asynchronous delivery worker.
3. R7A-10 requires the invitation URL to contain the opaque raw invitation token.
4. R7A-10 prohibits persisting the raw token in database columns, outbox payloads, logs, audit records, analytics, telemetry, and error messages.
5. The invitation record persists only the SHA-256 hash of the token.
6. A SHA-256 hash cannot recover the original token.
7. R7A requires retries and stale `PROCESSING` recovery.

Before this amendment, the contract had no approved mechanism by which a post-commit worker could obtain the raw token needed to construct the invitation URL.

This is a genuine security and lifecycle blocker. It must not be resolved by storing the raw token in the outbox, invitation table, event payload, JWT claims, frontend state, logs, or an undocumented encryption scheme.

---

## 4. Existing Approved Constraints

The approved architecture requires:

- raw invitation tokens are generated as cryptographically secure opaque values;
- at least 32 random bytes are recommended by R7;
- only the SHA-256 hash is persisted in `hospital_invitations.token_hash`;
- raw tokens are never logged or returned through ordinary invitation APIs;
- raw tokens are never stored in `membership_events.details`;
- the outbox payload contains no raw token;
- the outbox remains a durable delivery-intent record, not a secret store;
- the outbox uses the approved `PENDING`, `PROCESSING`, `SENT`, and `FAILED` lifecycle;
- delivery attempts are bounded at three attempts;
- retry delays are one minute after attempt one and five minutes after attempt two;
- stale `PROCESSING` records use the approved 15-minute threshold;
- delivery workers are backend-controlled and must not use client-supplied tenant authority;
- external delivery occurs only after the identity/outbox transaction commits;
- the invitation remains governed by the seven-day expiry and existing acceptance validation;
- the delivery provider remains behind the provider-neutral abstraction.

No requirement in this document weakens or replaces those constraints.

---

## 5. Security Requirements

Any approved R7A-11 mechanism MUST:

1. keep the raw token out of `hospital_invitations`;
2. keep the raw token out of `invitation_delivery_outbox` and its JSONB payload;
3. keep the raw token out of `membership_events`;
4. keep the raw token out of normal application logs;
5. keep the raw token out of analytics, telemetry, traces, and monitoring labels;
6. keep the raw token out of API responses except the approved delivery boundary;
7. keep the raw token out of ordinary database query results and operational tooling;
8. prevent client-controlled token retrieval;
9. preserve Supabase Auth as the identity authority;
10. preserve FastAPI/backend authority for delivery processing;
11. enforce hospital and invitation ownership on every handoff operation;
12. provide a bounded lifetime for any temporary secret material;
13. support auditable access without recording the secret itself;
14. define behavior for retries, crashes, duplicate claims, and delivery failure;
15. never reconstruct the raw token from its hash;
16. avoid introducing a second long-lived invitation-token store.

---

## 6. Alternatives Considered

### 6.1 Option A — Short-Lived Encrypted Token Material Stored Separately

A separate persistence mechanism could store encrypted token material for a bounded period. The outbox would contain only an opaque reference.

**Security properties:** Confidentiality would depend on encryption-key ownership, key rotation, access control, ciphertext retention, and protection against replay. The plaintext raw token would not be stored in the outbox.

**Lifecycle:** The mechanism would need explicit creation, expiration, read, deletion, and crash-recovery rules.

**Retry implications:** It could preserve the same invitation token across the approved retry window, but the contract must define whether reads are replayable, single-use, or lease-based.

**Worker access:** A backend-only worker would need an approved authorization path and a defined key-management boundary.

**Failure behavior:** Missing ciphertext, decryption failure, expiry, and key-service failure would require explicit failure classifications.

**Operational complexity:** High. It introduces encrypted secret storage and key-management obligations not currently defined by R7A.

**Compatibility:** Potentially compatible with R7A, but not approved by the existing documents.

**Status:** NOT SELECTED. Requires an explicit architecture decision.

### 6.2 Option B — Dedicated Secure Ephemeral Token Store

A backend-controlled ephemeral store could hold the raw token for a bounded lifetime. The outbox would reference it through an opaque handoff identifier.

**Security properties:** The raw token could remain outside the database outbox and invitation tables. Security would depend on store isolation, access control, retention, memory/disk behavior, and reference secrecy.

**Lifecycle:** The contract would need explicit expiration, read, deletion, and recovery behavior.

**Retry implications:** A strictly one-time read could lose the token if a worker crashes before delivery. A replayable or lease-based read could support retries but would require precise idempotency and ownership semantics.

**Worker access:** Only trusted backend worker infrastructure could retrieve the material. Client access must be denied.

**Failure behavior:** The contract would need to define whether missing or expired material causes terminal failure, requeue, or another controlled state.

**Operational complexity:** Moderate to high. It introduces a new secure infrastructure dependency.

**Compatibility:** Potentially compatible with R7A, but the existing architecture does not approve a particular ephemeral store or its security model.

**Status:** NOT SELECTED. Requires an explicit architecture decision.

### 6.3 Option C — Backend-Only Secure Handoff Service or Interface

Invitation creation could pass the raw token to a backend-only handoff component, which would later provide it to the worker under controlled authorization. The outbox would retain only an opaque reference.

**Security properties:** The secret boundary could be isolated behind a narrowly defined interface. Security would depend on the service's storage, lifetime, authorization, and audit semantics.

**Lifecycle:** The service would need defined creation, reference binding, expiration, retrieval, deletion, and recovery behavior.

**Retry implications:** The interface could support a lease or bounded replay model, but that behavior is not defined by the approved R7A contract.

**Worker access:** Retrieval could be restricted to the delivery worker and bound to the outbox ID, invitation ID, and hospital ID.

**Failure behavior:** The service would need defined behavior for unavailable, expired, already-consumed, or mismatched handoffs.

**Operational complexity:** Potentially lower than a general-purpose secret store if implemented as a narrow platform boundary, but it still introduces an architectural component and security contract.

**Compatibility:** Potentially compatible with R7A, but no such service or interface is currently approved.

**Status:** NOT SELECTED. Requires an explicit architecture decision.

### 6.4 Option D — Another Existing-Architecture Mechanism

An existing approved platform component could provide the handoff without adding a new secret store or changing token hashing.

**Security properties, lifecycle, retry behavior, worker access, and failure behavior:** These would depend on the identified component and would need to be documented before approval.

**Operational complexity:** Unknown until an existing approved component is identified.

**Compatibility:** Cannot be established from the current R7/R7A documents.

**Status:** NOT SELECTED. No qualifying existing mechanism has been identified during readiness validation.

---

## 7. Selected Decision

The approved mechanism is a **backend-only ephemeral handoff service**.

The service stores the raw invitation token in protected temporary storage encrypted at rest. The transactional outbox stores only an opaque handoff reference bound to the invitation, hospital, and outbox record.

The handoff is replayable by the authorized delivery worker until the earlier of successful delivery or the invitation's seven-day expiry. Successful delivery destroys or makes the handoff unusable.

Only the trusted backend delivery worker may retrieve the handoff. The frontend, client, ordinary authenticated users, external provider, and invitation API consumers must not retrieve it.

The same outbox record and invitation token are reused across retries. A worker crash after retrieval does not consume the handoff; R7A stale `PROCESSING` recovery and bounded attempt limits remain authoritative.

```text
R7A-11 STATUS: APPROVED
R7A-11 IMPLEMENTATION: AUTHORIZED
R7 IMPLEMENTATION: AUTHORIZED
```

---

## 8. R7A-11 Contract

The following contract is approved for implementation.

### R7A-11.1 Secure Mechanism

The backend-only ephemeral handoff service carries the raw token from invitation creation to post-commit delivery processing without persisting it in the invitation or outbox.

### R7A-11.2 Temporary Storage

Temporary token material resides in the handoff service's protected ephemeral storage, encrypted at rest and separate from the invitation and outbox tables.

### R7A-11.3 Protection Model

The material is ephemeral in lifecycle, encrypted at rest, protected in transit, access-controlled to trusted backend worker infrastructure, and retained only until successful delivery or invitation expiry, whichever occurs first.

### R7A-11.4 Reader Authorization

Only the trusted backend delivery worker may read temporary token material. The client, frontend, ordinary authenticated user, invitation API, and external provider must not retrieve it directly.

### R7A-11.5 Creation Owner

The invitation creation service, operating within the approved invitation transaction boundary, owns creation of the handoff material and opaque handoff reference.

### R7A-11.6 Retrieval Owner

The delivery worker owns retrieval through the handoff service interface. It must validate the outbox reference, invitation identity, hospital identity, and worker authority before retrieval.

### R7A-11.7 Outbox Reference

The outbox contains only a non-secret opaque handoff reference associated with the delivery intent. It must not contain the raw token, a reversible token encoding, or secret-bearing payload data. The reference is not a tenant or authorization authority.

### R7A-11.8 Retrieval Semantics

Retrieval is replayable to the authorized worker until successful delivery or invitation expiry. Duplicate processing remains prevented by the R7A atomic outbox claim and idempotency key. A worker crash before or during delivery is recovered through R7A stale `PROCESSING` recovery without consuming the handoff.

### R7A-11.9 Successful Delivery

After the provider reports success, the worker must mark the outbox `SENT` according to R7A-2. Temporary token material must be destroyed, revoked, or made unusable according to the approved mechanism. The raw token must not be returned in the API response or persisted as a delivery result.

### R7A-11.10 Delivery Failure

A delivery failure must follow R7A-8 classification and R7A-3 retry scheduling. Temporary token material must remain available only as necessary for the approved retry lifecycle and must remain bounded by its approved lifetime.

### R7A-11.11 Expiration

The handoff lifetime is bounded by the seven-day invitation expiry. It expires no later than `expires_at`, is destroyed or made unusable on successful delivery, and never extends invitation validity.

### R7A-11.12 Worker Crash After Retrieval

The handoff remains replayable after a crash following retrieval, subject to the seven-day expiry and the R7A attempt limit. The crash does not permanently lose delivery intent or create an unbounded secret.

### R7A-11.13 Retry

A retry uses the same invitation and the same raw token through the handoff service. It must not issue a replacement invitation merely because delivery failed. Replay remains available through the R7A retry and stale-`PROCESSING` recovery lifecycle, without placing the raw token in the outbox.

### R7A-11.14 Leakage Prevention

The implementation must redact or exclude raw tokens and invitation URLs containing raw tokens from logs, responses, SQL inspection surfaces, event payloads, errors, traces, analytics, and telemetry. Handoff access is auditable through non-secret identifiers and outcome metadata only.

### R7A-11.15 SHA-256 Hash Interaction

The existing `hospital_invitations.token_hash` remains the sole persistent invitation-verification representation. The handoff must not replace, duplicate, reverse, or weaken SHA-256 verification. The raw token must continue to be verified by hashing the presented token and comparing it with `token_hash`.

### R7A-11.16 Seven-Day Expiry

The invitation remains valid for seven days and is invalid when `now >= expires_at`. Handoff expiration must be bounded independently and must never make an expired invitation acceptable. A valid handoff does not bypass invitation expiry or identity binding.

---

## 9. Data Model Impact

No raw-token column or outbox token field is authorized by this amendment.

The implementation must use an opaque handoff reference in the outbox and must not add raw-token persistence. The concrete protected-storage technology is an implementation detail only if it preserves this contract and does not introduce a second long-lived token store.

The existing `hospital_invitations.token_hash` requirement remains unchanged.

---

## 10. Outbox Integration

The outbox transaction remains:

```text
BEGIN
    invitation with token_hash
    outbox delivery intent
    opaque handoff reference only, if approved
COMMIT
```

The outbox must never contain:

- the raw invitation token;
- an invitation URL containing the raw token;
- a reversible encoding of the token;
- encryption material that enables unauthorized recovery;
- a secret-bearing event or payload.

The outbox must retain the approved idempotency key and lifecycle fields from R7A-1. Any handoff reference must be bound to the same invitation and hospital and must not become an alternate tenant authority.

---

## 11. Worker Integration

After commit, the backend delivery worker remains responsible for:

1. atomically claiming the eligible outbox record;
2. incrementing `attempt_count` before delivery;
3. authorizing handoff retrieval through backend-controlled worker authority;
4. retrieving the raw token only through the approved R7A-11 mechanism;
5. constructing the approved invitation URL in memory;
6. calling the provider-neutral delivery abstraction;
7. recording only safe result and failure metadata;
8. destroying, releasing, or retaining temporary material according to the approved lifecycle;
9. transitioning the outbox according to R7A-2 and R7A-3.

The worker must not obtain the token from a client, frontend, JWT claim, invitation query response, event payload, or token hash.

---

## 12. Retry and Recovery

R7A-11 must be compatible with these approved transitions:

```text
PENDING -> PROCESSING -> SENT
PENDING -> PROCESSING -> PENDING -> PROCESSING -> SENT
PENDING -> PROCESSING -> FAILED
PROCESSING -> PENDING after approved stale recovery
PROCESSING -> FAILED after the approved attempt limit
```

A delivery retry must not create a new invitation or a new invitation token. The same invitation token must remain available through the approved secure mechanism for the permitted retry lifecycle.

The current R7A retry values remain unchanged:

- maximum attempts: 3;
- retry after attempt 1 failure: 1 minute;
- retry after attempt 2 failure: 5 minutes;
- stale `PROCESSING` threshold: 15 minutes.

Temporary token material remains replayable after a read, worker crash, provider timeout, or ambiguous provider result until successful delivery or invitation expiry. Provider failure classification and attempt transitions remain governed by R7A-3 and R7A-8.

---

## 13. Security and Privacy

The handoff mechanism must preserve separation between:

```text
persistent invitation verification: SHA-256 token_hash
secure delivery handoff: temporary raw token material
outbox: non-secret delivery intent
external provider call: invitation URL delivery boundary
```

The raw token must not appear in:

- database columns or JSONB payloads;
- SQL query results or ordinary operational inspection;
- API responses;
- membership events or audit records;
- logs, exception messages, traces, analytics, or telemetry;
- frontend state or URL visible to application code beyond the approved invitation route;
- JWT claims or authorization context.

The worker must preserve hospital isolation and must not retrieve a handoff belonging to another invitation or hospital.

---

## 14. Failure Modes

The approved mechanism must define behavior for each case below:

| Failure mode | Required architectural outcome |
|---|---|
| Worker crashes before token retrieval | Outbox remains recoverable; no secret is leaked; approved stale recovery applies. |
| Worker crashes after token retrieval but before delivery | Temporary material remains replayable to the authorized worker until successful delivery or invitation expiry; retry remains deterministic and bounded. |
| Provider delivery failure | Classify as `RETRYABLE` or `NON_RETRYABLE` under R7A-8; preserve invitation state. |
| Handoff expires before delivery | Mark the delivery record `FAILED` with a safe handoff-expired error; do not bypass invitation expiry or create a replacement token. |
| Handoff is missing | Mark the delivery record `FAILED` with a safe handoff-unavailable error; never reconstruct from the hash. |
| Duplicate worker claim | Database claim semantics prevent concurrent processing. |
| Retry of the same outbox record | Reuse the same invitation and token through the approved handoff mechanism; do not create a new invitation. |
| Invitation reaches seven-day expiry | Acceptance must fail when `now >= expires_at`, regardless of handoff state. |

These outcomes are part of the approved R7A-11 handoff contract.

---

## 15. Observability

Safe operational metadata may include:

- outbox ID;
- invitation ID;
- hospital ID where authorized;
- idempotency key;
- status;
- attempt count;
- failure classification;
- safe error code;
- timestamps;
- handoff reference metadata only if it is non-secret and approved for observability.

The following must never be logged, emitted, or used as telemetry dimensions:

- raw invitation token;
- invitation URL containing the raw token;
- token hash where it could enable correlation or disclosure beyond the approved boundary;
- access token or refresh token;
- JWT;
- password;
- encryption key;
- provider credential;
- secret-bearing handoff material.

Auditing must record access events without recording the secret value.

---

## 16. Backward Compatibility

This approved amendment preserves:

- the existing SHA-256 `token_hash` storage requirement;
- the seven-day invitation expiry;
- authenticated email binding;
- canonical invitation roles;
- the invitation acceptance transaction;
- the R7A outbox schema and lifecycle unless a later approved amendment explicitly authorizes a reference change;
- provider-neutral delivery;
- external delivery after database commit.

It does not authorize a raw-token column, a raw-token outbox payload, a second long-lived token store, or a change to invitation token format.

---

## 17. Implementation Requirements After Approval

Implementation must:

1. implement only the selected and approved handoff mechanism;
2. define its storage, encryption/protection, lifetime, access authority, ownership, and deletion semantics;
3. bind every handoff to the invitation, hospital, and outbox identity;
4. preserve the SHA-256 token hash as the persistent verification representation;
5. preserve the seven-day expiry;
6. keep the raw token outside the outbox and ordinary persistence;
7. construct the invitation URL only in the approved backend delivery boundary;
8. preserve R7A attempt, retry, idempotency, and recovery values;
9. prevent client, frontend, JWT, event, log, and telemetry access;
10. maintain the approved encrypted handoff storage and RLS controls through the required migration;
11. add focused tests for lifecycle, authorization, confidentiality, retries, crashes, expiry, and tenant isolation;
12. stop and report any implementation conflict rather than inventing a replacement.

Implementation is authorized only within this contract.

---

## 18. Tests Required After Approval

Focused tests must cover at minimum:

### Handoff creation and binding

- handoff material is created only by the authorized invitation service;
- handoff is bound to the invitation, hospital, and outbox identity;
- client cannot create, replace, read, or delete handoff material;
- cross-hospital retrieval is rejected;
- raw token is never persisted in prohibited locations.

### Retrieval and link construction

- only the trusted worker can retrieve the handoff;
- worker constructs the approved invitation URL in memory;
- the delivery abstraction receives the URL without provider coupling;
- raw token and URL are absent from logs, errors, events, telemetry, and API responses.

### Retry and crash recovery

- retry reuses the same invitation and token;
- retry does not create a second invitation;
- worker crash before retrieval is recoverable;
- worker crash after retrieval follows the approved lease/replay semantics;
- missing or expired handoff follows the approved failure behavior;
- stale `PROCESSING` recovery preserves attempt count;
- no fourth delivery attempt occurs.

### Expiry and acceptance

- seven-day invitation expiry remains authoritative;
- expired invitations cannot be accepted even if handoff material remains;
- token verification continues to use SHA-256 comparison;
- identity binding remains enforced.

Focused implementation tests are required and are maintained with the R7 implementation.

---

## 19. Approval Gate

```text
DECISION ID: R7A-11
STATUS: APPROVED
IMPLEMENTATION: AUTHORIZED
R7 IMPLEMENTATION: AUTHORIZED
```

### Architectural Approval

```text
[x] APPROVED
[ ] REJECTED
[ ] APPROVED WITH AMENDMENTS
```

**Approved By:** ______________________________

**Date:** _____________________________________

**Amendments:**

```text
________________________________________________

________________________________________________

________________________________________________
```

---

## 20. Decision Record

```text
Decision ID: R7A-11
Decision Type: Security / Transactional Delivery Architecture
Status: APPROVED
Implementation: AUTHORIZED

Amends:
PHASE_16G_R7A_TRANSACTIONAL_OUTBOX_CONTRACT_AMENDMENT.md

Supersedes:
Only the conflicting token-handoff portions of R7A-10.

Depends On:
R7
R7A-1
R7A-2
R7A-3
R7A-4
R7A-5
R7A-6
R7A-7
R7A-8
R7A-9
R7A-10

Selected Mechanism:
BACKEND-ONLY EPHEMERAL HANDOFF SERVICE

Storage:
PROTECTED EPHEMERAL STORAGE, ENCRYPTED AT REST

Retrieval:
REPLAYABLE TO AUTHORIZED DELIVERY WORKER UNTIL SUCCESSFUL DELIVERY OR INVITATION EXPIRY

Access:
TRUSTED BACKEND DELIVERY WORKER ONLY

Implementation Gate:
AUTHORIZED
```

---

## 21. Final Statement

R7A-11 resolves the token-handoff blocker without weakening the approved token-hashing, outbox, retry, identity, tenancy, or authentication architecture.

The approved mechanism is a backend-only ephemeral handoff service using protected storage encrypted at rest. The handoff is replayable only to the trusted delivery worker until successful delivery or the seven-day invitation expiry. R7 implementation may proceed within these constraints.
