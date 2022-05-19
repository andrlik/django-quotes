#########################
Changelog
#########################

0.2.3
-----

- Bug: Fixed issue with pagination not showing accurate count for all objects.
- Bug: Fix page title when viewing a list of sources for a SourceGroup.

0.2.2
-----

Update for latest mypy and fixes for documentation builds.

0.2.1
-----

- Enable type annotations with py.typed.

0.2.0
-----

- ``SourceGroups`` no longer require a unique name (since users won't know what else is there anyway).
- New slug generation to ensure that slugs remain unique.
- It is no longer possible to specify a slug within a given create form for either ``SourceGroup`` or ``Source`` objects.

0.1.3
-----

- Adds a configuration option for controlling how many quotes should be retrieved for random quote selection from a
  ``SourceGroup``. To make use of this option, add the variable ``MAX_QUOTES_FOR_RANDOM_GROUP_SET`` to your project's
  ``settings.py``.
- Bugfix: ``SourceGroup`` random group selection now prioritizes quotes that have been served less often via the
  ``QuoteStats.times_used`` value. This was already the case when selecting from a single ``Source``, but the behavior
  is now consistent for ``SourceGroup`` as well.

0.1.2
-----

- Adds a configuration option for controlling how many quotes should be retrieved for random quote selection.
  To make use of this option, add the variable ``MAX_QUOTES_FOR_RANDOM_SET`` in your project's ``settings.py`` file.
