import unittest
from typing import List
from card import Card, Deck
from player import Player
from betting import BettingRound
from game_state import GameState

class MockPlayer(Player):
    def __init__(self, name: str, chips: int = 1000, is_ai: bool = True):
        super().__init__(name, chips, is_ai)
        self.next_actions = []  # List of (action, amount) tuples
        
    def ai_make_decision(self, to_call: int, pot: int, community_cards: List = None) -> tuple[str, int]:
        if not self.next_actions:
            return 'fold', 0
        return self.next_actions.pop(0)

class TestPokerGame(unittest.TestCase):
    def setUp(self):
        # Create players with predetermined actions
        self.player1 = MockPlayer("Player 1", 1000)
        self.player2 = MockPlayer("Player 2", 1000)
        self.player3 = MockPlayer("Player 3", 1000)
        self.players = [self.player1, self.player2, self.player3]
        
        # Create betting round
        self.betting = BettingRound(self.players)
        
    def test_simple_betting_round(self):
        """Test a simple betting round where everyone calls"""
        # Set up player actions
        self.player1.next_actions = [('call', 20)]  # Call big blind
        self.player2.next_actions = [('call', 20)]  # Call big blind
        self.player3.next_actions = [('check', 0)]  # Big blind checks
        
        # Start from UTG position (after big blind)
        self.betting.current_bet = 20  # Big blind amount
        result = self.betting.handle_betting_round("pre-flop", 0)
        
        self.assertTrue(result)
        self.assertEqual(self.betting.pot, 60)  # 20 * 3 players
        self.assertEqual(self.player1.chips, 980)
        self.assertEqual(self.player2.chips, 980)
        self.assertEqual(self.player3.chips, 980)
        
    def test_raise_and_fold(self):
        """Test when one player raises and others fold"""
        # Set up player actions
        self.player1.next_actions = [('raise', 60)]  # Raise to 60
        self.player2.next_actions = [('fold', 0)]
        self.player3.next_actions = [('fold', 0)]
        
        # Start betting round
        self.betting.current_bet = 20
        result = self.betting.handle_betting_round("pre-flop", 0)
        
        self.assertTrue(result)
        self.assertEqual(self.betting.pot, 60)  # Initial 20 + raise to 60
        self.assertEqual(self.player1.chips, 940)  # Lost 60
        self.assertEqual(self.player2.chips, 1000)  # Folded, no loss
        self.assertEqual(self.player3.chips, 1000)  # Folded, no loss
        
    def test_multiple_raises(self):
        """Test multiple raises in a round"""
        # Set up player actions
        self.player1.next_actions = [('raise', 40), ('call', 100)]  # Raise to 40, then call 100
        self.player2.next_actions = [('raise', 100), ('fold', 0)]   # Re-raise to 100, then fold
        self.player3.next_actions = [('call', 100), ('fold', 0)]    # Call 100, then fold
        
        # Start betting round
        self.betting.current_bet = 20
        result = self.betting.handle_betting_round("pre-flop", 0)
        
        self.assertTrue(result)
        self.assertEqual(self.player1.chips, 900)  # Paid 100
        self.assertEqual(self.player2.chips, 900)  # Paid 100
        self.assertEqual(self.player3.chips, 900)  # Paid 100
        self.assertEqual(self.betting.pot, 300)    # 100 * 3 players
        
    def test_all_in_scenario(self):
        """Test when a player goes all-in"""
        # Set up players with different chip amounts
        self.player1.chips = 50
        self.player2.chips = 200
        self.player3.chips = 100
        
        # Set up actions
        self.player1.next_actions = [('raise', 50)]  # All-in
        self.player2.next_actions = [('call', 50)]   # Call all-in
        self.player3.next_actions = [('call', 50)]   # Call all-in
        
        # Start betting round
        self.betting.current_bet = 20
        result = self.betting.handle_betting_round("pre-flop", 0)
        
        self.assertTrue(result)
        self.assertEqual(self.player1.chips, 0)    # All-in
        self.assertEqual(self.player2.chips, 150)  # Called 50
        self.assertEqual(self.player3.chips, 50)   # Called 50
        self.assertEqual(self.betting.pot, 150)    # 50 * 3 players
        
    def test_check_around(self):
        """Test when all players check"""
        # Set up player actions
        self.player1.next_actions = [('check', 0)]
        self.player2.next_actions = [('check', 0)]
        self.player3.next_actions = [('check', 0)]
        
        # Start betting round (post-flop)
        result = self.betting.handle_betting_round("flop", 0)
        
        self.assertTrue(result)
        self.assertEqual(self.betting.pot, 0)  # No bets made
        self.assertEqual(self.player1.chips, 1000)
        self.assertEqual(self.player2.chips, 1000)
        self.assertEqual(self.player3.chips, 1000)
        
    def test_blinds_posting(self):
        """Test correct posting of blinds"""
        # Post blinds with dealer at position 0
        self.betting.post_blinds(0)
        
        # Player 2 should be small blind, Player 3 big blind
        self.assertEqual(self.player2.chips, 990)  # Posted small blind 10
        self.assertEqual(self.player3.chips, 980)  # Posted big blind 20
        self.assertEqual(self.betting.pot, 30)     # Total blinds
        self.assertEqual(self.betting.current_bet, 20)  # Current bet should be big blind

if __name__ == '__main__':
    unittest.main() 