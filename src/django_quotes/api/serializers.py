#
# serializers.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

from __future__ import annotations

from rest_framework.serializers import ModelSerializer

from django_quotes.models import Quote, Source, SourceGroup


class SourceGroupSerializer(ModelSerializer):
    """
    Serializer for SourceGroup.

    Includes the following fields:

    - name (str)
    - slug (str)
    - description (str)
    - description_rendered (str)
    """

    class Meta:
        model = SourceGroup
        fields = ["name", "slug", "description", "description_rendered"]


class SourceSerializer(ModelSerializer):
    """
    Serializer for Source.

    Includes the following fields:

    - name (str)
    - group (SourceGroupSerializer)
    - slug (str)
    - description (str)
    - description_rendered (str)
    """

    group = SourceGroupSerializer()

    class Meta:
        model = Source
        fields = ["name", "group", "slug", "description", "description_rendered"]


class QuoteSerializer(ModelSerializer):
    """
    Serializer for Quote.

    Includes the following fields:

    - quote (str)
    - quote_rendered (str)
    - source (SourceSerializer)
    - citation (str)
    - citation_url (str)
    """

    source = SourceSerializer()  # type: ignore

    class Meta:
        model = Quote
        fields = ["quote", "quote_rendered", "source", "citation", "citation_url"]
