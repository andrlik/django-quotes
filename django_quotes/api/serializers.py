from rest_framework.serializers import ModelSerializer

from ..models import Character, CharacterGroup, Quote


class CharacterGroupSerializer(ModelSerializer):
    class Meta:
        model = CharacterGroup
        fields = ["name", "slug", "description", "description_rendered"]


class CharacterSerializer(ModelSerializer):
    group = CharacterGroupSerializer()

    class Meta:
        model = Character
        fields = ["name", "group", "slug", "description", "description_rendered"]


class QuoteSerializer(ModelSerializer):
    character = CharacterSerializer()

    class Meta:
        model = Quote
        fields = ["quote", "quote_rendered", "character", "citation", "citation_url"]
