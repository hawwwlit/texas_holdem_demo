import unittest
from typing import List
from card import Card, Deck
from player import Player
from betting import BettingRound
from game_state import GameState
from game import TexasHoldem

class MockPlayer(Player):
    def __init__(self, name: str, chips: int = 1000, is_ai: bool = True):
        super().__init__(name, chips, is_ai)
        self.next_actions = []  # List of (action, amount) tuples
        self.mock_hand = []     # Predetermined cards for testing
        
    def ai_make_decision(self, to_call: int, pot: int, community_cards: List = None) -> tuple[str, int]:
        if not self.next_actions:
            return 'fold', 0
        action, amount = self.next_actions.pop(0)
        if action == 'call':
            return action, to_call
        return action, amount
        
    def receive_card(self, card: Card):
        if self.mock_hand:
            self.hand.append(self.mock_hand.pop(0))
        else:
            super().receive_card(card)
            
    def make_decision(self, to_call: int, pot: int, community_cards: List = None) -> tuple[str, int]:
        """Override for both AI and human players in testing"""
        return self.ai_make_decision(to_call, pot, community_cards)

class MockDeck(Deck):
    def __init__(self, predetermined_cards: List[Card] = None):
        super().__init__()
        if predetermined_cards:
            self.cards = predetermined_cards

