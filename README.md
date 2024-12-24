# Texas Hold'em Poker Game

A simplified implementation of Texas Hold'em poker where you play against AI opponents. The game features proper hand evaluation, betting rounds, and basic AI decision-making.

## Features

- Play Texas Hold'em poker against 3 AI opponents
- Full implementation of poker hand rankings using the treys library
- Proper betting mechanics including:
  - Small and big blinds
  - Betting rounds (pre-flop, flop, turn, river)
  - Raising, calling, checking, and folding
- Color-coded terminal output for better readability
- Basic AI decision making based on hand strength

## Requirements

- Python 3.7+
- colorama
- treys

## Installation

1. Clone this repository:
```bash
git clone [your-repo-url]
cd texas_holdem_demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the game:
```bash
python main.py
```

## Testing

Run the test suite:
```bash
python -m unittest test_poker_game.py -v
```

## Project Structure

- `main.py` - Entry point and game initialization
- `game.py` - Core game logic and round management
- `betting.py` - Betting round mechanics
- `card.py` - Card and deck implementations
- `player.py` - Player class with AI decision making
- `game_state.py` - Game state tracking

## License

MIT License 