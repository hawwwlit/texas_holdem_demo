from game import TexasHoldem

def main():
    print("Welcome to Simple Texas Hold'em!")
    print("You'll be playing against AI opponents.")
    print("Each player starts with 1000 chips.")
    
    # Create and start the game
    game = TexasHoldem(num_ai_players=3)
    game.play_game()
    
    print("\nThanks for playing!")

if __name__ == "__main__":
    main() 