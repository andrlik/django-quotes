#
# rules.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

"""Access control rules."""

import rules


@rules.predicate
def is_owner(user, obj):
    """Check if the user is the owner of the object."""
    return obj.owner == user


@rules.predicate
def is_public(user, obj):
    """Check if the object is public."""
    return obj.public


@rules.predicate
def allows_submissions(user, obj):
    """Check if the object allows submissions."""
    return obj.allow_submissions


is_owner_or_public = is_public | is_owner  # type: ignore


@rules.predicate
def is_group_owner(user, obj):
    """Check if the object's group is owned by the user."""
    return user == obj.group.owner


@rules.predicate
def is_source_owner(user, obj):
    """Check that the quote source is owned by the user."""
    return user == obj.source.owner


is_group_owner_and_authenticated = rules.is_authenticated & is_group_owner  # type: ignore
