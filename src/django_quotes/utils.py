#
# utils.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from loguru import logger
from slugify import slugify


def generate_unique_slug_for_model(
    model_class: type[Model],
    text: str,
    slug_field: str | None = "slug",
    max_length_override: int | None = None,
) -> str:
    """
    Generate a unique slug for the given model.

    Args:
        model_class (Model): A class based upon ``django.db.models.Model``
        text (str): Text to convert to a slug.
        slug_field (str | None): The name of the slug field of the model.
        max_length_override (int | None): Maximum number of characters to use
            if not the same as what's defined in the slug field.
    Returns:
         (str): The generated slug.
    """
    unique_found: bool = False
    has_next: bool = False
    next_val: int = 0
    if not max_length_override:
        logger.debug("Setting max_length of slug from field definition.")
        max_length: int = model_class._meta.get_field(slug_field).max_length  # type: ignore
    else:
        logger.debug("User override value for max length of slug.")
        max_length = max_length_override
    slug = slugify(text, max_length=max_length)
    logger.debug(f"Base slug is set to '{slug}'.")
    while not unique_found:
        logger.debug(f"Testing uniqueness of slug '{slug}'...")
        try:
            model_class.objects.get(**{str(slug_field): slug})
        except ObjectDoesNotExist:
            logger.debug("Slug is unique!")
            unique_found = True
        if not unique_found:
            logger.debug("Slug is not unique yet.")
            next_val += 1
            if has_next:
                slug = slug[len(slug) - (len(str(next_val - 1)) - 1) :]
            if len(slug) >= max_length:
                slug = slug[: max_length - (len(str(next_val)) + 1)]
            slug = slug + f"-{next_val}"
            has_next = True
    return slug
