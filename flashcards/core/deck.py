import os
import sqlite3
from datetime import date

from core.card import Card

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "flashcards.db")


class Deck:
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.create_table()
        self.load()

    def connect(self):
        return sqlite3.connect(DB_PATH)

    def create_table(self):
        conn = self.connect()
        conn.execute(
            """CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck TEXT,
                question TEXT,
                answer TEXT,
                box INTEGER,
                next_review TEXT
            )"""
        )
        conn.commit()
        conn.close()

    def add_card(self, card):
        conn = self.connect()
        cursor = conn.execute(
            "INSERT INTO cards (deck, question, answer, box, next_review) VALUES (?, ?, ?, ?, ?)",
            (self.name, card.question, card.answer, card.box, card.next_review.isoformat()),
        )
        card.id = cursor.lastrowid
        conn.commit()
        conn.close()
        self.cards.append(card)

    def update_card(self, card):
        conn = self.connect()
        conn.execute(
            "UPDATE cards SET box = ?, next_review = ? WHERE id = ?",
            (card.box, card.next_review.isoformat(), card.id),
        )
        conn.commit()
        conn.close()

    def load(self):
        conn = self.connect()
        rows = conn.execute(
            "SELECT id, question, answer, box, next_review FROM cards WHERE deck = ?",
            (self.name,),
        ).fetchall()
        conn.close()
        self.cards = [
            Card(q, a, box, date.fromisoformat(nr), card_id)
            for (card_id, q, a, box, nr) in rows
        ]

    def due_cards(self):
        return [c for c in self.cards if c.is_due()]