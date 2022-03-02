from rest_framework.serializers import ModelSerializer

from ..models import Quote, Source, SourceGroup


class SourceGroupSerializer(ModelSerializer):
    class Meta:
        model = SourceGroup
        fields = ["name", "slug", "description", "description_rendered"]


class SourceSerializer(ModelSerializer):
    group = SourceGroupSerializer()

    class Meta:
        model = Source
        fields = ["name", "group", "slug", "description", "description_rendered"]


class QuoteSerializer(ModelSerializer):
    source = SourceSerializer()

    class Meta:
        model = Quote
        fields = ["quote", "quote_rendered", "source", "citation", "citation_url"]
