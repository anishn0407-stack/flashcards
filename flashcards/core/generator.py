import nltk

from core.card import Card

DEFINITION_WORDS = [" is ", " are "]
ARTICLES = ["a ", "an ", "the "]
MIN_WORDS = 4
MIN_BLANK_LENGTH = 5


def ensure_nltk_data():
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab")


class CardGenerator:
    def __init__(self):
        ensure_nltk_data()

    def split_sentences(self, notes):
        return nltk.sent_tokenize(notes)

    def find_definition_word(self, sentence):
        for word in DEFINITION_WORDS:
            if word in sentence:
                return word
        return None

    def clean_term(self, term):
        term = term.strip()
        for article in ARTICLES:
            if term.lower().startswith(article):
                return term[len(article):]
        return term

    def make_definition_card(self, sentence, definition_word):
        term, rest = sentence.split(definition_word, 1)
        term = self.clean_term(term)
        question = f"What{definition_word}{term}?"
        answer = rest.strip().rstrip(".")
        answer = answer[0].upper() + answer[1:]
        return Card(question, answer)

    def make_blank_card(self, sentence):
        words = sentence.split()
        candidates = [w.strip(".,;:()") for w in words]
        candidates = [w for w in candidates if len(w) >= MIN_BLANK_LENGTH]
        if not candidates:
            return None
        target = max(candidates, key=len)
        question = "Fill in the blank: " + sentence.replace(target, "_____", 1)
        return Card(question, target)

    def generate(self, notes):
        cards = []
        for sentence in self.split_sentences(notes):
            if len(sentence.split()) < MIN_WORDS:
                continue
            definition_word = self.find_definition_word(sentence)
            if definition_word:
                card = self.make_definition_card(sentence, definition_word)
            else:
                card = self.make_blank_card(sentence)
            if card:
                cards.append(card)
        return cards