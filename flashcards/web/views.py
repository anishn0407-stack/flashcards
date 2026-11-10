from django.http import JsonResponse

from core.deck import Deck

DECK_NAME = "My Deck"
BOXES = [1, 2, 3]


def count_by_box(cards):
    counts = {box: 0 for box in BOXES}
    for card in cards:
        counts[card.box] += 1
    return counts


def mastered_percent(counts, total):
    if total == 0:
        return 0
    return round(100 * counts[3] / total)


def stats(request):
    deck = Deck(DECK_NAME)
    total = len(deck.cards)
    counts = count_by_box(deck.cards)

    data = {
        "deck": DECK_NAME,
        "total_cards": total,
        "due_today": len(deck.due_cards()),
        "cards_per_box": counts,
        "mastered_percent": mastered_percent(counts, total),
    }
    return JsonResponse(data, json_dumps_params={"indent": 2})