
"""
Game State Module

Monitors game state through screenshot analysis using OpenCV.
Extracts player statistics like health, endurance, and experience.
"""

import cv2
import numpy as np
import pyautogui
from PIL import Image
import time


class GameStateMonitor:
    """Monitors game state through screenshot analysis."""
    
    def __init__(self):
        """Initialize the game state monitor."""
        # Define UI element regions (these will need calibration per screen resolution)
        self.ui_regions = {
            'health_bar': (50, 50, 200, 20),      # x, y, width, height
            'endurance_bar': (50, 80, 200, 20),
            'experience_bar': (50, 110, 300, 15),
            'chat_area': (10, 400, 500, 200),
            'target_info': (600, 50, 200, 100)
        }
        
        # Color ranges for different UI elements (HSV format)
        self.color_ranges = {
            'health_red': ((0, 120, 70), (10, 255, 255)),
            'health_green': ((40, 120, 70), (80, 255, 255)),
            'endurance_blue': ((100, 120, 70), (130, 255, 255)),
            'experience_yellow': ((20, 120, 70), (30, 255, 255))
        }
    
    def take_screenshot(self, region=None):
        """Take a screenshot of the game or specific region."""
        if region:
            x, y, width, height = region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        else:
            screenshot = pyautogui.screenshot()
        
        # Convert PIL image to OpenCV format
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return screenshot_cv
    
    def extract_bar_percentage(self, image, color_range, bar_region):
        """Extract percentage from a colored bar (health/endurance/exp)."""
        # Crop to bar region
        x, y, width, height = bar_region
        bar_image = image[y:y+height, x:x+width]
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(bar_image, cv2.COLOR_BGR2HSV)
        
        # Create mask for the specific color
        lower, upper = color_range
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        
        # Calculate percentage based on filled pixels
        total_pixels = width * height
        filled_pixels = cv2.countNonZero(mask)
        
        if total_pixels > 0:
            percentage = (filled_pixels / total_pixels) * 100
            return min(100, max(0, percentage))
        
        return 0
    
    def get_health_percentage(self):
        """Get current health percentage."""
        screenshot = self.take_screenshot()
        
        # Try both red (damaged) and green (healthy) health colors
        health_region = self.ui_regions['health_bar']
        
        green_health = self.extract_bar_percentage(
            screenshot, 
            self.color_ranges['health_green'], 
            health_region
        )
        
        red_health = self.extract_bar_percentage(
            screenshot, 
            self.color_ranges['health_red'], 
            health_region
        )
        
        # Return the higher value (some health bars change color)
        return max(green_health, red_health)
    
    def get_endurance_percentage(self):
        """Get current endurance percentage."""
        screenshot = self.take_screenshot()
        return self.extract_bar_percentage(
            screenshot,
            self.color_ranges['endurance_blue'],
            self.ui_regions['endurance_bar']
        )
    
    def get_experience_percentage(self):
        """Get current experience percentage for current level."""
        screenshot = self.take_screenshot()
        return self.extract_bar_percentage(
            screenshot,
            self.color_ranges['experience_yellow'],
            self.ui_regions['experience_bar']
        )
    
    def get_player_stats(self):
        """Get all player statistics at once."""
        return {
            'health': self.get_health_percentage(),
            'endurance': self.get_endurance_percentage(),
            'experience': self.get_experience_percentage(),
            'timestamp': time.time()
        }
    
    def detect_enemy_target(self):
        """Detect if an enemy is currently targeted."""
        screenshot = self.take_screenshot(self.ui_regions['target_info'])
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Use edge detection to find UI elements
        edges = cv2.Canny(gray, 50, 150)
        
        # If there are enough edges, likely a target is selected
        edge_count = cv2.countNonZero(edges)
        return edge_count > 100  # Threshold may need adjustment
    
    def detect_combat_state(self):
        """Detect if character is in combat."""
        stats = self.get_player_stats()
        
        # Simple heuristic: rapid endurance drain indicates combat
        if hasattr(self, 'last_endurance'):
            endurance_change = self.last_endurance - stats['endurance']
            if endurance_change > 5:  # Significant endurance loss
                return True
        
        self.last_endurance = stats['endurance']
        return False
    
    def wait_for_health_recovery(self, target_percentage=80, timeout=30):
        """Wait for health to recover to target percentage."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            health = self.get_health_percentage()
            if health >= target_percentage:
                return True
            time.sleep(1)
        
        return False  # Timeout reached
    
    def monitor_continuous(self, callback=None, interval=1.0):
        """Continuously monitor game state and call callback with updates."""
        while True:
            stats = self.get_player_stats()
            stats['enemy_targeted'] = self.detect_enemy_target()
            stats['in_combat'] = self.detect_combat_state()
            
            if callback:
                callback(stats)
            
            time.sleep(interval)
    
    def calibrate_ui_regions(self, resolution=(1920, 1080)):
        """Calibrate UI regions for different screen resolutions."""
        # Scale UI regions based on resolution
        scale_x = resolution[0] / 1920
        scale_y = resolution[1] / 1080
        
        calibrated_regions = {}
        for name, (x, y, width, height) in self.ui_regions.items():
            calibrated_regions[name] = (
                int(x * scale_x),
                int(y * scale_y),
                int(width * scale_x),
                int(height * scale_y)
            )
        
        self.ui_regions = calibrated_regions
