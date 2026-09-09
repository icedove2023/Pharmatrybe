# R9H - Production Isolation Runtime

## Status

The repository provides a policy abstraction and a container-runtime adapter, but production container execution is deployment-dependent and is not enabled by the current Windows development runtime.

## Enforced In Application Code

- Governance and artifact admission occur before external code import.
- External code uses the JSON subprocess protocol through contract proxies.
- Requests, stdout, stderr, and serialized results are bounded.
- The child receives an explicit environment allowlist and temporary working directory.
- Execution-time governance and artifact hashes are rechecked.
- Execution metadata is persisted without patient payloads, plugin output, credentials, or secrets.
- Network-capable external plugins are denied unless a runtime proves network policy enforcement.

## Policy Truthfulness

`IsolationPolicy` is platform-owned. `IsolationRuntime.can_enforce()` returns an auditable enforcement decision. The development subprocess reports that CPU, memory, OS filesystem, and execution-identity controls are not enforced. It must not be used as production isolation for a policy requiring those controls.

`ContainerIsolationRuntime` builds a Docker-compatible command with:

- CPU and memory limits;
- `--network=none`;
- read-only root filesystem;
- dropped Linux capabilities;
- `no-new-privileges`;
- a dedicated non-root user;
- an explicit artifact bind mount;
- automatic container removal.

The adapter only reports enforcement when the configured container executable is available and the policy is valid. It does not silently fall back to the development subprocess.

## Deployment Prerequisites

Production external execution requires a Linux/container deployment that provides:

- a trusted container runtime;
- a plugin runtime image containing the worker and approved dependencies;
- a non-root `pharmatrybe-plugin` user;
- cgroup CPU and memory enforcement;
- network namespace/firewall policy;
- read-only root filesystem and explicit writable temporary storage;
- process and container cleanup permissions;
- runtime monitoring and image/artifact supply-chain controls.

No live container runtime or deployed Supabase environment was verified in this workspace.

## Explicit Limitations

The current Windows development subprocess is not an OS sandbox. It does not provide hard CPU or memory limits, OS-level network isolation, complete host filesystem confinement, or a restricted operating-system identity. R9H therefore remains deployment-blocked for production external execution until the container runtime adapter is wired to the deployed execution service and verified there.
