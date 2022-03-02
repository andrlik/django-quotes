import rules


@rules.predicate
def is_owner(user, obj):
    return obj.owner == user


@rules.predicate
def is_public(user, obj):
    return obj.public


@rules.predicate
def allows_submissions(user, obj):
    return obj.allow_submissions


is_owner_or_public = is_public | is_owner


@rules.predicate
def is_group_owner(user, obj):
    return user == obj.group.owner


@rules.predicate
def is_character_owner(user, obj):
    return user == obj.character.owner


is_group_owner_and_authenticated = rules.is_authenticated & is_group_owner
