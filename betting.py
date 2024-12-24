from typing import List
from colorama import Fore, Style
import time
from player import Player

class BettingRound:
    def __init__(self, players: List[Player], small_blind: int = 10, big_blind: int = 20):
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.pot = 0
        self.current_bet = 0
        self.round_bets = {}  # Track bets for each player in the current round
        
    def post_blinds(self, dealer_pos: int) -> None:
        # Reset round bets
        self.round_bets = {player: 0 for player in self.players}
        
        # Small blind position
        sb_pos = (dealer_pos + 1) % len(self.players)
        bb_pos = (dealer_pos + 2) % len(self.players)
        
        # Post small blind
        sb_player = self.players[sb_pos]
        sb_amount = min(self.small_blind, sb_player.chips)
        sb_player.make_bet(sb_amount)
        self.round_bets[sb_player] = sb_amount
        self.pot += sb_amount
        print(f"\n{sb_player.name} posts small blind: {sb_amount}")
        
        # Post big blind
        bb_player = self.players[bb_pos]
        bb_amount = min(self.big_blind, bb_player.chips)
        bb_player.make_bet(bb_amount)
        self.round_bets[bb_player] = bb_amount
        self.pot += bb_amount
        self.current_bet = bb_amount
        print(f"{bb_player.name} posts big blind: {bb_amount}")
        
    def handle_betting_round(self, round_name: str, start_from: int, community_cards: List = None) -> bool:
        print(f"\n{Fore.YELLOW}=== {round_name.upper()} Betting Round ==={Style.RESET_ALL}")
        
        active_players = [p for p in self.players if not p.folded and p.chips > 0]
        if len(active_players) <= 1:
            return False
            
        # Reset current bets for the new betting round (except pre-flop)
        if round_name != "pre-flop":
            self.current_bet = 0
            self.pot = sum(self.round_bets.values())  # Add previous round bets to pot
            for player in self.players:
                player.current_bet = 0
                self.round_bets[player] = 0
                
        # Keep track of betting
        current_pos = start_from
        last_action_pos = None  # Track position of last action
        betting_started = False  # Track if any bets have been made
        
        while True:
            player = self.players[current_pos]
            
            # Skip players who have folded or are all-in
            if player.folded or player.chips <= 0:
                current_pos = (current_pos + 1) % len(self.players)
                continue
                
            # Store the current bet before the player acts
            previous_bet = self.current_bet
            previous_player_bet = self.round_bets.get(player, 0)
            
            # Handle player action
            if player.is_ai:
                self._handle_ai_turn(player, community_cards)
            else:
                self._handle_player_turn(player, community_cards)
                
            # Update round bets
            current_player_bet = player.current_bet - previous_player_bet
            if current_player_bet > 0:
                self.round_bets[player] = player.current_bet
                
            # If this is a raise, mark this position
            if player.current_bet > previous_bet:
                last_action_pos = current_pos
                betting_started = True
            
            # Move to next position
            current_pos = (current_pos + 1) % len(self.players)
            
            # Check if betting round should end
            if betting_started:
                # If we've gone around to the last action position
                if last_action_pos is not None and current_pos == last_action_pos:
                    # Check if all active players have matched the bet
                    all_matched = True
                    for p in active_players:
                        if not p.folded and p.chips > 0 and p.current_bet < self.current_bet:
                            all_matched = False
                            break
                    if all_matched:
                        break
            else:
                # If no bets have been made and we've gone around the table
                if current_pos == start_from:
                    # Check if everyone has checked or folded
                    all_checked = True
                    for p in active_players:
                        if not p.folded and p.current_bet > 0:
                            all_checked = False
                            break
                    if all_checked:
                        break
                    
        # Calculate final pot for this round
        self.pot = sum(self.round_bets.values())
        return True
        
    def _handle_player_turn(self, player: Player, community_cards: List = None):
        print(f"\n{Fore.GREEN}Your turn! Your hand: {' '.join(str(card) for card in player.hand)}{Style.RESET_ALL}")
        if community_cards:
            print(f"Your hand rank: {player.get_hand_rank_name(community_cards)}")
        print(f"Current bet: {self.current_bet}, Your current bet: {player.current_bet}")
        print(f"To call: {max(0, self.current_bet - player.current_bet)}, Your chips: {player.chips}")
        
        # Get decision from player (either through input or mock)
        if hasattr(player, 'make_decision'):
            action, amount = player.make_decision(
                self.current_bet - player.current_bet,
                self.pot,
                community_cards
            )
        else:
            while True:
                if self.current_bet == player.current_bet:
                    action = input(f"{Fore.YELLOW}What would you like to do? (check/bet/fold): {Style.RESET_ALL}").lower()
                else:
                    action = input(f"{Fore.YELLOW}What would you like to do? (call/raise/fold): {Style.RESET_ALL}").lower()
                
                if action == 'fold':
                    return 'fold', 0
                elif action in ['call', 'check']:
                    return 'call', self.current_bet - player.current_bet
                elif action in ['raise', 'bet']:
                    min_raise = self.current_bet + self.big_blind
                    try:
                        amount = int(input(f"{Fore.YELLOW}How much would you like to raise to? (minimum {min_raise}): {Style.RESET_ALL}"))
                        if amount < min_raise:
                            print(f"Raise amount must be at least {min_raise}!")
                            continue
                        if amount <= self.current_bet:
                            print("Raise amount must be greater than current bet!")
                            continue
                        return 'raise', amount
                    except ValueError:
                        print("Please enter a valid number!")
                        continue
                        
        # Handle the decision
        if action == 'fold':
            player.folded = True
            print(f"{player.name} folds!")
        elif action in ['call', 'check']:
            call_amount = self.current_bet - player.current_bet
            if call_amount > 0:
                bet = player.make_bet(call_amount)
                print(f"{player.name} calls {bet}!")
            else:
                print(f"{player.name} checks!")
        else:  # raise
            min_raise = self.current_bet + self.big_blind
            if amount < min_raise:
                amount = min_raise
            bet = player.make_bet(amount - player.current_bet)
            self.current_bet = amount
            print(f"{player.name} raises to {amount}!")
            
    def _handle_ai_turn(self, player: Player, community_cards: List = None):
        print(f"\n{Fore.BLUE}{player.name}'s turn...{Style.RESET_ALL}")
        time.sleep(1)  # Add some delay to make it feel more natural
        
        action, amount = player.make_decision(
            self.current_bet - player.current_bet,
            self.pot,
            community_cards
        )
        
        # Handle the decision
        if action == 'fold':
            player.folded = True
            print(f"{player.name} folds!")
        elif action in ['call', 'check']:
            call_amount = self.current_bet - player.current_bet
            if call_amount > 0:
                bet = player.make_bet(call_amount)
                print(f"{player.name} calls {bet}!")
            else:
                print(f"{player.name} checks!")
        else:  # raise
            min_raise = self.current_bet + self.big_blind
            if amount < min_raise:
                amount = min_raise
            bet = player.make_bet(amount - player.current_bet)
            self.current_bet = amount
            print(f"{player.name} raises to {amount}!") 