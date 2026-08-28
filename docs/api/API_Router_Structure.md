# PharmaTrybe API Router Structure

## Purpose

This document defines the versioned router structure for the PharmaTrybe backend API.
The goal is to keep the FastAPI application modular, predictable, and ready for future service expansion without introducing business logic.

## API Versioning

The backend exposes a versioned API namespace under `/api/v1`.
This preserves a stable contract for future backend evolution while keeping the implementation organized and explicit.

## Router Organization

The API is split into independent router modules that each represent a distinct functional area:

- authentication
- clinical cases
- patients
- recommendations
- WHO knowledge
- SOAR/GSK integration
- ARMD integration
- decision orchestration
- explainability
- admin operations
- health and version endpoints

Each module is mounted under the main versioned router and exposes a lightweight placeholder endpoint for future extension.

## Naming Conventions

The router package follows these conventions:

- use descriptive module names that align with the service area
- keep route handlers small and placeholder-based
- use explicit FastAPI router prefixes for clarity
- preserve a consistent `/api/v1` namespace

## Responsibilities

Each router is responsible only for:

- exposing a stable endpoint entry point
- returning a simple service-status payload
- preserving the modular API boundary

No CRUD operations, database access, AI inference, or clinical logic are implemented in these routes.

## Future Expansion

The structure is intentionally lightweight so future Phase 3 work can add real handlers, request models, or orchestration logic without reworking the overall API layout.
This keeps the router surface predictable and supports independent evolution of each domain area.
