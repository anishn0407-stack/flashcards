from datetime import date, timedelta


class Scheduler:
    GAPS = {1: 1, 2: 3, 3: 7}
    MAX_BOX = 3

    def review(self, card, easy):
        if easy:
            card.box = min(card.box + 1, self.MAX_BOX)
        else:
            card.box = 1
        card.next_review = date.today() + timedelta(days=self.GAPS[card.box])