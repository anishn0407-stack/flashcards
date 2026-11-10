from datetime import date


class Card:
    def __init__(self, question, answer, box=1, next_review=None, card_id=None):
        self.id = card_id
        self.question = question
        self.answer = answer
        self.box = box
        self.next_review = next_review or date.today()

    def is_due(self):
        return self.next_review <= date.today()

    def describe(self):
        return f"Q: {self.question} | A: {self.answer} | Box {self.box}"