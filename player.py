from typing import List
import random
from treys import Evaluator
from card import Card

class Player:
    def __init__(self, name: str, chips: int = 1000, is_ai: bool = False):
        self.name = name
        self.chips = chips
        self.hand: List[Card] = []
        self.is_ai = is_ai
        self.current_bet = 0
        self.folded = False
        self.evaluator = Evaluator()
        
    def receive_card(self, card: Card):
        self.hand.append(card)
        
    def clear_hand(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False
        
    def make_bet(self, amount: int) -> int:
        if amount > self.chips:
            amount = self.chips
        self.chips -= amount
        self.current_bet += amount
        return amount
    
    def ai_make_decision(self, to_call: int, pot: int, community_cards: List[Card]) -> tuple[str, int]:
        if not self.is_ai:
            raise ValueError("This is not an AI player!")
            
        # Improved AI logic using proper hand evaluation
        hand_strength = self._evaluate_hand_strength(community_cards)
        
        # Convert hand strength to a 0-1 scale (7462 is the worst hand, 1 is the best in treys)
        normalized_strength = (7462 - hand_strength) / 7462
        
        # If the call amount is too high relative to our chips, be more cautious
        if to_call > self.chips // 3:
            normalized_strength *= 0.7
            
        if normalized_strength > 0.8:  # Very strong hand
            if random.random() < 0.7:  # More likely to raise with strong hand
                raise_amount = to_call * 3
                return 'raise', min(raise_amount, self.chips)
            return 'call', to_call
        elif normalized_strength > 0.6:  # Strong hand
            if random.random() < 0.4:
                raise_amount = to_call * 2
                return 'raise', min(raise_amount, self.chips)
            return 'call', to_call
        elif normalized_strength > 0.4:  # Medium hand
            if to_call > self.chips // 3:
                return 'fold', 0
            return 'call', to_call
        else:  # Weak hand
            if to_call > self.chips // 5:
                return 'fold', 0
            if random.random() < 0.2:  # Sometimes bluff
                raise_amount = to_call * 2
                return 'raise', min(raise_amount, self.chips)
            return 'call', to_call
            
    def _evaluate_hand_strength(self, community_cards: List[Card] = None) -> int:
        if not community_cards:
            # Pre-flop evaluation based on card ranks
            if len(self.hand) < 2:  # Not enough cards yet
                return 5000
                
            ranks = [card.get_value() for card in self.hand]
            if ranks[0] == ranks[1]:  # Pocket pair
                return 2000
            elif all(rank > 10 for rank in ranks):  # Both high cards
                return 3000
            elif any(rank > 10 for rank in ranks):  # One high card
                return 4000
            else:
                return 5000
        
        # Convert cards to treys format
        board = [card.treys_card for card in community_cards]
        hole_cards = [card.treys_card for card in self.hand]
        
        # Get hand rank (lower is better in treys)
        return self.evaluator.evaluate(board, hole_cards)
    
    def get_hand_rank_name(self, community_cards: List[Card]) -> str:
        if not community_cards:
            return "High Card"
            
        board = [card.treys_card for card in community_cards]
        hole_cards = [card.treys_card for card in self.hand]
        
        rank = self.evaluator.evaluate(board, hole_cards)
        return self.evaluator.class_to_string(self.evaluator.get_rank_class(rank)) 