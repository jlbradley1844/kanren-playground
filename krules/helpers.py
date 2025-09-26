"""Helpers for common rule patterns: transitive closure, ancestry, role-based rules.

These helpers blend small kanren queries with in-memory structures to keep things
easy to extend. For complex uses you may want to move to a database-backed
store or a more advanced rule engine.
"""
from __future__ import annotations

from typing import Iterable, Set, Tuple, Dict, List

from kanren import run, var
from .relations import parent


def closure_from_edges(edges: Iterable[Tuple[str, str]]) -> Dict[str, Set[str]]:
    """Compute the transitive closure for a directed graph represented as edges.

    Returns a mapping node -> set(reachable nodes).
    """
    # Build adjacency list
    adj: Dict[str, Set[str]] = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set())

    # Floyd-Warshall style expansion (simple, small graphs only)
    nodes = list(adj.keys())
    reach = {n: set(adj.get(n, set())) for n in nodes}
    for k in nodes:
        for i in nodes:
            if k in reach[i]:
                reach[i].update(reach[k])
    return reach


def descendants_of(person: str) -> List[str]:
    """Return all descendants (transitive children) of a person using kanren queries.

    For small trees this is fine; for large data prefer a graph DB or a cached closure.
    """
    # naive breadth-first using children_of from relations
    from .relations import children_of

    seen = set()
    queue = list(children_of(person))
    while queue:
        c = queue.pop(0)
        if c in seen:
            continue
        seen.add(c)
        queue.extend(children_of(c))
    return list(seen)


def ancestors_of(person: str) -> List[str]:
    from .relations import parents_of

    seen = set()
    queue = list(parents_of(person))
    while queue:
        p = queue.pop(0)
        if p in seen:
            continue
        seen.add(p)
        queue.extend(parents_of(p))
    return list(seen)


# Simple in-memory role assignments. You can replace this with a datastore.
_roles: Dict[str, Set[str]] = {}


def assign_role(role: str, subject: str) -> None:
    _roles.setdefault(role, set()).add(subject)


def assign_role_inherit(role: str, subject: str) -> None:
    """Assign role and inherit it to role-membership of descendants.

    For example, assigning 'manager' to 'alice' will also give 'manager' to
    descendants of 'alice' depending on business logic. This is just an example
    policy; modify as needed.
    """
    assign_role(role, subject)
    for d in descendants_of(subject):
        assign_role(role, d)


def has_role(role: str, subject: str) -> bool:
    return subject in _roles.get(role, set())


def role_members(role: str) -> List[str]:
    return list(_roles.get(role, set()))
