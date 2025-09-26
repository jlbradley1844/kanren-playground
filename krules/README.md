krules — business-rule helpers (kanren)
======================================

This folder contains a small set of helpers and starter facts for writing
business rules using the `kanren` logic programming library. The helpers are
intentionally minimal and meant to be extended with your domain logic.

Quick notes
-----------
- Requires `kanren` to be installed in your environment (we used a project venv).
- The helpers are small and primarily intended for prototyping. For large data
  sets consider using a graph database or persistent store for roles.

Files
-----
- `relations.py` — starter facts and simple kanren-based helpers
- `helpers.py` — transitive closure, ancestry/descendant helpers and role utilities

Guidance
--------
- Replace the in-memory `_roles` dict in `helpers.py` with a persistent store
  (database, Redis, etc.) when you need durability or multi-process access.
- For large graphs use an optimized transitive closure algorithm or a graph
  database instead of the simple closure implementation provided here.
- Keep rules small and pure where possible so they are easy to test.

If you'd like, I can add more domain-oriented helper templates (temporal rules,
permission checks, role hierarchies) or wire a persistent backend for roles.
