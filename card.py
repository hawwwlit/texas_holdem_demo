from typing import List
import random
from treys import Card as TreysCard
from treys import Deck as TreysDeck

class Card:
    SUITS = ['♠', '♥', '♦', '♣']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    # Mapping for treys conversion
    SUIT_MAP = {'♠': 's', '♥': 'h', '♦': 'd', '♣': 'c'}
    RANK_MAP = {
        '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '10': 'T',
        'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'
    }
    
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
        # Create treys card representation
        self.treys_card = TreysCard.new(f"{self.RANK_MAP[rank]}{self.SUIT_MAP[suit]}")
        
    def __str__(self):
        return f"{self.rank}{self.suit}"
    
    def get_value(self) -> int:
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 14
        return int(self.rank)

class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self.reset()
        
    def reset(self):
        self.cards = [Card(suit, rank) for suit in Card.SUITS for rank in Card.RANKS]
        
    def shuffle(self):
        random.shuffle(self.cards)
        
    def draw(self) -> Card:
        if not self.cards:
            raise ValueError("No cards left in deck!")
        return self.cards.pop() 