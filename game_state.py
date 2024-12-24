from typing import List
from colorama import Fore, Style
from card import Card
from player import Player
from treys import Evaluator

class GameState:
    def __init__(self, players: List[Player]):
        self.players = players
        self.community_cards: List[Card] = []
        self.evaluator = Evaluator()
        
    def show_game_state(self, human_player: Player):
        print(f"\n{Fore.CYAN}Pot: {self.get_total_pot()}{Style.RESET_ALL}")
        if self.community_cards:
            print(f"Community Cards: {' '.join(str(card) for card in self.community_cards)}")
        print(f"Your Hand: {' '.join(str(card) for card in human_player.hand)}")
        if self.community_cards:
            print(f"Your hand rank: {human_player.get_hand_rank_name(self.community_cards)}")
        print(f"Your Chips: {human_player.chips}")
        
    def show_chip_counts(self):
        print("\nCurrent chip counts:")
        for player in self.players:
            print(f"{player.name}: {player.chips}")
            
    def get_total_pot(self) -> int:
        # Calculate total pot from the betting round
        total = 0
        for player in self.players:
            if not player.folded:  # Only count bets from non-folded players
                total += player.current_bet
        return total
            
    def handle_showdown(self, pot: int):
        active_players = [p for p in self.players if not p.folded]
        
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"\n{Fore.GREEN}{winner.name} wins {pot} chips!{Style.RESET_ALL}")
            winner.chips += pot
            return
            
        print(f"\n{Fore.GREEN}=== Showdown ==={Style.RESET_ALL}")
        for player in active_players:
            hand_rank = player.get_hand_rank_name(self.community_cards)
            print(f"{player.name}'s hand: {' '.join(str(card) for card in player.hand)} ({hand_rank})")
            
        # Use treys evaluator to find the winner
        winner = min(active_players, 
                    key=lambda p: p._evaluate_hand_strength(self.community_cards))
        
        print(f"\n{Fore.GREEN}{winner.name} wins {pot} chips with {winner.get_hand_rank_name(self.community_cards)}!{Style.RESET_ALL}")
        winner.chips += pot 