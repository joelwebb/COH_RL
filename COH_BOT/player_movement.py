
"""
Player Movement Module

Handles character movement and navigation in City of Heroes using pyautogui.
Provides high-level movement functions for automated gameplay.
"""

import pyautogui
import time
import math


class MovementController:
    """Controls player character movement using keyboard inputs."""
    
    def __init__(self):
        """Initialize the movement controller with default settings."""
        # Disable pyautogui failsafe for smoother operation
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Default key mappings for City of Heroes
        self.keys = {
            'forward': 'w',
            'backward': 's',
            'strafe_left': 'a',
            'strafe_right': 'd',
            'turn_left': 'q',
            'turn_right': 'e',
            'jump': 'space',
            'sprint': 'r',
            'fly': 'f'
        }
    
    def move_forward(self, duration=1.0):
        """Move character forward for specified duration."""
        pyautogui.keyDown(self.keys['forward'])
        time.sleep(duration)
        pyautogui.keyUp(self.keys['forward'])
    
    def move_backward(self, duration=1.0):
        """Move character backward for specified duration."""
        pyautogui.keyDown(self.keys['backward'])
        time.sleep(duration)
        pyautogui.keyUp(self.keys['backward'])
    
    def strafe_left(self, duration=1.0):
        """Strafe left for specified duration."""
        pyautogui.keyDown(self.keys['strafe_left'])
        time.sleep(duration)
        pyautogui.keyUp(self.keys['strafe_left'])
    
    def strafe_right(self, duration=1.0):
        """Strafe right for specified duration."""
        pyautogui.keyDown(self.keys['strafe_right'])
        time.sleep(duration)
        pyautogui.keyUp(self.keys['strafe_right'])
    
    def turn_left(self, angle=45):
        """Turn character left by specified angle (approximate)."""
        # Rough calculation: 1 second of turning ≈ 180 degrees
        duration = angle / 180.0
        pyautogui.keyDown(self.keys['turn_left'])
        time.sleep(duration)
        pyautogui.keyUp(self.keys['turn_left'])
    
    def turn_right(self, angle=45):
        """Turn character right by specified angle (approximate)."""
        duration = angle / 180.0
        pyautogui.keyDown(self.keys['turn_right'])
        time.sleep(duration)
        pyautogui.keyUp(self.keys['turn_right'])
    
    def jump(self):
        """Make character jump."""
        pyautogui.press(self.keys['jump'])
    
    def toggle_sprint(self):
        """Toggle sprint mode on/off."""
        pyautogui.press(self.keys['sprint'])
    
    def toggle_fly(self):
        """Toggle flight mode on/off (if available)."""
        pyautogui.press(self.keys['fly'])
    
    def circle_strafe_target(self, radius=10, duration=5.0, clockwise=True):
        """Circle strafe around a target."""
        steps = int(duration * 10)  # 10 steps per second
        step_duration = duration / steps
        turn_angle = 360 / steps
        
        for _ in range(steps):
            # Move forward slightly
            self.move_forward(step_duration * 0.3)
            
            # Strafe in circle
            if clockwise:
                self.strafe_right(step_duration * 0.4)
                self.turn_right(turn_angle)
            else:
                self.strafe_left(step_duration * 0.4)
                self.turn_left(turn_angle)
            
            time.sleep(step_duration * 0.3)
    
    def kite_enemy(self, distance=15):
        """Perform kiting maneuver - move away while maintaining distance."""
        # Move backward while occasionally turning to maintain target
        self.move_backward(2.0)
        self.turn_left(15)
        self.move_backward(1.0)
        self.turn_right(30)
        self.move_backward(1.0)
        self.turn_left(15)
    
    def retreat(self):
        """Emergency retreat sequence."""
        self.move_backward(3.0)
        self.turn_left(180)  # Turn around
        self.move_forward(5.0)  # Run away
    
    def rest(self):
        """Stop all movement to allow endurance recovery."""
        # Release all movement keys
        for key in self.keys.values():
            pyautogui.keyUp(key)
        time.sleep(0.5)
    
    def navigate_to_waypoint(self, x, y, current_x, current_y):
        """Navigate to a specific coordinate (basic pathfinding)."""
        # Calculate direction to target
        dx = x - current_x
        dy = y - current_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 5:  # Close enough
            return True
        
        # Calculate angle to target
        angle = math.atan2(dy, dx) * 180 / math.pi
        
        # Turn towards target (simplified)
        if angle > 10:
            self.turn_right(min(angle, 45))
        elif angle < -10:
            self.turn_left(min(abs(angle), 45))
        
        # Move forward
        move_time = min(distance / 20, 2.0)  # Adjust speed based on distance
        self.move_forward(move_time)
        
        return False  # Not yet at destination
