from typing import List
from colorama import init, Fore, Style
from card import Card, Deck
from player import Player
from betting import BettingRound
from game_state import GameState

init()  # Initialize colorama

class TexasHoldem:
    def __init__(self, num_ai_players: int = 3):
        # Create players
        self.players = [Player("You", is_ai=False)]
        for i in range(num_ai_players):
            self.players.append(Player(f"AI Player {i+1}", is_ai=True))
            
        self.deck = Deck()
        self.dealer_pos = 0  # Position of the dealer button
        self.game_state = GameState(self.players)
        self.betting_round = BettingRound(self.players)
            
    def play_game(self):
        while True:
            self._play_round()
            
            # Show current chip counts
            self.game_state.show_chip_counts()
            
            # Move dealer button
            self.dealer_pos = (self.dealer_pos + 1) % len(self.players)
            
            # Ask to continue
            choice = input(f"{Fore.YELLOW}Play another round? (y/n): {Style.RESET_ALL}").lower()
            if choice != 'y':
                break
                
    def _play_round(self):
        # Reset game state
        self.deck.reset()
        self.deck.shuffle()
        self.game_state.community_cards = []
        
        for player in self.players:
            player.clear_hand()
            
        # Post blinds
        self.betting_round.post_blinds(self.dealer_pos)
            
        # Deal hole cards
        for _ in range(2):
            for i in range(len(self.players)):
                # Deal cards starting from small blind position
                player_pos = (self.dealer_pos + i + 1) % len(self.players)
                self.players[player_pos].receive_card(self.deck.draw())
                
        print(f"\n{Fore.GREEN}=== New Round Started ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}Dealer: {self.players[self.dealer_pos].name}{Style.RESET_ALL}")
        self.game_state.show_game_state(self.players[0])
        
        # Pre-flop betting (start from UTG position)
        if self.betting_round.handle_betting_round("pre-flop", start_from=(self.dealer_pos + 3) % len(self.players)):
            # Flop
            self._deal_community_cards(3)
            if self.betting_round.handle_betting_round("flop", start_from=(self.dealer_pos + 1) % len(self.players), community_cards=self.game_state.community_cards):
                # Turn
                self._deal_community_cards(1)
                if self.betting_round.handle_betting_round("turn", start_from=(self.dealer_pos + 1) % len(self.players), community_cards=self.game_state.community_cards):
                    # River
                    self._deal_community_cards(1)
                    self.betting_round.handle_betting_round("river", start_from=(self.dealer_pos + 1) % len(self.players), community_cards=self.game_state.community_cards)
                    
        # Show all hands and determine winner
        self.game_state.handle_showdown(self.betting_round.pot)
        
    def _deal_community_cards(self, count: int):
        for _ in range(count):
            self.game_state.community_cards.append(self.deck.draw())
        print(f"\n{Fore.CYAN}Community Cards: {' '.join(str(card) for card in self.game_state.community_cards)}{Style.RESET_ALL}") 