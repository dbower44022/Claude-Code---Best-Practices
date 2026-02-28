---
name: design-principles
description: CRMExtender global design principles and technical constraints that govern all implementation. Use when writing any code, making architectural decisions, choosing data patterns, or reviewing implementation approaches. Covers display speed, idempotency, schema compatibility, contact creation, correction tracking, sort performance, and field editability. These are rules, not suggestions.
---

# CRMExtender Design Principles

These principles are extracted from the Product TDD Section 11 and apply to
all implementation work. They are non-negotiable constraints.

## 11.1 Display Speed is Paramount

The system's value depends on fast, responsive data access. Denormalize wherever
it reduces JOIN depth for frequently displayed data. Accept write complexity to
achieve read speed.

## 11.2 Idempotent Writes

All sync operations use UPSERT or INSERT-ON-CONFLICT patterns. Safe to re-run
at any time. No operation should produce different results on second execution.

## 11.3 Schema Compatibility

DDL must work in both SQLite and PostgreSQL with minimal divergence.
PostgreSQL-only features are used only where a SQLite fallback exists (or is
explicitly accepted as a migration-time change).

## 11.4 Contacts Are Created Immediately

Unknown identifiers create minimal contact records (`status='incomplete'`) on
first encounter. This prevents communications from existing without a contact
linkage and ensures the identity resolution pipeline always has a record to
work with.

## 11.5 Every Correction Is a Training Signal

User corrections to assignments, triage, and conversation management are
captured in dedicated correction tables to feed the AI learning system.
No user correction is discarded.

## 11.6 Sort Performance Awareness

Fields in the entity registry must respect the sort performance categories
(direct column, JOIN column, correlated subquery). Subquery-backed fields are
marked `sortable=False` unless the entity TDD defines a caching strategy.
The Entity Base PRD marks fields requiring caching with † in the Sortable column.

## 11.7 Editability Is Explicit

Every field in the Entity Base PRD declares its edit behavior (Direct, Override,
Via sub-entity, Computed, System). Claude Code must not make a field editable
that the PRD marks as Computed or System, and must route Via sub-entity fields
through the appropriate editor rather than inline editing.
