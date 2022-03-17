#########################
Changelog
#########################

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
