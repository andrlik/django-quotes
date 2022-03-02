from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.fields import CharField
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from ..models import Character, CharacterGroup
from .serializers import CharacterGroupSerializer, CharacterSerializer, QuoteSerializer


class CharacterGroupViewSet(
    AutoPermissionViewSetMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    """
    A generic viewset for listing and retrieving details on character groups.
    """

    serializer_class = CharacterGroupSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "group"
    permission_type_map = {
        "create": "add",
        "destroy": "delete",
        "list": None,
        "partial_update": "change",
        "retrieve": "read",
        "update": "change",
        "get_random_quote": "read",
        "generate_sentence": "read",
    }

    def get_queryset(self, *args, **kwargs):
        return CharacterGroup.objects.filter(
            owner=self.request.user
        ) | CharacterGroup.objects.filter(public=True)

    @extend_schema(responses={200: QuoteSerializer})
    @action(detail=True, methods=["get"])
    def get_random_quote(self, request, group=None):
        g = self.get_object()
        quote = g.get_random_quote()
        if quote is not None:
            qs = QuoteSerializer(quote)
            return Response(status=status.HTTP_200_OK, data=qs.data)
        return Response(
            status=status.HTTP_404_NOT_FOUND, data={"error": "No quotes found."}
        )

    @extend_schema(
        responses={
            200: inline_serializer(
                name="generated_sentence", fields={"sentence": CharField()}
            )
        }
    )
    @action(detail=True, methods=["get"])
    def generate_sentence(self, request, group=None):
        g = self.get_object()
        if g.markov_characters == 0:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={
                    "error": "This group does not currently allow sentence generation."
                },
            )
        sentence = g.generate_markov_sentence()
        if sentence is not None:
            return Response(status=status.HTTP_200_OK, data={"sentence": sentence})
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            data={"error": "Insufficent data to generate sentence."},
        )


class CharacterViewSet(
    AutoPermissionViewSetMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    """
    Retrieve and list views for characters.
    """

    serializer_class = CharacterSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "character"
    permission_type_map = {
        "create": "add",
        "destroy": "delete",
        "list": None,
        "partial_update": "change",
        "retrieve": "read",
        "update": "change",
        "get_random_quote": "read",
        "generate_sentence": "read",
    }

    def get_queryset(self, *args, **kwargs):
        group_slug = self.request.query_params.get("group")
        queryset = Character.objects.filter(
            owner=self.request.user
        ) | Character.objects.filter(public=True)
        if group_slug:
            try:
                group = CharacterGroup.objects.get(slug=group_slug)
            except ObjectDoesNotExist:
                return CharacterGroup.objects.none()
            queryset = queryset.filter(group=group)
        return queryset

    @extend_schema(responses={200: QuoteSerializer})
    @action(detail=True, methods=["get"])
    def get_random_quote(self, request, character=None):
        character = self.get_object()
        quote = character.get_random_quote()
        if quote is not None:
            qs = QuoteSerializer(quote)
            return Response(status=status.HTTP_200_OK, data=qs.data)
        return Response(
            status=status.HTTP_404_NOT_FOUND, data={"error": "No quotes found."}
        )

    @extend_schema(
        responses={
            200: inline_serializer(
                name="generated_sentence", fields={"sentence": CharField()}
            )
        }
    )
    @action(detail=True, methods=["get"])
    def generate_sentence(self, request, character=None):
        character = self.get_object()
        if not character.allow_markov:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"error": "This character does not permit sentence generation."},
            )
        sentence = character.get_markov_sentence()
        if sentence is not None:
            return Response(status=status.HTTP_200_OK, data={"sentence": sentence})
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            data={
                "error": "Unable to generate markov sentence. This character may not have enough quotes yet."
            },
        )
