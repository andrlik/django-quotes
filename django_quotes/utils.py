from typing import Optional, Type

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from loguru import logger
from slugify import slugify


def generate_unique_slug_for_model(
    model_class: Type[Model],
    text: str,
    slug_field: Optional[str] = "slug",
    max_length_override: Optional[int] = None,
) -> str:
    """
    Generate a unique slug for the given model.

    :param model_class: A class based upon ``django.db.models.Model``
    :param text: Text to convert to a slug.
    :param slug_field: The name of the slug field of the model.
    :param max_length_override: Maximum number of characters to use if not the same as what's defined in the slug field.
    :return: The generated slug.
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
                slug = slug[len(slug) - (len(str(next_val - 1)) - 1) :]  # noqa: E203
            if len(slug) >= max_length:
                slug = slug[: max_length - (len(str(next_val)) + 1)]
            slug = slug + f"-{next_val}"
            has_next = True
    return slug
