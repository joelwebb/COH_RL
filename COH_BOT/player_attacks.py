
"""
Player Attacks Module

Handles combat abilities and attack chains in City of Heroes using hotkeys.
Provides configurable attack sequences with timing controls.
"""

import pyautogui
import time
from typing import Dict, List, Tuple, Optional


class AttackController:
    """Controls player combat abilities using hotkey inputs."""
    
    def __init__(self):
        """Initialize the attack controller with default settings."""
        # Disable pyautogui failsafe for smoother operation
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05
        
        # Default hotkey mappings (1-9 number keys)
        self.hotkeys = {
            1: '1',
            2: '2', 
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            9: '9'
        }
        
        # Default attack chains with timings (ability_key, wait_time)
        self.attack_chains = {
            'basic_combo': [(1, 1.2), (2, 1.5), (3, 2.0)],
            'power_combo': [(4, 2.0), (5, 2.5), (6, 3.0)],
            'aoe_combo': [(7, 2.5), (8, 3.0), (9, 1.0)],
            'quick_strike': [(1, 0.8), (2, 0.8)],
            'heavy_attack': [(6, 3.5)],
            'defensive': [(5, 2.0), (3, 1.5)],
            'ranged_combo': [(2, 1.0), (4, 1.5), (7, 2.0)],
            'melee_combo': [(1, 1.2), (3, 1.8), (5, 2.2)]
        }
        
        # Animation and activation times for different ability types
        self.ability_timings = {
            1: 1.2,  # Quick attack
            2: 1.0,  # Fast ability
            3: 1.8,  # Medium ability
            4: 1.5,  # Ranged attack
            5: 2.2,  # Heavy ability
            6: 3.5,  # Very heavy/slow ability
            7: 2.5,  # AoE ability
            8: 3.0,  # Large AoE
            9: 1.0   # Utility/buff
        }
    
    def use_ability(self, ability_number: int, wait_for_animation: bool = True):
        """Use a single ability by hotkey number."""
        if ability_number not in self.hotkeys:
            raise ValueError(f"Invalid ability number: {ability_number}")
        
        key = self.hotkeys[ability_number]
        pyautogui.press(key)
        
        if wait_for_animation:
            wait_time = self.ability_timings.get(ability_number, 1.5)
            time.sleep(wait_time)
    
    def execute_attack_chain(self, chain_name: str, interrupt_on_low_health: bool = False):
        """Execute a predefined attack chain."""
        if chain_name not in self.attack_chains:
            raise ValueError(f"Unknown attack chain: {chain_name}")
        
        chain = self.attack_chains[chain_name]
        
        for ability_key, wait_time in chain:
            # Optional: Check health before continuing (requires game_state module)
            if interrupt_on_low_health:
                try:
                    from .game_state import GameStateMonitor
                    monitor = GameStateMonitor()
                    if monitor.get_health_percentage() < 20:
                        print("Low health detected, interrupting attack chain")
                        break
                except ImportError:
                    pass  # Continue if game_state module not available
            
            self.use_ability(ability_key, wait_for_animation=False)
            time.sleep(wait_time)
    
    def custom_attack_sequence(self, sequence: List[Tuple[int, float]]):
        """Execute a custom attack sequence."""
        for ability_key, wait_time in sequence:
            self.use_ability(ability_key, wait_for_animation=False)
            time.sleep(wait_time)
    
    def rapid_fire_attack(self, ability_number: int, count: int = 3, interval: float = 0.5):
        """Rapidly use the same ability multiple times."""
        for _ in range(count):
            self.use_ability(ability_number, wait_for_animation=False)
            time.sleep(interval)
    
    def rotation_attack(self, abilities: List[int], cycles: int = 1):
        """Cycle through abilities in rotation."""
        for cycle in range(cycles):
            for ability in abilities:
                self.use_ability(ability)
    
    def conditional_attack(self, primary_ability: int, backup_ability: int, 
                          condition_check: callable = None):
        """Use primary ability, fall back to backup if condition fails."""
        try:
            if condition_check and not condition_check():
                self.use_ability(backup_ability)
            else:
                self.use_ability(primary_ability)
        except Exception:
            # If anything goes wrong, use backup
            self.use_ability(backup_ability)
    
    def interrupt_current_attack(self):
        """Interrupt current attack animation (ESC key)."""
        pyautogui.press('esc')
        time.sleep(0.2)
    
    def add_custom_chain(self, name: str, chain: List[Tuple[int, float]]):
        """Add a new custom attack chain."""
        self.attack_chains[name] = chain
    
    def modify_ability_timing(self, ability_number: int, new_timing: float):
        """Modify the timing for a specific ability."""
        self.ability_timings[ability_number] = new_timing
    
    def get_available_chains(self) -> List[str]:
        """Get list of available attack chain names."""
        return list(self.attack_chains.keys())
    
    def burst_combo(self):
        """Execute highest damage combo quickly."""
        self.execute_attack_chain('power_combo')
    
    def aoe_clear(self):
        """Execute AoE combo for multiple enemies."""
        self.execute_attack_chain('aoe_combo')
    
    def safe_attack(self):
        """Execute basic combo with health monitoring."""
        self.execute_attack_chain('basic_combo', interrupt_on_low_health=True)
    
    def emergency_attack(self):
        """Quick emergency attack sequence."""
        self.execute_attack_chain('quick_strike')
    
    def buff_rotation(self):
        """Use utility/buff abilities."""
        # Use abilities 9, 8 (typically buffs/utilities)
        self.use_ability(9)
        time.sleep(1.0)
        self.use_ability(8)
    
    def target_and_attack(self, target_key: str = 'tab', attack_chain: str = 'basic_combo'):
        """Target nearest enemy and execute attack chain."""
        pyautogui.press(target_key)  # Target nearest enemy
        time.sleep(0.3)
        self.execute_attack_chain(attack_chain)
    
    def continuous_attack_mode(self, chain_name: str = 'basic_combo', 
                              duration: float = 30.0, pause_between: float = 0.5):
        """Continuously execute attack chains for specified duration."""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            self.execute_attack_chain(chain_name)
            time.sleep(pause_between)
            
            # Optional break on low health
            try:
                from .game_state import GameStateMonitor
                monitor = GameStateMonitor()
                if monitor.get_health_percentage() < 15:
                    print("Critical health, stopping continuous attacks")
                    break
            except ImportError:
                pass
    
    def smart_attack_selection(self, enemy_count: int = 1):
        """Select appropriate attack based on enemy count."""
        if enemy_count == 1:
            self.execute_attack_chain('basic_combo')
        elif enemy_count <= 3:
            self.execute_attack_chain('ranged_combo')
        else:
            self.execute_attack_chain('aoe_combo')
