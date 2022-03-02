import markovify
import spacy

nlp = spacy.load("en_core_web_sm")


class MarkovPOSText(markovify.Text):
    """
    Use spacy to improve Markov text generation per example in:
    https://github.com/jsvine/markovify
    """

    def word_split(self, sentence):
        return ["::".join((word.orth_, word.pos_)) for word in nlp(sentence)]  # type: ignore

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence
