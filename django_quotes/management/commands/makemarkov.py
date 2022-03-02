from django.core.management.base import BaseCommand

from ...models import CharacterGroup, CharacterMarkovModel, GroupMarkovModel


class Command(BaseCommand):
    help = "Checks if markov models are out of date, and if so regenerates them."

    def handle(self, *args, **kwargs):
        groups = CharacterGroup.objects.all()
        groups_updated = 0
        characters_updated = 0
        for group in groups:
            gmm = GroupMarkovModel.objects.get(group=group)
            update_group = False
            for character in group.character_set.filter(allow_markov=True):
                if character.markov_ready:
                    quote_to_test = character.quote_set.all().order_by("-modified")[0]
                    cmm = CharacterMarkovModel.objects.get(character=character)
                    if cmm.modified > gmm.modified:
                        update_group = True
                    if quote_to_test.modified > cmm.modified:
                        cmm.generate_model_from_corpus()
                        characters_updated += 1
                        update_group = True
            if update_group:
                gmm.generate_model_from_corpus()
                groups_updated += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Updated models for {groups_updated} Character Groups and {characters_updated} Characters!"
            )
        )
