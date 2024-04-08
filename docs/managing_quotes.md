---
title: Managing Sources and Quotes
---

Django-Quotes uses a number of rudimentary data models with basic scaffolding views to manage the data. User-based permissions are used to control access to the data.

## Models

### Source Group

::: django_quotes.models.SourceGroup
    handler: python
    selection:
      members:
        - generate_markov_sentence
        - get_random_quote
    rendering:
      show_root_toc_entry: False
      heading_level: 4
      
### Source

::: django_quotes.models.Source
    handler: python
    selection:
      members:
        - generate_markov_sentence
        - get_random_quote
    rendering:
      heading_level: 4
      
### Quote

::: django_quotes.models.Quote
    handler: python
    selection:
      members:
        - save
    rendering:
      heading_level: 4
      
### Group Stats

::: django_quotes.models.GroupStats
    handler: python
    selection:
      members:
        - generate_model_from_corpus
    rendering:
      heading_level: 4
  
### Source Stats
 
::: django_quotes.models.SourceStats
    handler: python
    selection:
      members:
        - generate_model_from_corpus
    rendering:
      heading_level: 4
      
### Quote Stats
       
::: django_quotes.models.QuoteStats
    handler: python
    selection:
      members:
        - generate_model_from_corpus
    rendering:
      heading_level: 4
   
## Views

The core views for managing the quotes consist of simple data entry and manipulation functions, heavily utilizing Django's generic views. All views require login.

### Source Group List

Provides a paginated list of source groups created by logged in user.

Served at `/app/groups/`.

### Source Group Create

Allows a user to define a new `SourceGroup`.

Served at `app/groups/create/`.

### Source Group Detail

Displays a detailed view of a source group with a sampling of the :ref:`Source` objects associated, with links to full listings.

Served at `app/groups/<slug:group>/`.

### Source Group Update

Allows user to update the source group's attributes.

Served at `app/groups/<slug:group>/edit/`.

### Source Group Delete

Allows user to delete a `SourceGroup` and all child data associated with it.

Served at `app/groups/<slug:group>/delete/`.

### Source List

Paginated list of all the :ref:`Source` objects associated with a given group, along with aggregate statistics such as total quotes.

Served at `app/groups/<slug:group>/sources/`.

### Source Create

Enables a user to create a new `Source` for a given `SourceGroup`.

Served at `app/groups/<slug:group>/sources/create/`.

### Source Detail

Detail view of the :ref:`Source` object including a sampling of recently created/modified quotes with links to full listings.

Served at `app/sources/<slug:source>/`.

### Source Update

Enables editing of the source attributes such as name, description, whether to allow markov requests, etc.

Served at `app/sources/<slug:source>/edit/`.

### Source Delete

Enable deleting a source and all child data associated with it.

Served at `app/sources/<slug:source>/delete/`.

### Quote List

Provides a paginated list of quotes created for the given :ref:`Source`.

Served at `app/sources/<slug:source>/quotes/`.

### Quote Create

Add a quote for the given `Source`.

Served at `app/sources/<slug:source>/quotes/create/`.

### Quote Detail

Shows details of the quote including the HTML rendered version of the text, and in the future will also include statistical data.

Served at `app/quotes/<int:quote>/`.

### Quote Update

Enables the user to update the quote text for a given `Quote` object.

Served at `app/quotes/<int:quote>/edit/`.

### Quote Delete

Enables the user to delete a given `Quote` object.

Served at `app/quotes/<int:quote>/delete/`.

## Signals

There are two signals provided that are used to update statistics related to `SourceGroup`, `Source`, and `Quote` objects. If you implement your own methods and want to ensure your stats related to `quotes_requested` and `quotes_generated` remain accurate, you will need to send these.

### Quote Retrieved

```python
django_quotes.signals.quote_random_retrieved.send(sender, instance, quote_retrieved, *args, **kwargs)
```

The `sender` should in most contexts be either `Source` or `SourceGroup` class definitions (**not instances**).
The `instance` should be the actual instance of the `Source` that is being used.

This signal will update the ``quotes_retrieved`` stats in the related ``GroupStats``, ``SourceStats``, and ``QuoteStats`` objects.

### Quote Generated

```python
django_quotes.signals.markov_sentence_generated.send(sender, instance, *args, **kwargs)
```

The `sender` should in most contexts be either `Source` or `SourceGroup` class definitions (**not instances**).
The `instance` should be the actual instance of the `Source` that is being used.

This signal will update the ``quotes_generated`` stats in the related ``GroupStats`` and ``SourceStats`` objects.

## Management Commands

`django-quotes` provides a management command you can use to check and generate new Markov models for both `SourceGroup` and `Source` objects.

``bash
python manage.py makemarkov
``
