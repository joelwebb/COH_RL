
# COH_RL - City of Heroes Bot Development

![City of Heroes](https://i.ytimg.com/vi/QAbetA5BUEI/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLBolyQEmrYb_n5A53rNNFk0TOyqWw)

Bots to fight crime! Reinforcement learning approaches to playing COH in a semi-open world using computer vision and automated input control.

## Overview

This project provides tools for automating City of Heroes gameplay using Python libraries like `pyautogui` for player control and `opencv` for real-time game state analysis through screenshots.

## Features

- **Player Movement Control**: Automated character movement and navigation using pyautogui
- **Real-time Game State Monitoring**: Extract health, endurance, and experience data from screenshots using OpenCV
- **Modular Design**: Clean, importable Python package structure for easy integration

## Installation

The required dependencies will be automatically installed when you run the code:
- `pyautogui` - For simulating keyboard and mouse inputs
- `opencv-python` - For image processing and game state analysis
- `numpy` - For numerical operations with image data
- `pillow` - For image handling and manipulation

## Quick Start

```python
from COH_BOT import player_movement, game_state

# Initialize movement controller
movement = player_movement.MovementController()

# Move character forward for 2 seconds
movement.move_forward(duration=2.0)

# Turn left 90 degrees
movement.turn_left(angle=90)

# Initialize game state monitor
monitor = game_state.GameStateMonitor()

# Get current player stats
stats = monitor.get_player_stats()
print(f"Health: {stats['health']}%")
print(f"Endurance: {stats['endurance']}%")
print(f"Experience: {stats['experience']}%")
```

## Package Structure

```
COH_BOT/
├── __init__.py
├── player_movement.py    # Character movement and navigation
├── game_state.py        # Screenshot analysis and stat monitoring
└── player_attacks.py    # Combat abilities and attack chains

tests/
├── __init__.py
├── test_player_movement.py
├── test_game_state.py
└── test_player_attacks.py
```

## Safety Considerations

- Always test automation in safe environments
- Be mindful of game terms of service
- Use reasonable delays between actions to avoid detection
- Implement fail-safes for unexpected game states

## Usage Examples

### Movement Control
```python
# Basic movement patterns
movement.move_forward(2.0)
movement.move_backward(1.0)
movement.strafe_left(1.5)
movement.strafe_right(1.5)

# Combat positioning
movement.circle_strafe_target(radius=10, duration=5.0)
movement.kite_enemy(distance=15)
```

### Attack System
```python
from COH_BOT import player_attacks

# Initialize attack controller
attacks = player_attacks.AttackController()

# Use individual abilities (hotkeys 1-9)
attacks.use_ability(1)  # Use ability on hotkey 1
attacks.use_ability(5)  # Use ability on hotkey 5

# Execute predefined attack chains
attacks.execute_attack_chain('basic_combo')    # Basic 3-hit combo
attacks.execute_attack_chain('power_combo')    # High damage combo
attacks.execute_attack_chain('aoe_combo')      # Area of effect attacks

# Quick access methods
attacks.burst_combo()      # Highest damage combo
attacks.aoe_clear()        # Clear multiple enemies
attacks.emergency_attack() # Quick emergency sequence

# Custom attack sequences
custom_sequence = [(1, 1.2), (3, 1.8), (6, 3.0)]  # (ability, wait_time)
attacks.custom_attack_sequence(custom_sequence)
```

### Game State Monitoring
```python
# Monitor player vitals
while True:
    stats = monitor.get_player_stats()
    if stats['health'] < 30:
        movement.retreat()
    if stats['endurance'] < 20:
        movement.rest()
```

### Combat Integration
```python
# Complete combat loop
from COH_BOT import player_movement, game_state, player_attacks

movement = player_movement.MovementController()
monitor = game_state.GameStateMonitor()
attacks = player_attacks.AttackController()

# Combat sequence
while True:
    stats = monitor.get_player_stats()
    
    if stats['health'] < 20:
        movement.retreat()
        break
    elif stats['endurance'] < 30:
        movement.rest()
    else:
        # Target and attack enemies
        attacks.target_and_attack('tab', 'basic_combo')
        
        # Use AoE if multiple enemies detected
        if monitor.detect_enemy_target():
            attacks.smart_attack_selection(enemy_count=3)
```

## Development

Run tests with:
```bash
python -m pytest tests/
```

## Contributing

1. Add new features to the appropriate module
2. Write comprehensive tests
3. Update documentation
4. Follow PEP 8 style guidelines

## Disclaimer

This project is for educational purposes. Please respect game terms of service and use responsibly.
