
"""
LLM Integrations Module

Integrates AWS Nova LLM for making intelligent gameplay decisions
based on current game state analysis.
"""

import json
import boto3
import base64
import time
import os
from typing import Dict, Any, Optional
from .game_state import GameStateMonitor


class NovaGameplayAI:
    """AWS Nova integration for City of Heroes gameplay decisions."""
    
    def __init__(self):
        """Initialize Nova client and game state monitor."""
        self.bedrock_client = boto3.client(
            'bedrock-runtime', 
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        self.model_id = os.getenv('NOVA_MODEL_ID', 'amazon.nova-micro-v1:0')
        self.game_monitor = GameStateMonitor()
        
        # Decision prompts for different game scenarios
        self.decision_prompts = {
            "combat": """
            Analyze this City of Heroes game state and decide the best combat action:
            
            Game State: {game_state}
            
            Available Actions:
            - attack: Use basic attack combo
            - power_combo: Use high-damage combo (costs more endurance)
            - aoe_combo: Use area attack for multiple enemies
            - retreat: Move away from danger
            - rest: Recover endurance
            - move_forward: Advance toward enemies
            - circle_strafe: Tactical positioning
            
            Respond with ONLY a JSON object: {{"action": "action_name", "reason": "brief explanation"}}
            """,
            
            "exploration": """
            Analyze this City of Heroes exploration state and decide movement:
            
            Game State: {game_state}
            
            Available Actions:
            - move_forward: Continue exploring forward
            - turn_left: Turn and explore left
            - turn_right: Turn and explore right
            - patrol: Execute patrol pattern
            - rest: Recover health/endurance
            - search_enemies: Look for targets
            
            Respond with ONLY a JSON object: {{"action": "action_name", "reason": "brief explanation"}}
            """,
            
            "recovery": """
            Character needs recovery in City of Heroes:
            
            Game State: {game_state}
            
            Available Actions:
            - rest: Stay and recover
            - retreat: Move to safer location
            - find_cover: Seek protection
            - wait: Wait for natural recovery
            
            Respond with ONLY a JSON object: {{"action": "action_name", "reason": "brief explanation"}}
            """
        }
    
    def call_nova_with_image(self, prompt: str, image_data: Optional[str] = None) -> Dict[str, Any]:
        """Call Nova with text prompt and optional screenshot."""
        try:
            # Prepare message content
            content = [{"text": prompt}]
            
            # Add image if provided
            if image_data:
                content.append({
                    "image": {
                        "format": "png",
                        "source": {"bytes": image_data}
                    }
                })
            
            body = {
                "messages": [
                    {"role": "user", "content": content}
                ],
                "inferenceConfig": {
                    "max_new_tokens": 256,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "top_k": 50
                }
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(body)
            )
            
            response_text = json.loads(response['body'].read())["output"]["message"]["content"][0]["text"]
            
            # Try to parse as JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return {"action": "rest", "reason": "Failed to parse AI response"}
                
        except Exception as e:
            print(f"Nova API error: {e}")
            return {"action": "rest", "reason": f"API error: {str(e)}"}
    
    def analyze_game_state(self, stats: Dict[str, Any]) -> str:
        """Determine current game scenario based on stats."""
        health = stats.get('health', 100)
        endurance = stats.get('endurance', 100)
        in_combat = stats.get('in_combat', False)
        enemy_targeted = stats.get('enemy_targeted', False)
        
        # Determine scenario
        if health < 30 or endurance < 20:
            return "recovery"
        elif in_combat or enemy_targeted:
            return "combat"
        else:
            return "exploration"
    
    def get_screenshot_data(self) -> str:
        """Get base64 encoded screenshot for Nova analysis."""
        try:
            # Take screenshot and convert to base64
            screenshot = self.game_monitor.take_screenshot()
            import cv2
            _, buffer = cv2.imencode('.png', screenshot)
            return base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None
    
    def make_gameplay_decision(self) -> Dict[str, Any]:
        """Make an AI-driven gameplay decision based on current state."""
        # Get current game state
        stats = self.game_monitor.get_player_stats()
        stats['in_combat'] = self.game_monitor.detect_combat_state()
        stats['enemy_targeted'] = self.game_monitor.detect_enemy_target()
        
        # Determine scenario and get appropriate prompt
        scenario = self.analyze_game_state(stats)
        prompt_template = self.decision_prompts[scenario]
        prompt = prompt_template.format(game_state=json.dumps(stats, indent=2))
        
        # Get screenshot for visual context
        screenshot_data = self.get_screenshot_data()
        
        # Get AI decision
        decision = self.call_nova_with_image(prompt, screenshot_data)
        
        # Add metadata
        decision['scenario'] = scenario
        decision['game_state'] = stats
        decision['timestamp'] = time.time()
        
        return decision
    
    def execute_decision(self, decision: Dict[str, Any]) -> bool:
        """Execute the AI's decision using game controllers."""
        action = decision.get('action', 'rest')
        
        try:
            from . import player_movement, player_attacks
            
            movement = player_movement.MovementController()
            attacks = player_attacks.AttackController()
            
            # Execute based on action type
            if action == 'attack':
                attacks.execute_attack_chain('basic_combo')
            elif action == 'power_combo':
                attacks.execute_attack_chain('power_combo')
            elif action == 'aoe_combo':
                attacks.execute_attack_chain('aoe_combo')
            elif action == 'retreat':
                movement.move_backward(2.0)
            elif action == 'rest':
                time.sleep(3.0)  # Rest for 3 seconds
            elif action == 'move_forward':
                movement.move_forward(1.5)
            elif action == 'circle_strafe':
                movement.circle_strafe_target(radius=8, duration=2.0)
            elif action == 'turn_left':
                movement.turn_left(45)
            elif action == 'turn_right':
                movement.turn_right(45)
            elif action == 'patrol':
                movement.patrol_area()
            elif action == 'search_enemies':
                attacks.target_nearest_enemy()
            elif action == 'find_cover':
                movement.move_backward(3.0)
            elif action == 'wait':
                time.sleep(2.0)
            else:
                print(f"Unknown action: {action}")
                return False
                
            return True
            
        except Exception as e:
            print(f"Action execution error: {e}")
            return False
