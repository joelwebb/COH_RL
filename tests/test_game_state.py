
"""
Unit tests for game_state module.
"""

import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
from COH_BOT.game_state import GameStateMonitor


class TestGameStateMonitor(unittest.TestCase):
    """Test cases for GameStateMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = GameStateMonitor()
    
    def test_initialization(self):
        """Test monitor initialization."""
        self.assertIsInstance(self.monitor.ui_regions, dict)
        self.assertIsInstance(self.monitor.color_ranges, dict)
        self.assertIn('health_bar', self.monitor.ui_regions)
        self.assertIn('health_red', self.monitor.color_ranges)
    
    @patch('COH_BOT.game_state.pyautogui.screenshot')
    @patch('COH_BOT.game_state.cv2.cvtColor')
    def test_take_screenshot(self, mock_cvtColor, mock_screenshot):
        """Test screenshot capture."""
        # Mock PIL image
        mock_pil_image = MagicMock()
        mock_screenshot.return_value = mock_pil_image
        
        # Mock numpy array conversion
        mock_array = np.zeros((100, 100, 3), dtype=np.uint8)
        with patch('COH_BOT.game_state.np.array', return_value=mock_array):
            result = self.monitor.take_screenshot()
        
        mock_screenshot.assert_called_once()
        mock_cvtColor.assert_called_once()
    
    @patch('COH_BOT.game_state.pyautogui.screenshot')
    def test_take_screenshot_with_region(self, mock_screenshot):
        """Test screenshot capture with specific region."""
        region = (10, 10, 100, 100)
        
        with patch('COH_BOT.game_state.cv2.cvtColor'):
            with patch('COH_BOT.game_state.np.array'):
                self.monitor.take_screenshot(region)
        
        mock_screenshot.assert_called_with(region=(10, 10, 100, 100))
    
    def test_extract_bar_percentage_full(self):
        """Test percentage extraction from full bar."""
        # Create a test image with full green bar
        test_image = np.zeros((50, 200, 3), dtype=np.uint8)
        test_image[10:30, 50:250] = [0, 255, 0]  # Green bar region
        
        color_range = ((40, 120, 70), (80, 255, 255))  # Green range
        bar_region = (50, 10, 200, 20)
        
        percentage = self.monitor.extract_bar_percentage(
            test_image, color_range, bar_region
        )
        
        # Should detect a high percentage (not exactly 100 due to HSV conversion)
        self.assertGreater(percentage, 80)
    
    def test_extract_bar_percentage_empty(self):
        """Test percentage extraction from empty bar."""
        # Create a test image with no colored pixels
        test_image = np.zeros((50, 200, 3), dtype=np.uint8)
        
        color_range = ((40, 120, 70), (80, 255, 255))  # Green range
        bar_region = (50, 10, 200, 20)
        
        percentage = self.monitor.extract_bar_percentage(
            test_image, color_range, bar_region
        )
        
        # Should detect 0% or very low percentage
        self.assertLess(percentage, 10)
    
    @patch('COH_BOT.game_state.GameStateMonitor.take_screenshot')
    @patch('COH_BOT.game_state.GameStateMonitor.extract_bar_percentage')
    def test_get_health_percentage(self, mock_extract, mock_screenshot):
        """Test health percentage retrieval."""
        mock_extract.side_effect = [75, 0]  # Green health: 75%, Red health: 0%
        
        health = self.monitor.get_health_percentage()
        
        self.assertEqual(health, 75)
        self.assertEqual(mock_extract.call_count, 2)  # Called for both colors
    
    @patch('COH_BOT.game_state.GameStateMonitor.take_screenshot')
    @patch('COH_BOT.game_state.GameStateMonitor.extract_bar_percentage')
    def test_get_endurance_percentage(self, mock_extract, mock_screenshot):
        """Test endurance percentage retrieval."""
        mock_extract.return_value = 85
        
        endurance = self.monitor.get_endurance_percentage()
        
        self.assertEqual(endurance, 85)
        mock_extract.assert_called_once()
    
    @patch('COH_BOT.game_state.GameStateMonitor.take_screenshot')
    @patch('COH_BOT.game_state.GameStateMonitor.extract_bar_percentage')
    def test_get_experience_percentage(self, mock_extract, mock_screenshot):
        """Test experience percentage retrieval."""
        mock_extract.return_value = 45
        
        experience = self.monitor.get_experience_percentage()
        
        self.assertEqual(experience, 45)
        mock_extract.assert_called_once()
    
    @patch('COH_BOT.game_state.GameStateMonitor.get_health_percentage')
    @patch('COH_BOT.game_state.GameStateMonitor.get_endurance_percentage')
    @patch('COH_BOT.game_state.GameStateMonitor.get_experience_percentage')
    def test_get_player_stats(self, mock_exp, mock_end, mock_health):
        """Test comprehensive player stats retrieval."""
        mock_health.return_value = 90
        mock_end.return_value = 70
        mock_exp.return_value = 60
        
        stats = self.monitor.get_player_stats()
        
        self.assertEqual(stats['health'], 90)
        self.assertEqual(stats['endurance'], 70)
        self.assertEqual(stats['experience'], 60)
        self.assertIn('timestamp', stats)
    
    @patch('COH_BOT.game_state.GameStateMonitor.take_screenshot')
    @patch('COH_BOT.game_state.cv2.Canny')
    @patch('COH_BOT.game_state.cv2.countNonZero')
    def test_detect_enemy_target_present(self, mock_count, mock_canny, mock_screenshot):
        """Test enemy target detection when target is present."""
        mock_count.return_value = 150  # Above threshold
        
        result = self.monitor.detect_enemy_target()
        
        self.assertTrue(result)
    
    @patch('COH_BOT.game_state.GameStateMonitor.take_screenshot')
    @patch('COH_BOT.game_state.cv2.Canny')
    @patch('COH_BOT.game_state.cv2.countNonZero')
    def test_detect_enemy_target_absent(self, mock_count, mock_canny, mock_screenshot):
        """Test enemy target detection when no target is present."""
        mock_count.return_value = 50  # Below threshold
        
        result = self.monitor.detect_enemy_target()
        
        self.assertFalse(result)
    
    @patch('COH_BOT.game_state.GameStateMonitor.get_player_stats')
    def test_detect_combat_state_in_combat(self, mock_stats):
        """Test combat detection when in combat."""
        # First call: endurance at 80%
        mock_stats.return_value = {'endurance': 80}
        self.monitor.detect_combat_state()  # Initialize last_endurance
        
        # Second call: endurance dropped to 70% (10% drop indicates combat)
        mock_stats.return_value = {'endurance': 70}
        result = self.monitor.detect_combat_state()
        
        self.assertTrue(result)
    
    @patch('COH_BOT.game_state.GameStateMonitor.get_player_stats')
    def test_detect_combat_state_not_in_combat(self, mock_stats):
        """Test combat detection when not in combat."""
        # Stable endurance indicates no combat
        mock_stats.return_value = {'endurance': 80}
        self.monitor.detect_combat_state()  # Initialize
        
        mock_stats.return_value = {'endurance': 79}  # Minor change
        result = self.monitor.detect_combat_state()
        
        self.assertFalse(result)
    
    @patch('COH_BOT.game_state.GameStateMonitor.get_health_percentage')
    @patch('COH_BOT.game_state.time.sleep')
    def test_wait_for_health_recovery_success(self, mock_sleep, mock_health):
        """Test waiting for health recovery when successful."""
        mock_health.side_effect = [70, 75, 85]  # Health increases over time
        
        result = self.monitor.wait_for_health_recovery(80, timeout=5)
        
        self.assertTrue(result)
    
    @patch('COH_BOT.game_state.GameStateMonitor.get_health_percentage')
    @patch('COH_BOT.game_state.time.sleep')
    @patch('COH_BOT.game_state.time.time')
    def test_wait_for_health_recovery_timeout(self, mock_time, mock_sleep, mock_health):
        """Test waiting for health recovery when timeout occurs."""
        # Simulate timeout by making time.time() return increasing values
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6]  # Exceeds 5-second timeout
        mock_health.return_value = 70  # Health stays low
        
        result = self.monitor.wait_for_health_recovery(80, timeout=5)
        
        self.assertFalse(result)
    
    def test_calibrate_ui_regions(self):
        """Test UI region calibration for different resolutions."""
        original_health_region = self.monitor.ui_regions['health_bar']
        
        # Test scaling for 1280x720 (2/3 scale)
        self.monitor.calibrate_ui_regions((1280, 720))
        
        new_health_region = self.monitor.ui_regions['health_bar']
        
        # Values should be scaled down
        self.assertLess(new_health_region[0], original_health_region[0])
        self.assertLess(new_health_region[1], original_health_region[1])


if __name__ == '__main__':
    unittest.main()
