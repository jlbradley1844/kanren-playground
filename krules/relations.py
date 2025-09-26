"""Simple kanren-based relations and helpers for business rules prototyping.

This module intentionally keeps things small: it defines a few base facts and
helper predicates you can extend. It uses the `kanren` library that should
already be installed in the environment.
"""
from __future__ import annotations

import collections

# Compatibility shim: some downstream packages import names (Iterator,
# Hashable, Callable, etc.) from `collections` (the old location). On
# modern Python these live in `collections.abc`. Provide backwards-compatible
# attributes on the `collections` module so older packages keep working.
try:
    from collections import abc as _collections_abc
    _map_names = [
        "Iterator",
        "Hashable",
        "Callable",
        "Sequence",
        "Mapping",
        "MutableMapping",
    ]
    for _name in _map_names:
        if not hasattr(collections, _name) and hasattr(_collections_abc, _name):
            setattr(collections, _name, getattr(_collections_abc, _name))
except Exception:
    # best-effort; if this fails we'll surface import errors below
    pass

from kanren import Relation, facts, run, var, conde


# Define relations
parent = Relation()
male = Relation()
female = Relation()


# Example: register some simple facts (you can replace these with your domain data)
facts(parent, ("bob", "alice"), ("bob", "jack"), ("alice", "sue"))
facts(male, ("bob",), ("jack",))
facts(female, ("alice",), ("sue",))


def children_of(person):
    """Return a generator of children for `person`.

    Example:
        list(children_of('bob')) -> ['alice', 'jack']
    """
    x = var()
    results = run(0, x, parent(person, x))
    return results


def parents_of(child):
    x = var()
    results = run(0, x, parent(x, child))
    return results


def is_male(name):
    x = var()
    return bool(run(1, x, male(name,)) )


def is_female(name):
    x = var()
    return bool(run(1, x, female(name,)) )


def siblings_of(name):
    """Return names of siblings: share a parent but are not the same person."""
    p = var()
    s = var()
    results = run(0, s, parent(p, name), parent(p, s), conde([s != name]))
    # run returns tuples for compound answers; ensure simple list
    return [r for r in results]
