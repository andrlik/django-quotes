from typing import List

import re
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model

from django_quotes.models import Quote, Source, SourceGroup
from tests.factories.users import UserFactory

User = get_user_model()


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


# Enabling testing for view documentation per: https://simonwillison.net/2018/Jul/28/documentation-unit-tests/


docs_path = Path(__file__).parent / "docs"
label_re = re.compile(r"\.\. _([^\s:]+):")


def get_headings(filename, underline="-"):
    content = (docs_path / filename).open().read()
    heading_re = re.compile(r"(\S+)\n\{}+\n".format(underline))
    return set(heading_re.findall(content))


def get_labels(filename):
    content = (docs_path / filename).open().read()
    return set(label_re.findall(content))


@pytest.fixture(scope="session")
def documented_views():
    view_labels = set()
    for filename in docs_path.glob("*.rst"):
        for label in get_labels(filename):
            first_word = label.split("_")[0]
            if first_word.endswith("View"):
                view_labels.add(first_word)
    return view_labels


# Courtesy of https://randomwordgenerator.com/sentence.php
@pytest.fixture(scope="session")
def corpus_sentences() -> List[str]:
    return [
        "She wasn't sure whether to be impressed or concerned that he folded underwear in neat little packages.",
        "She looked into the mirror and saw another person.",
        "Siri became confused when we reused to follow her directions.",
        "The anaconda was the greatest criminal mastermind in this part of the neighborhood.",
        "If eating three-egg omelets causes weight-gain, budgie eggs are a good substitute.",
        "The sunblock was handed to the girl before practice, but the burned skin was proof she did not apply it.",
        "There were three sphered rocks congregating in a cubed room.",
        "She tilted her head back and let whip cream stream into her mouth while taking a bath.",
        "Smoky the Bear secretly started the fires.",
        "Mary realized if her calculator had a history, it would be more embarrassing than her browser history.",
        "He ended up burning his fingers poking someone else's fire.",
        "There was no ice cream in the freezer, nor did they have money to go to the store.",
        "He went back to the video to see what had been recorded and was shocked at what he saw.",
        "The beach was crowded with snow leopards.",
        "The estate agent quickly marked out his territory on the dance floor.",
        "Warm beer on a cold day isn't my idea of fun.",
        "As the asteroid hurtled toward earth, Becky was upset her dentist appointment had been canceled.",
        "After coating myself in vegetable oil I found my success rate skyrocketed.",
        "She was amazed by the large chunks of ice washing up on the beach.",
        "Henry couldn't decide if he was an auto mechanic or a priest.",
    ]


@pytest.fixture
def property_group(user, corpus_sentences):
    cg = SourceGroup.objects.create(name="Wranglin Robots", owner=user)
    for x in range(10):
        allow_markov = False
        if x % 2 == 0:
            allow_markov = True
        c = Source.objects.create(
            name=str(x), group=cg, allow_markov=allow_markov, owner=user
        )
        for quote in corpus_sentences:
            Quote.objects.create(quote=quote, source=c, owner=user)
    yield cg
    cg.delete()
