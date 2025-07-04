# Changelog

## 0.6.0

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.5.2...v0.6.0)

- Support for Python 3.13. Drops support for Python 3.11.
- Support for Django 5.2
- Updates django-markov
- Adds `--force` option to `makemarkov` management command to regenerate all MarkovTextModels. You should run this after updating to ensure your models are correctly stored.

## 0.5.2

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.5.1...v0.5.2)

- Officially supports Django 5.1

## 0.5.1

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.5.0...v0.5.1)

- Updates to `django-markov` to 0.3.0
- Converts add_new_quote_to_model to use the underlying functions from django-markov.
- Adds the ability to add an iterable of Quote instances to the model at once. The call accepts either an iterable or QuerySet of Quote instances, or a single instance to maintain backwards compatibility.

## 0.5.0

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.4.2...v0.5.0)

- Adds a method `django_quotes.tasks.update_models_on_quote_save` that can be used for distributed task queues such as django-q2 or celery for updating markov models as a background task.
- Updates behavior of SourceGroup when generating its text model based its sources. It now makes use of `django-markov`'s `combine_models`, which is over 750% faster!
- Adds convenience method `add_quote_to_model` to `Source` for quick adding of quotes. We still don't trigger this automatically due to performance concerns. You should either use this with a distributed task queue or run the management command as a cronjob.


## 0.4.2

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.4.1...v0.4.2)

- Rendered fields have been removed: `description_rendered` and `quote_rendered`. For backwards compatibility, their values can be accessed via properties of the same names.

## 0.4.1

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.4.0...v0.4.1)

- Some improvements to migrations to handle some upgrade use cases.
- Some type annotation improvements.

## 0.4.0

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.3.2...v0.4.0)

- Drops support for Python 3.9 and 3.10.
- Moves markov model management to [django-markov](https://github.com/django-markov).
  - This replaces the current `SourceMarkovModel` and `GroupMakovModel` with `MarkovTextModel`.
  - This replaces the `markov_sentence_generated` with `django-markov`'s `sentence_generated` signal.
  - Migrations will transfer existing models to the new database tables and then remove the old one.
    - While no data loss is anticipated, if is **highly** recommended that you take a backup of your database prior to upgrading.
    - If you'd still like to implement the migrations cautiously, you can run `python manage.py migrate django_quotes 0011` first to confirm that the data migrated safely. Then you can run `python manage.py migrate django_quotes 0012` to complete the upgrade and remove the old tables.
- As `django-markov` makes heavy use of the newest async features, Django>=5.0 is now required.
- Improved python module reference documentation.
- Add versioning to documentation.

## 0.3.2

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.3.1...v0.3.2)

- Security update: removes `py` from dependencies as no longer needed and has a vulnerability.

## 0.3.1

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.3.0...v0.3.1)

- Adds support for python 3.11 by upgrading `spacy` dependency to 3.4.2 and adding `py`.

**Upgrade Note:** You will want to update your spacy language model after updating. You can do this by:

```bash
python -m spacy download en_core_web_sm
```

## 0.3.0

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.2.4...v0.3.0)

- Add `pub_date` field to `Quote` model. This prevents a quote with a future date from appearing in random requests.

## 0.2.4

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.2.3...v0.2.4)

- Update documentation links on PyPI.

## 0.2.3

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.2.2...v0.2.3)

- Bug: Fixed issue with pagination not showing accurate count for all objects.
- Bug: Fix page title when viewing a list of sources for a SourceGroup.

## 0.2.2

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.2.1...v0.2.2)

Update for latest mypy and fixes for documentation builds.

## 0.2.1

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.2.0...v0.2.1)

- Enable type annotations with py.typed.

## 0.2.0

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.1.3...v0.2.0)

- `SourceGroups` no longer require a unique name (since users won't know what else is there anyway).
- New slug generation to ensure that slugs remain unique.
- It is no longer possible to specify a slug within a given create form for either `SourceGroup` or `Source` objects.

## 0.1.3

[Compare the full difference](https://github.com/andrlik/django-quotes/compare/v0.1.2...v0.1.3)

- Adds a configuration option for controlling how many quotes should be retrieved for random quote selection from a
  `SourceGroup`. To make use of this option, add the variable `MAX_QUOTES_FOR_RANDOM_GROUP_SET` to your project's
  `settings.py`.
- Bugfix: `SourceGroup` random group selection now prioritizes quotes that have been served less often via the
  `QuoteStats.times_used` value. This was already the case when selecting from a single `Source`, but the behavior
  is now consistent for `SourceGroup` as well.

## 0.1.2

- Adds a configuration option for controlling how many quotes should be retrieved for random quote selection.
  To make use of this option, add the variable ``MAX_QUOTES_FOR_RANDOM_SET`` in your project's ``settings.py`` file.
