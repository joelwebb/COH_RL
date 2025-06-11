
"""
Unit tests for player_movement module.
"""

import unittest
from unittest.mock import patch, MagicMock
import time
from COH_BOT.player_movement import MovementController


class TestMovementController(unittest.TestCase):
    """Test cases for MovementController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = MovementController()
    
    def test_initialization(self):
        """Test controller initialization."""
        self.assertIsInstance(self.controller.keys, dict)
        self.assertIn('forward', self.controller.keys)
        self.assertIn('backward', self.controller.keys)
        self.assertEqual(self.controller.keys['forward'], 'w')
    
    @patch('COH_BOT.player_movement.pyautogui')
    @patch('COH_BOT.player_movement.time.sleep')
    def test_move_forward(self, mock_sleep, mock_pyautogui):
        """Test forward movement."""
        self.controller.move_forward(2.0)
        
        mock_pyautogui.keyDown.assert_called_with('w')
        mock_pyautogui.keyUp.assert_called_with('w')
        mock_sleep.assert_called_with(2.0)
    
    @patch('COH_BOT.player_movement.pyautogui')
    @patch('COH_BOT.player_movement.time.sleep')
    def test_move_backward(self, mock_sleep, mock_pyautogui):
        """Test backward movement."""
        self.controller.move_backward(1.5)
        
        mock_pyautogui.keyDown.assert_called_with('s')
        mock_pyautogui.keyUp.assert_called_with('s')
        mock_sleep.assert_called_with(1.5)
    
    @patch('COH_BOT.player_movement.pyautogui')
    @patch('COH_BOT.player_movement.time.sleep')
    def test_strafe_left(self, mock_sleep, mock_pyautogui):
        """Test left strafing."""
        self.controller.strafe_left(1.0)
        
        mock_pyautogui.keyDown.assert_called_with('a')
        mock_pyautogui.keyUp.assert_called_with('a')
        mock_sleep.assert_called_with(1.0)
    
    @patch('COH_BOT.player_movement.pyautogui')
    @patch('COH_BOT.player_movement.time.sleep')
    def test_strafe_right(self, mock_sleep, mock_pyautogui):
        """Test right strafing."""
        self.controller.strafe_right(1.0)
        
        mock_pyautogui.keyDown.assert_called_with('d')
        mock_pyautogui.keyUp.assert_called_with('d')
        mock_sleep.assert_called_with(1.0)
    
    @patch('COH_BOT.player_movement.pyautogui')
    @patch('COH_BOT.player_movement.time.sleep')
    def test_turn_left(self, mock_sleep, mock_pyautogui):
        """Test left turning."""
        self.controller.turn_left(90)
        
        mock_pyautogui.keyDown.assert_called_with('q')
        mock_pyautogui.keyUp.assert_called_with('q')
        # 90 degrees should take 0.5 seconds (90/180)
        mock_sleep.assert_called_with(0.5)
    
    @patch('COH_BOT.player_movement.pyautogui')
    @patch('COH_BOT.player_movement.time.sleep')
    def test_turn_right(self, mock_sleep, mock_pyautogui):
        """Test right turning."""
        self.controller.turn_right(180)
        
        mock_pyautogui.keyDown.assert_called_with('e')
        mock_pyautogui.keyUp.assert_called_with('e')
        # 180 degrees should take 1.0 second
        mock_sleep.assert_called_with(1.0)
    
    @patch('COH_BOT.player_movement.pyautogui')
    def test_jump(self, mock_pyautogui):
        """Test jumping."""
        self.controller.jump()
        mock_pyautogui.press.assert_called_with('space')
    
    @patch('COH_BOT.player_movement.pyautogui')
    def test_toggle_sprint(self, mock_pyautogui):
        """Test sprint toggle."""
        self.controller.toggle_sprint()
        mock_pyautogui.press.assert_called_with('r')
    
    @patch('COH_BOT.player_movement.pyautogui')
    def test_toggle_fly(self, mock_pyautogui):
        """Test flight toggle."""
        self.controller.toggle_fly()
        mock_pyautogui.press.assert_called_with('f')
    
    @patch('COH_BOT.player_movement.pyautogui')
    def test_rest(self, mock_pyautogui):
        """Test rest function."""
        self.controller.rest()
        
        # Should call keyUp for all keys
        expected_calls = len(self.controller.keys)
        self.assertEqual(mock_pyautogui.keyUp.call_count, expected_calls)
    
    def test_navigate_to_waypoint_close(self):
        """Test navigation when already close to waypoint."""
        # When within 5 units, should return True
        result = self.controller.navigate_to_waypoint(10, 10, 8, 9)
        self.assertTrue(result)
    
    @patch('COH_BOT.player_movement.MovementController.turn_right')
    @patch('COH_BOT.player_movement.MovementController.move_forward')
    def test_navigate_to_waypoint_far(self, mock_move, mock_turn):
        """Test navigation when far from waypoint."""
        # When far from target, should return False and attempt movement
        result = self.controller.navigate_to_waypoint(100, 100, 0, 0)
        self.assertFalse(result)
        
        # Should have attempted to turn and move
        mock_turn.assert_called()
        mock_move.assert_called()


if __name__ == '__main__':
    unittest.main()
