# MVP Product Specification

## Goal

Enable a farmer to sign in, create a farm and flock, register sheep or goats, and see trustworthy livestock totals and animals requiring attention.

## Initial users

- Farm owner: manages the farm, membership, and all records.
- Farm worker: records and views animals; expanded permissions follow later.

## First vertical slice

1. Sign in securely.
2. Create or select a farm.
3. Create a flock.
4. Register an animal with an ear tag, species, sex, birth date, and status.
5. Search or filter the animal register.
6. View total active animals, species totals, and attention count.

## Domain rules

- Ear tags are unique within a farm, not globally.
- Every flock and animal belongs to exactly one farm.
- Farm data is accessible only to active farm members.
- Lifecycle status is separate from health attention state.
- Historical health and husbandry information will be appended as events, not overwritten on the animal.

## Deferred

Treatments, recurring husbandry tasks, notifications, feeding plans, chatbot answers, offline mode, native applications, and location trackers are outside the first vertical slice.
