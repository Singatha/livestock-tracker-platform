# Database Design

## Overview

PostgreSQL is the system of record. Django migrations own the schema. `accounts.User` extends Django's standard user model; other persistent domain models inherit `TimeStampedModel`, which provides a UUID primary key plus `created_at` and `updated_at` timestamps.

Most business tables carry a direct `farm_id`. This intentional denormalisation makes tenant filters and indexes simple, but code must verify that related objects belong to the same farm. `FeedingPlanItem` is the notable exception: its farm is derived through its plan.

## Tenancy and Livestock Core

```mermaid
erDiagram
    USER ||--o{ FARM : owns
    USER ||--o{ FARM_MEMBERSHIP : joins
    FARM ||--o{ FARM_MEMBERSHIP : has
    FARM ||--o{ FARM_INVITATION : issues
    USER ||--o{ FARM_INVITATION : sends_or_accepts
    FARM ||--o{ FARM_MEMBERSHIP_AUDIT : records
    FARM ||--o{ FLOCK : contains
    FARM ||--o{ ANIMAL : owns
    FLOCK o|--o{ ANIMAL : groups
    ANIMAL ||--o{ ANIMAL_LIFECYCLE_EVENT : has
    FLOCK o|--o{ ANIMAL_LIFECYCLE_EVENT : from_or_to
    USER ||--o{ ANIMAL_LIFECYCLE_EVENT : records

    FARM {
      uuid id PK
      bigint owner_id FK
      varchar name
    }
    FARM_MEMBERSHIP {
      uuid id PK
      uuid farm_id FK
      bigint user_id FK
      enum role
      boolean is_active
    }
    FLOCK {
      uuid id PK
      uuid farm_id FK
      varchar name
    }
    ANIMAL {
      uuid id PK
      uuid farm_id FK
      uuid flock_id FK
      varchar ear_tag
      enum species
      enum sex
      enum status
      boolean needs_attention
    }
    ANIMAL_LIFECYCLE_EVENT {
      uuid id PK
      uuid animal_id FK
      uuid farm_id FK
      enum event_type
      date effective_date
      bigint recorded_by_id FK
    }
```

`FarmMembership` is the authorisation join between a user and farm. Roles are owner, manager, worker, and viewer. `Farm.owner` identifies the founding/primary owner while memberships drive access control. Animal lifecycle state is stored on `Animal` for current queries and appended to `AnimalLifecycleEvent` for history.

## Animal History and Reproduction

```mermaid
erDiagram
    FARM ||--o{ HEALTH_OBSERVATION : owns
    ANIMAL ||--o{ HEALTH_OBSERVATION : has
    HEALTH_OBSERVATION o|--o{ TREATMENT : motivates
    ANIMAL ||--o{ TREATMENT : receives
    ANIMAL ||--o{ WEIGHT_MEASUREMENT : weighs
    ANIMAL ||--o{ ATTACHMENT : has
    FARM ||--o{ ATTACHMENT : stores
    ANIMAL ||--o{ BREEDING_RECORD : dam
    ANIMAL o|--o{ BREEDING_RECORD : sire
    BREEDING_RECORD ||--o| BIRTH_RECORD : concludes
    ANIMAL ||--o{ BIRTH_RECORD : dam

    HEALTH_OBSERVATION {
      uuid id PK
      uuid farm_id FK
      uuid animal_id FK
      enum category
      enum severity
      boolean is_resolved
    }
    TREATMENT {
      uuid id PK
      uuid farm_id FK
      uuid animal_id FK
      uuid observation_id FK
      datetime administered_at
      date withdrawal_end_date
    }
    WEIGHT_MEASUREMENT {
      uuid id PK
      uuid farm_id FK
      uuid animal_id FK
      date measured_on
      decimal weight_kg
    }
    BREEDING_RECORD {
      uuid id PK
      uuid farm_id FK
      uuid dam_id FK
      uuid sire_id FK
      date breeding_date
      date expected_birth_date
      enum status
    }
    BIRTH_RECORD {
      uuid id PK
      uuid breeding_id UK
      uuid dam_id FK
      date birth_date
      smallint total_born
      smallint born_alive
      smallint stillborn
    }
```

`Treatment` is a lightweight historical health entry. Structured medicine inventory and multi-dose workflows use the separate treatment-course model below. A breeding can have at most one birth. The service copies the breeding dam onto the birth for efficient history and enforces that birth totals reconcile.

## Operations, Inventory, and Supporting Records

