
"""
Unit tests for player_attacks module.
"""

import unittest
from unittest.mock import patch, MagicMock
import time
from COH_BOT.player_attacks import AttackController


class TestAttackController(unittest.TestCase):
    """Test cases for AttackController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = AttackController()
    
    def test_initialization(self):
        """Test controller initialization."""
        self.assertIsInstance(self.controller.hotkeys, dict)
        self.assertIsInstance(self.controller.attack_chains, dict)
        self.assertIn('basic_combo', self.controller.attack_chains)
        self.assertEqual(self.controller.hotkeys[1], '1')
    
    @patch('COH_BOT.player_attacks.pyautogui')
    @patch('COH_BOT.player_attacks.time.sleep')
    def test_use_ability(self, mock_sleep, mock_pyautogui):
        """Test single ability use."""
        self.controller.use_ability(1, wait_for_animation=True)
        
        mock_pyautogui.press.assert_called_with('1')
        mock_sleep.assert_called_with(1.2)  # Default timing for ability 1
    
    @patch('COH_BOT.player_attacks.pyautogui')
    @patch('COH_BOT.player_attacks.time.sleep')
    def test_use_ability_no_wait(self, mock_sleep, mock_pyautogui):
        """Test ability use without waiting for animation."""
        self.controller.use_ability(2, wait_for_animation=False)
        
        mock_pyautogui.press.assert_called_with('2')
        # Should not call sleep for animation
        mock_sleep.assert_not_called()
    
    def test_use_ability_invalid_number(self):
        """Test using invalid ability number."""
        with self.assertRaises(ValueError):
            self.controller.use_ability(10)
    
    @patch('COH_BOT.player_attacks.AttackController.use_ability')
    @patch('COH_BOT.player_attacks.time.sleep')
    def test_execute_attack_chain(self, mock_sleep, mock_use_ability):
        """Test executing a predefined attack chain."""
        self.controller.execute_attack_chain('basic_combo')
        
        # Should call use_ability for each ability in basic_combo
        expected_calls = len(self.controller.attack_chains['basic_combo'])
        self.assertEqual(mock_use_ability.call_count, expected_calls)
    
    def test_execute_unknown_chain(self):
        """Test executing unknown attack chain."""
        with self.assertRaises(ValueError):
            self.controller.execute_attack_chain('unknown_chain')
    
    @patch('COH_BOT.player_attacks.AttackController.use_ability')
    @patch('COH_BOT.player_attacks.time.sleep')
    def test_custom_attack_sequence(self, mock_sleep, mock_use_ability):
        """Test custom attack sequence."""
        sequence = [(1, 1.0), (3, 2.0), (5, 1.5)]
        self.controller.custom_attack_sequence(sequence)
        
        self.assertEqual(mock_use_ability.call_count, 3)
        # Check sleep was called with correct timing
        mock_sleep.assert_any_call(1.0)
        mock_sleep.assert_any_call(2.0)
        mock_sleep.assert_any_call(1.5)
    
    @patch('COH_BOT.player_attacks.AttackController.use_ability')
    @patch('COH_BOT.player_attacks.time.sleep')
    def test_rapid_fire_attack(self, mock_sleep, mock_use_ability):
        """Test rapid fire attack."""
        self.controller.rapid_fire_attack(1, count=3, interval=0.5)
        
        self.assertEqual(mock_use_ability.call_count, 3)
        # Should sleep 0.5 seconds between each attack
        self.assertEqual(mock_sleep.call_count, 3)
    
    @patch('COH_BOT.player_attacks.AttackController.use_ability')
    def test_rotation_attack(self, mock_use_ability):
        """Test rotation attack."""
        abilities = [1, 2, 3]
        self.controller.rotation_attack(abilities, cycles=2)
        
        # Should call use_ability 6 times (3 abilities × 2 cycles)
        self.assertEqual(mock_use_ability.call_count, 6)
    
    @patch('COH_BOT.player_attacks.pyautogui')
    def test_interrupt_current_attack(self, mock_pyautogui):
        """Test attack interruption."""
        self.controller.interrupt_current_attack()
        
        mock_pyautogui.press.assert_called_with('esc')
    
    def test_add_custom_chain(self):
        """Test adding custom attack chain."""
        custom_chain = [(1, 1.0), (2, 1.5)]
        self.controller.add_custom_chain('test_chain', custom_chain)
        
        self.assertIn('test_chain', self.controller.attack_chains)
        self.assertEqual(self.controller.attack_chains['test_chain'], custom_chain)
    
    def test_modify_ability_timing(self):
        """Test modifying ability timing."""
        self.controller.modify_ability_timing(1, 2.0)
        
        self.assertEqual(self.controller.ability_timings[1], 2.0)
    
    def test_get_available_chains(self):
        """Test getting available chain names."""
        chains = self.controller.get_available_chains()
        
        self.assertIsInstance(chains, list)
        self.assertIn('basic_combo', chains)
        self.assertIn('power_combo', chains)
    
    @patch('COH_BOT.player_attacks.AttackController.execute_attack_chain')
    def test_burst_combo(self, mock_execute):
        """Test burst combo shortcut."""
        self.controller.burst_combo()
        
        mock_execute.assert_called_with('power_combo')
    
    @patch('COH_BOT.player_attacks.AttackController.execute_attack_chain')
    def test_aoe_clear(self, mock_execute):
        """Test AoE clear shortcut."""
        self.controller.aoe_clear()
        
        mock_execute.assert_called_with('aoe_combo')
    
    @patch('COH_BOT.player_attacks.pyautogui')
    @patch('COH_BOT.player_attacks.AttackController.execute_attack_chain')
    def test_target_and_attack(self, mock_execute, mock_pyautogui):
        """Test targeting and attacking."""
        self.controller.target_and_attack()
        
        mock_pyautogui.press.assert_called_with('tab')
        mock_execute.assert_called_with('basic_combo')
    
    @patch('COH_BOT.player_attacks.AttackController.execute_attack_chain')
    def test_smart_attack_selection_single(self, mock_execute):
        """Test smart attack selection for single enemy."""
        self.controller.smart_attack_selection(enemy_count=1)
        
        mock_execute.assert_called_with('basic_combo')
    
    @patch('COH_BOT.player_attacks.AttackController.execute_attack_chain')
    def test_smart_attack_selection_multiple(self, mock_execute):
        """Test smart attack selection for multiple enemies."""
        self.controller.smart_attack_selection(enemy_count=5)
        
        mock_execute.assert_called_with('aoe_combo')


if __name__ == '__main__':
    unittest.main()
