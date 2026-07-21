# ADR 0001: Django and Nuxt Modular Monolith

- Status: Accepted
- Date: 2026-07-21

## Context

The original system split a small livestock domain across an HTTP gateway, gRPC service, RabbitMQ consumer, Keycloak, and generated protobuf contracts. Product discovery now requires rapid iteration across animal records, health, reminders, feeding, dashboards, and a future assistant.

## Decision

Use Django 5.2 and Django REST Framework as one modular backend, PostgreSQL as the system of record, and Nuxt 4 with Vue 3 and TypeScript for the web client. Add Celery and Redis only when durable scheduled work is implemented. Expose versioned REST/JSON with an OpenAPI contract.

Organize backend code by business capability. Keep business workflows outside HTTP views, enforce farm scoping at every query boundary, and split deployment units only after measured operational need.

## Consequences

Development and deployment become simpler, transactions can span related domain modules, and Django Admin provides an immediate operational interface. The application must maintain clear internal module boundaries to avoid becoming an unstructured monolith.
