"""krules: business-rule helpers using the kanren logic programming library.

This package is a minimal starter so you can drop your domain rules into `krules/`.
"""
from .relations import (
    parent,
    male,
    female,
    children_of,
    parents_of,
    is_male,
    is_female,
    siblings_of,
)
from .helpers import (
    descendants_of,
    ancestors_of,
    closure_from_edges,
    assign_role,
    assign_role_inherit,
    has_role,
    role_members,
)

__all__ = [
    "parent",
    "male",
    "female",
    "children_of",
    "parents_of",
    "is_male",
    "is_female",
    "siblings_of",
    "descendants_of",
    "ancestors_of",
    "closure_from_edges",
    "assign_role",
    "assign_role_inherit",
    "has_role",
    "role_members",
]