class TestPokerGameEndToEnd(unittest.TestCase):
    def setUp(self):
        # Create players
        self.human = MockPlayer("You", 1000, is_ai=False)
        self.ai1 = MockPlayer("AI Player 1", 1000)
        self.ai2 = MockPlayer("AI Player 2", 1000)
        self.ai3 = MockPlayer("AI Player 3", 1000)
        
    def test_full_round_with_pair_vs_high_card(self):
        """Test a complete round where one player has a pair and others have high cards"""
        # Set up predetermined hands
        self.human.mock_hand = [
            Card('♠', 'A'),
            Card('♥', 'A')  # Pair of Aces
        ]
        self.ai1.mock_hand = [
            Card('♦', 'K'),
            Card('♣', 'Q')  # King high
        ]
        self.ai2.mock_hand = [
            Card('♥', 'J'),
            Card('♦', '10')  # Jack high
        ]
        self.ai3.mock_hand = [
            Card('♣', '9'),
            Card('♠', '8')  # Nine high
        ]
        
        # Set up community cards
        community_cards = [
            Card('♦', '2'),
            Card('♥', '3'),
            Card('♠', '4'),
            Card('♣', '5'),
            Card('♦', '7')
        ]
        
        # Create game with mock deck
        game = TexasHoldem(num_ai_players=3)
        game.players = [self.human, self.ai1, self.ai2, self.ai3]
        game.deck.cards = community_cards
        
        # Set up betting sequences
        self.human.next_actions = [
            ('raise', 60),  # Pre-flop raise
            ('raise', 100), # Flop raise
            ('check', 0),   # Turn
            ('check', 0)    # River
        ]
        self.ai1.next_actions = [
            ('call', 60),   # Call pre-flop
            ('call', 100),  # Call flop
            ('check', 0),   # Turn
            ('check', 0)    # River
        ]
        self.ai2.next_actions = [
            ('call', 60),   # Call pre-flop
            ('fold', 0)     # Fold on flop
        ]
        self.ai3.next_actions = [
            ('call', 60),   # Call pre-flop
            ('fold', 0)     # Fold on flop
        ]
        
        # Play one round
        game._play_round()
        
        # Verify winner and pot
        self.assertEqual(self.human.chips > 1000, True)  # Human should win with pair of Aces
        
    def test_full_round_with_all_in_scenario(self):
        """Test a complete round with an all-in situation"""
        # Set up players with different chip stacks
        self.human.chips = 100
        self.ai1.chips = 200
        self.ai2.chips = 300
        self.ai3.chips = 400
        
        # Set up hands
        self.human.mock_hand = [
            Card('♠', 'K'),
            Card('♥', 'K')  # Pair of Kings
        ]
        self.ai1.mock_hand = [
            Card('♦', 'Q'),
            Card('♣', 'Q')  # Pair of Queens
        ]
        self.ai2.mock_hand = [
            Card('♥', 'J'),
            Card('♦', '10')
        ]
        self.ai3.mock_hand = [
            Card('♣', '9'),
            Card('♠', '8')
        ]
        
        # Set up community cards
        community_cards = [
            Card('♦', '2'),
            Card('♥', '3'),
            Card('♠', '4'),
            Card('♣', '5'),
            Card('♦', '7')
        ]
        
        # Create game
        game = TexasHoldem(num_ai_players=3)
        game.players = [self.human, self.ai1, self.ai2, self.ai3]
        game.deck.cards = community_cards
        
        # Set up betting sequences
        self.human.next_actions = [
            ('raise', 100)  # All-in
        ]
        self.ai1.next_actions = [
            ('call', 100)   # Call all-in
        ]
        self.ai2.next_actions = [
            ('fold', 0)
        ]
        self.ai3.next_actions = [
            ('fold', 0)
        ]
        
        # Play round
        game._play_round()
        
        # Verify all-in mechanics
        self.assertEqual(self.human.chips, 0)  # Human should be all-in
        self.assertTrue(self.ai2.folded)  # AI2 should have folded
        self.assertTrue(self.ai3.folded)  # AI3 should have folded
        
    def test_full_round_with_flush_scenario(self):
        """Test a complete round where one player makes a flush"""
        # Set up hands for flush scenario
        self.human.mock_hand = [
            Card('♥', 'A'),
            Card('♥', 'K')  # Hearts
        ]
        self.ai1.mock_hand = [
            Card('♦', 'A'),
            Card('♦', 'K')  # Diamonds
        ]
        self.ai2.mock_hand = [
            Card('♣', 'Q'),
            Card('♠', 'J')
        ]
        self.ai3.mock_hand = [
            Card('♠', '10'),
            Card('♣', '9')
        ]
        
        # Community cards with three hearts
        community_cards = [
            Card('♥', '2'),
            Card('♥', '3'),
            Card('♥', '4'),  # Three more hearts for human's flush
            Card('♦', '5'),
            Card('♣', '7')
        ]
        
        # Create game
        game = TexasHoldem(num_ai_players=3)
        game.players = [self.human, self.ai1, self.ai2, self.ai3]
        game.deck.cards = community_cards
        
        # Set up betting sequences
        self.human.next_actions = [
            ('raise', 60),   # Pre-flop raise
            ('raise', 120),  # Flop raise
            ('check', 0),    # Turn
            ('check', 0)     # River
        ]
        self.ai1.next_actions = [
            ('call', 60),    # Call pre-flop
            ('call', 120),   # Call flop
            ('check', 0),    # Turn
            ('check', 0)     # River
        ]
        self.ai2.next_actions = [
            ('fold', 0)      # Fold pre-flop
        ]
        self.ai3.next_actions = [
            ('fold', 0)      # Fold pre-flop
        ]
        
        # Play round
        game._play_round()
        
        # Verify flush wins
        self.assertEqual(self.human.chips > 1000, True)  # Human should win with flush
        
    def test_multiple_rounds(self):
        """Test playing multiple rounds with chip tracking"""
        game = TexasHoldem(num_ai_players=3)
        game.players = [self.human, self.ai1, self.ai2, self.ai3]
        
        # Set up actions for multiple rounds
        self.human.next_actions = [('fold', 0)] * 3  # Fold each round
        self.ai1.next_actions = [('call', 20), ('check', 0)] * 3  # Call and check each round
        self.ai2.next_actions = [('fold', 0)] * 3  # Fold each round
        self.ai3.next_actions = [('fold', 0)] * 3  # Fold each round
        
        # Play 3 rounds
        for _ in range(3):
            game._play_round()
            game.dealer_pos = (game.dealer_pos + 1) % len(game.players)
        
        # Verify chip counts are being tracked correctly
        total_chips = sum(p.chips for p in game.players)
        self.assertEqual(total_chips, 4000)  # Total chips should remain constant
        
    def test_showdown_with_tied_hands(self):
        """Test a showdown scenario with tied hands"""
        # Both players have pair of Aces
        self.human.mock_hand = [
            Card('♠', 'A'),
            Card('♥', 'A')
        ]
        self.ai1.mock_hand = [
            Card('♦', 'A'),
            Card('♣', 'A')
        ]
        self.ai2.mock_hand = [
            Card('♥', 'K'),
            Card('♦', 'Q')
        ]
        self.ai3.mock_hand = [
            Card('♣', 'J'),
            Card('♠', '10')
        ]
        
        # Community cards
        community_cards = [
            Card('♥', '2'),
            Card('♦', '3'),
            Card('♠', '4'),
            Card('♣', '5'),
            Card('♦', '7')
        ]
        
        # Create game
        game = TexasHoldem(num_ai_players=3)
        game.players = [self.human, self.ai1, self.ai2, self.ai3]
        game.deck.cards = community_cards
        
        # Set up betting sequences
        self.human.next_actions = [
            ('raise', 60),   # Pre-flop raise
            ('check', 0),    # Flop
            ('check', 0),    # Turn
            ('check', 0)     # River
        ]
        self.ai1.next_actions = [
            ('call', 60),    # Call pre-flop
            ('check', 0),    # Flop
            ('check', 0),    # Turn
            ('check', 0)     # River
        ]
        self.ai2.next_actions = [
            ('fold', 0)      # Fold pre-flop
        ]
        self.ai3.next_actions = [
            ('fold', 0)      # Fold pre-flop
        ]
        
        # Play round
        game._play_round()
        
        # Verify kicker determines winner
        final_chips = [p.chips for p in game.players]
        self.assertNotEqual(final_chips[0], final_chips[1])  # Someone should win based on kicker

if __name__ == '__main__':
    unittest.main() 