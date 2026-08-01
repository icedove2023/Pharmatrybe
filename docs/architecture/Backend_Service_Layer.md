# PharmaTrybe Backend Service Layer

## Purpose

This document defines the architectural foundation for the PharmaTrybe backend service layer.
The goal is to establish reusable service clients that the FastAPI backend can use to communicate with future platform components while preserving modular boundaries.

## Service Layer

The backend service layer is the communication boundary between the FastAPI application and future platform services.
It exists to keep orchestration logic separate from transport details and to ensure that every integration follows a consistent pattern.

## Responsibilities

The service layer is responsible for:

- providing a common base class for future service clients
- defining service metadata and availability state
- standardizing the client interface for future integrations
- keeping HTTP transport and AI logic out of route handlers
- enabling future health monitoring for platform services

## Client Pattern

Every platform service has a dedicated client class.

The current clients are:

- SOARClient
- ARMDClient
- WHOClient
- DecisionEngineClient
- ExplainabilityClient

Each client inherits from BaseService and exposes placeholder methods only.

## Inheritance

All clients inherit from BaseService.

BaseService provides:

- timeout configuration placeholder
- retry configuration placeholder
- a standardized execution interface placeholder
- service metadata
- availability state

## Communication Flow

The FastAPI backend communicates with platform services through service clients.
This preserves the architecture rule that the backend acts as the orchestrator and that services remain independent.

```text
FastAPI Backend
      │
      ▼
Service Clients
      │
      ▼
Future Platform Services
```

## Future Integration

The initial implementation does not make HTTP requests or perform inference.
It only establishes the architectural entry points for:

- SOAR/GSK integration
- ARMD integration
- WHO Knowledge integration
- Clinical Decision Engine integration
- Explainability integration

## Health Monitoring

A service health registry exists to describe the current platform services.
It provides a simple model for future health checks and observability.

## Why the FastAPI Backend Uses Service Clients

The FastAPI backend communicates only through service clients so that:

- orchestration remains centralized
- platform services remain independently deployable
- business logic stays outside the API layer
- future transport changes do not require route redesign
- the architecture remains modular and auditable
