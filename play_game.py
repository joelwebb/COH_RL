
"""
City of Heroes AI Gameplay Script

Main script that uses AWS Nova to make intelligent gameplay decisions
based on real-time game state analysis.
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from COH_BOT.llm_integrations import NovaGameplayAI
from COH_BOT.game_state import GameStateMonitor
from COH_BOT import player_movement, player_attacks

# Load environment variables
load_dotenv()

class GameplayLogger:
    """Logs all gameplay decisions and actions."""
    
    def __init__(self):
        """Initialize logger with logs directory."""
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Create session log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.logs_dir / f"gameplay_session_{timestamp}.json"
        self.action_history = []
    
    def log_decision(self, decision: dict, execution_success: bool):
        """Log an AI decision and its execution result."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "execution_success": execution_success,
            "session_action_count": len(self.action_history) + 1
        }
        
        self.action_history.append(log_entry)
        
        # Write to file
        with open(self.session_file, 'w') as f:
            json.dump(self.action_history, f, indent=2)
        
        # Print summary
        action = decision.get('action', 'unknown')
        reason = decision.get('reason', 'no reason provided')
        status = "✓" if execution_success else "✗"
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {status} Action: {action} - {reason}")
    
    def get_recent_actions(self, count: int = 5) -> list:
        """Get the most recent actions for context."""
        return self.action_history[-count:] if self.action_history else []


class COHGameplayBot:
    """Main bot class for automated City of Heroes gameplay."""
    
    def __init__(self):
        """Initialize the gameplay bot."""
        self.ai = NovaGameplayAI()
        self.monitor = GameStateMonitor()
        self.logger = GameplayLogger()
        self.decision_interval = int(os.getenv('DECISION_INTERVAL', 5))
        self.running = False
        
        print("🦸 City of Heroes AI Bot Initialized")
        print(f"⏱️  Decision interval: {self.decision_interval} seconds")
        print(f"📁 Logs directory: {self.logger.logs_dir}")
    
    def validate_environment(self) -> bool:
        """Validate AWS credentials and environment setup."""
        required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            print("Please check your .env file and AWS credentials.")
            return False
        
        print("✅ Environment validation passed")
        return True
    
    def display_game_state(self, stats: dict):
        """Display current game state in a readable format."""
        health = stats.get('health', 0)
        endurance = stats.get('endurance', 0)
        experience = stats.get('experience', 0)
        in_combat = stats.get('in_combat', False)
        enemy_targeted = stats.get('enemy_targeted', False)
        
        # Create health/endurance bars
        health_bar = "█" * (health // 10) + "░" * (10 - health // 10)
        endurance_bar = "█" * (endurance // 10) + "░" * (10 - endurance // 10)
        
        combat_status = "⚔️ COMBAT" if in_combat else "🌍 EXPLORE"
        target_status = "🎯 TARGETED" if enemy_targeted else "👁️ SCANNING"
        
        print(f"\n📊 Game State:")
        print(f"   Health: {health:3.0f}% [{health_bar}]")
        print(f"   Endurance: {endurance:3.0f}% [{endurance_bar}]")
        print(f"   Experience: {experience:3.0f}%")
        print(f"   Status: {combat_status} | {target_status}")
    
    def run_gameplay_loop(self):
        """Main gameplay loop with AI decision making."""
        self.running = True
        action_count = 0
        
        print("\n🚀 Starting AI gameplay loop...")
        print("Press Ctrl+C to stop the bot\n")
        
        try:
            while self.running:
                action_count += 1
                print(f"\n{'='*50}")
                print(f"🤖 AI Decision Cycle #{action_count}")
                print(f"{'='*50}")
                
                # Get current game state
                stats = self.monitor.get_player_stats()
                stats['in_combat'] = self.monitor.detect_combat_state()
                stats['enemy_targeted'] = self.monitor.detect_enemy_target()
                
                # Display current state
                self.display_game_state(stats)
                
                # Get AI decision
                print("\n🧠 Consulting AI for next action...")
                decision = self.ai.make_gameplay_decision()
                
                # Execute decision
                print(f"🎮 Executing: {decision.get('action', 'unknown')}")
                execution_success = self.ai.execute_decision(decision)
                
                # Log the decision
                self.logger.log_decision(decision, execution_success)
                
                # Show recent action history
                recent_actions = self.logger.get_recent_actions(3)
                if recent_actions:
                    print(f"\n📋 Recent Actions:")
                    for i, entry in enumerate(recent_actions[-3:], 1):
                        action = entry['decision'].get('action', 'unknown')
                        status = "✓" if entry['execution_success'] else "✗"
                        print(f"   {i}. {status} {action}")
                
                # Wait before next decision
                print(f"\n⏳ Waiting {self.decision_interval} seconds before next decision...")
                time.sleep(self.decision_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping gameplay bot...")
            self.running = False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            self.running = False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup and save final logs."""
        print("📁 Saving final logs...")
        total_actions = len(self.logger.action_history)
        print(f"✅ Session completed: {total_actions} total actions logged")
        print(f"📋 Log file: {self.logger.session_file}")


def main():
    """Main entry point for the COH gameplay bot."""
    print("🦸‍♂️ City of Heroes AI Gameplay Bot")
    print("=" * 40)
    
    # Create bot instance
    bot = COHGameplayBot()
    
    # Validate environment
    if not bot.validate_environment():
        return
    
    # Start gameplay loop
    bot.run_gameplay_loop()


if __name__ == "__main__":
    main()
