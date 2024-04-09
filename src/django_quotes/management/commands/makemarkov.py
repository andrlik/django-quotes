#
# makemarkov.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

"""Checks if markov models are out of date, and if so regenerates them."""

from django.core.management.base import BaseCommand

from django_markov.models import MarkovTextModel
from django_quotes.models import SourceGroup


class Command(BaseCommand):
    help = "Checks if markov models are out of date, and if so regenerates them."

    def handle(self, *args, **kwargs):
        groups = SourceGroup.objects.all()
        groups_updated = 0
        characters_updated = 0
        for group in groups:
            if group.text_model is None:  # no cov
                group.text_model = MarkovTextModel.objects.create()
            gmm = group.text_model
            update_group = False
            for character in group.source_set.filter(allow_markov=True):
                if character.markov_ready:
                    quote_to_test = character.quote_set.all().order_by("-modified")[0]
                    if character.text_model is None:  # no cov
                        character.text_model = MarkovTextModel.objects.create()
                    cmm = character.text_model
                    if cmm.modified > gmm.modified:
                        update_group = True
                    if quote_to_test.modified > cmm.modified:
                        character.update_markov_model()
                        characters_updated += 1
                        update_group = True
            if update_group:
                group.update_markov_model()
                groups_updated += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Updated models for {groups_updated} Character Groups " f"and {characters_updated} Characters!"
            )
        )