```mermaid
erDiagram
    FARM ||--o{ HUSBANDRY_TASK : schedules
    ANIMAL o|--o{ HUSBANDRY_TASK : targets
    FLOCK o|--o{ HUSBANDRY_TASK : targets
    HUSBANDRY_TASK ||--o{ NOTIFICATION : produces
    USER ||--o{ NOTIFICATION : receives
    FARM ||--o{ MEDICINE_PRODUCT : stocks
    MEDICINE_PRODUCT ||--o{ MEDICINE_BATCH : batches
    MEDICINE_PRODUCT ||--o{ TREATMENT_COURSE : prescribed
    ANIMAL ||--o{ TREATMENT_COURSE : receives
    TREATMENT_COURSE ||--o{ DOSE_ADMINISTRATION : contains
    MEDICINE_BATCH ||--o{ DOSE_ADMINISTRATION : supplies
    FARM ||--o{ FEED : stocks
    FARM ||--o{ FEEDING_PLAN : owns
    FLOCK ||--o{ FEEDING_PLAN : follows
    FEEDING_PLAN ||--o{ FEEDING_PLAN_ITEM : contains
    FEED ||--o{ FEEDING_PLAN_ITEM : uses
    FARM ||--o{ IMPORT_JOB : runs
    FARM ||--o{ AUDIT_EVENT : records

    HUSBANDRY_TASK {
      uuid id PK
      uuid farm_id FK
      date due_date
      enum status
      int recurrence_days
    }
    MEDICINE_PRODUCT {
      uuid id PK
      uuid farm_id FK
      varchar name
      decimal reorder_level
      smallint meat_withdrawal_days
      smallint milk_withdrawal_days
    }
    MEDICINE_BATCH {
      uuid id PK
      uuid product_id FK
      varchar batch_number
      date expiry_date
      decimal quantity_on_hand
    }
    TREATMENT_COURSE {
      uuid id PK
      uuid animal_id FK
      uuid product_id FK
      enum status
      smallint planned_doses
    }
    DOSE_ADMINISTRATION {
      uuid id PK
      uuid course_id FK
      uuid batch_id FK
      datetime administered_at
      decimal quantity_used
    }
    FEEDING_PLAN_ITEM {
      uuid id PK
      uuid plan_id FK
      uuid feed_id FK
      decimal quantity_per_animal
    }
    IMPORT_JOB {
      uuid id PK
      uuid farm_id FK
      enum kind
      enum mode
      enum status
      json rows
      json errors
    }
    AUDIT_EVENT {
      uuid id PK
      uuid farm_id FK
      bigint actor_id FK
      varchar resource_type
      varchar resource_id
      uuid animal_id
      json changes
    }
```

`AuditEvent.resource_id` and `animal_id` are intentionally not foreign keys: audit history remains readable after a tracked resource or user is deleted. The actor is nullable and becomes `NULL` when the user is removed. Attachment file bytes are likewise outside PostgreSQL; the attachment row stores ownership, metadata, and the storage path.

## Key Constraints

| Constraint | Purpose |
| --- | --- |
| Unique `(farm, user)` membership | One role-bearing membership per user and farm |
| Unique invitation token | Unguessable invitation lookup |
| Unique `(farm, name)` for flocks, feeds, and medicine products | Tenant-local naming |
| Unique `(farm, ear_tag)` animal | Ear tags may repeat only across farms |
| Unique `(animal, measured_on)` weight | At most one official weight per animal per day |
| One-to-one birth to breeding | A breeding has at most one recorded outcome |
| Unique `(product, batch_number)` medicine batch | Identifies physical stock lots |
| Unique `(plan, feed)` feeding item | A feed appears once per plan |
| Unique `(recipient, task, kind)` notification | Idempotent reminder generation |

Cross-table rules that SQL constraints do not currently express are enforced in serializers and transactional services. Examples include same-farm relationships, species/sex eligibility for breeding, matching dose products and batches, sufficient stock, valid birth totals, valid feeding-plan dates, and retaining at least one active farm owner.

## Index Strategy

Indexes lead with `farm_id` on common tenant queries and then include status, species, date, recipient, category, or resource type as appropriate. This supports dashboards, due-task scans, timelines, inventory alerts, reports, and audit filtering without global table scans. Foreign keys and unique constraints also receive PostgreSQL indexes through Django.

When query behavior changes, inspect generated SQL and production-like data before adding an index. Avoid indexing low-selectivity fields alone, and remove indexes shown to be redundant.

## Delete and Retention Behavior

- Deleting a farm cascades through most operational data, but protected audit records and the protected owner relationship can prevent unsafe deletion.
- Removing a flock sets an animal's current flock to `NULL`; historical lifecycle flock references also use `SET_NULL`.
- Health observations, weights, attachments, and tasks cascade with their animal; breeding participants, birth records, and treatment courses protect referenced animals.
- Products, batches, courses, and dose administrations use `PROTECT` where deletion would invalidate medicine history.
- Recorded-by and administered-by relationships generally use `PROTECT`; audit actors use `SET_NULL`.
- `AuditEvent` overrides update and delete operations and is append-only through the application.

Retention periods and archival procedures are not yet defined. Production readiness must establish backup, restore, retention, privacy, and attachment-storage policies before live farm data is hosted.

## Schema Change Process

1. Change the Django model and associated validation/service rules.
2. Create a named migration with `python manage.py makemigrations`.
3. Review SQL and deletion behavior, especially for populated tables.
4. Add tests for constraints, farm isolation, and data migration behavior.
5. Run `python manage.py migrate` and the full backend test suite.
6. Update this document when entities, relationships, or material invariants change.
