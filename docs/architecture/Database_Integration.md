# PharmaTrybe Database Integration

## Purpose

This document defines the persistence foundation for the PharmaTrybe backend.
The goal is to establish the SQLAlchemy-based database architecture that future repositories and services can build on without introducing business logic.

## Architecture

The backend uses a modular database package under the FastAPI application.
It provides:

- SQLAlchemy engine configuration
- session management
- an abstract ORM base model with common lifecycle fields
- a repository foundation for future persistence layers
- a placeholder database health checker

## Repository Pattern

The repository layer is intentionally abstract.
It provides a reusable base class that future domain repositories can extend.
This keeps persistence concerns separate from API and service layers.

## Session Lifecycle

Sessions are managed through a dedicated session factory and a dependency-friendly generator function.
This pattern allows the FastAPI application to provide scoped database sessions while keeping the lifecycle explicit.

## Dependency Injection

The database session helper is designed to be used with FastAPI dependency injection.
The session is created when requested and closed after use, preserving a clear lifecycle boundary.

## Connection Pooling

The SQLAlchemy engine uses a basic connection pool configuration so the backend is ready for future connection reuse and pooling behavior.
This is a structural placeholder and does not yet perform runtime database operations.

## Security Considerations

The database integration layer follows these safety practices:

- use environment variables for connection strings
- keep credentials out of source control
- avoid embedding secrets in code or documentation
- remain decoupled from business rules and clinical logic
