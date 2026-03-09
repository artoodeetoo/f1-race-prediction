"""
Advanced Pit Strategy Predictor for F1 Race Simulation.

Models 1-stop vs 2-stop strategies, team preferences, and strategy execution quality.
This addresses the Ferrari strategy issue from the Australian GP 2026.
"""

import random
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class StrategyType(Enum):
    ONE_STOP = "1-stop"
    TWO_STOP = "2-stop"
    THREE_STOP = "3-stop"  # Rare, usually for recovery

@dataclass
class PitStrategy:
    """Represents a pit strategy for a driver."""
    strategy_type: StrategyType
    pit_laps: List[int]  # When to pit
    tire_compounds: List[str]  # Tire compounds for each stint
    expected_finish_position: int
    risk_level: float  # 0.0 = safe, 1.0 = risky
    description: str

class AdvancedStrategyPredictor:
    """Predicts and models pit strategies for race simulation."""
    
    # Team strategy execution ratings (0.0 = terrible, 1.0 = perfect)
    TEAM_STRATEGY_RATINGS = {
        'Red Bull Racing': 0.95,      # Excellent strategy team
        'Mercedes': 0.85,             # Generally good, some mistakes
        'Ferrari': 0.60,              # Historically poor strategic decisions
        'McLaren': 0.80,              # Improved strategy recently
        'Aston Martin': 0.75,         # Decent strategy
        'Alpine': 0.70,               # Average strategy
        'Williams': 0.65,             # Limited resources affect strategy
        'Haas': 0.60,                 # Often poor strategic calls
        'Racing Bulls': 0.75,         # Decent, learning from Red Bull
        'Audi': 0.70,                 # New team, unknown but competent
        'Cadillac': 0.65              # New team, likely conservative
    }
    
    # Team risk preferences (0.0 = very conservative, 1.0 = very aggressive)
    TEAM_RISK_PREFERENCES = {
        'Red Bull Racing': 0.8,       # Aggressive when ahead
        'Mercedes': 0.7,              # Calculated risks
        'Ferrari': 0.9,               # Often too aggressive/risky
        'McLaren': 0.6,               # More conservative lately
        'Aston Martin': 0.5,          # Conservative approach
        'Alpine': 0.7,                # Medium risk
        'Williams': 0.4,              # Very conservative (limited resources)
        'Haas': 0.8,                  # High risk (nothing to lose)
        'Racing Bulls': 0.6,          # Moderate risk
        'Audi': 0.5,                  # New team, conservative
        'Cadillac': 0.4               # New team, very conservative
    }
    
    def __init__(self):
        pass
    
    def determine_optimal_strategies(self, grid_positions: List, track, weather, tire_compounds: List[str] = None) -> Dict[str, PitStrategy]:
        """Determine optimal pit strategies for all drivers."""
        
        if tire_compounds is None:
            tire_compounds = ['SOFT', 'MEDIUM', 'HARD']
        
        strategies = {}
        
        print("🔧 Analyzing pit strategy options...")
        
        # Analyze track characteristics for strategy
        track_analysis = self._analyze_track_for_strategy(track)
        
        # Weather impact on strategy
        weather_factor = self._get_weather_strategy_impact(weather)
        
        for i, driver in enumerate(grid_positions):
            grid_position = i + 1
            team_name = driver.team
            
            # Calculate multiple strategy options
            strategy_options = []
            
            # Option 1: One-stop strategy
            one_stop = self._calculate_one_stop_strategy(driver, team_name, grid_position, track, weather_factor)
            if one_stop:
                strategy_options.append(one_stop)
            
            # Option 2: Two-stop strategy  
            two_stop = self._calculate_two_stop_strategy(driver, team_name, grid_position, track, weather_factor)
            if two_stop:
                strategy_options.append(two_stop)
            
            # Option 3: Alternative strategy (if starting poorly)
            if grid_position > 10:
                alt_strategy = self._calculate_alternative_strategy(driver, team_name, grid_position, track, weather_factor)
                if alt_strategy:
                    strategy_options.append(alt_strategy)
            
            # Choose best strategy based on team preferences and execution ability
            chosen_strategy = self._choose_team_strategy(team_name, strategy_options, grid_position)
            strategies[driver.name] = chosen_strategy
        
        return strategies
    
    def _analyze_track_for_strategy(self, track) -> Dict:
        """Analyze track characteristics that affect strategy."""
        analysis = {
            'tire_degradation_rate': track.tyre_wear / 10.0,  # Normalize to 0-1
            'overtaking_difficulty': track.overtaking_difficulty / 10.0,
            'pit_time_loss': 22.0 + (track.length_km - 5.0) * 0.5,  # Estimated pit time loss
            'drs_zones': max(1, track.straight_count - 1),  # Assume DRS zones on straights
            'track_position_importance': track.overtaking_difficulty / 10.0  # Higher = more important
        }
        
        return analysis
    
    def _get_weather_strategy_impact(self, weather) -> float:
        """Calculate how weather affects strategy choices."""
        if weather.condition == 'wet':
            return 1.3  # Weather makes strategy more important
        elif weather.condition == 'mixed':
            return 1.2  # Unpredictable conditions
        else:
            return 1.0  # Normal conditions
    
    def _calculate_one_stop_strategy(self, driver, team_name: str, grid_pos: int, track, weather_factor: float) -> Optional[PitStrategy]:
        """Calculate one-stop strategy option."""
        
        race_laps = track.laps
        
        # Optimal pit window for one-stop (usually middle third of race)
        optimal_pit_lap = int(race_laps * 0.6)  # Around 60% through race
        
        # Adjust pit window based on track characteristics
        tire_deg = track.tyre_wear
        if tire_deg > 7:  # High degradation
            optimal_pit_lap -= 5  # Pit earlier
        elif tire_deg < 4:  # Low degradation  
            optimal_pit_lap += 3  # Pit later
        
        # Choose tire compounds
        if grid_pos <= 10:  # Q3 participants start on qualifying tires
            start_compound = 'SOFT'
            pit_compound = 'HARD'
        else:
            start_compound = 'MEDIUM'
            pit_compound = 'HARD'
        
        # Estimate finishing position for one-stop
        base_finish = grid_pos
        
        # One-stop advantages: fewer pit stops, track position
        if track.overtaking_difficulty > 7:  # Hard to overtake
            base_finish -= 1  # Track position advantage
        
        # One-stop disadvantages: tire degradation in final stint
        if tire_deg > 6:  # High degradation track
            base_finish += 1  # Slower in final stint
        
        expected_finish = max(1, min(22, base_finish))
        
        return PitStrategy(
            strategy_type=StrategyType.ONE_STOP,
            pit_laps=[optimal_pit_lap],
            tire_compounds=[start_compound, pit_compound],
            expected_finish_position=expected_finish,
            risk_level=0.3,  # Generally safer
            description=f"One-stop: {start_compound}→{pit_compound} (pit lap {optimal_pit_lap})"
        )
    
    def _calculate_two_stop_strategy(self, driver, team_name: str, grid_pos: int, track, weather_factor: float) -> Optional[PitStrategy]:
        """Calculate two-stop strategy option."""
        
        race_laps = track.laps
        
        # Two pit windows
        first_pit = int(race_laps * 0.25)   # Around 25% through
        second_pit = int(race_laps * 0.65)  # Around 65% through
        
        # Adjust for track characteristics
        tire_deg = track.tyre_wear
        if tire_deg > 7:  # High degradation
            first_pit -= 2
            second_pit -= 2
        
        # Tire compound strategy
        start_compound = 'SOFT'
        middle_compound = 'MEDIUM'
        final_compound = 'MEDIUM'
        
        # Two-stop is better on high degradation tracks
        base_finish = grid_pos
        
        # Two-stop advantages: fresher tires, more aggressive
        if tire_deg > 6:  # High degradation
            base_finish -= 2  # Fresh tire advantage
        
        # Two-stop disadvantages: more pit stops, track position loss
        if track.overtaking_difficulty > 7:  # Hard to overtake
            base_finish += 2  # Lost track position
        else:
            base_finish -= 1  # Can overtake with fresh tires
        
        expected_finish = max(1, min(22, base_finish))
        
        return PitStrategy(
            strategy_type=StrategyType.TWO_STOP,
            pit_laps=[first_pit, second_pit],
            tire_compounds=[start_compound, middle_compound, final_compound],
            expected_finish_position=expected_finish,
            risk_level=0.6,  # More aggressive
            description=f"Two-stop: {start_compound}→{middle_compound}→{final_compound} (laps {first_pit}, {second_pit})"
        )
    
    def _calculate_alternative_strategy(self, driver, team_name: str, grid_pos: int, track, weather_factor: float) -> Optional[PitStrategy]:
        """Calculate alternative strategy for drivers starting poorly."""
        
        race_laps = track.laps
        
        # Alternative: Start on HARD, try to go long
        pit_lap = int(race_laps * 0.75)  # Very late pit
        
        return PitStrategy(
            strategy_type=StrategyType.ONE_STOP,
            pit_laps=[pit_lap],
            tire_compounds=['HARD', 'SOFT'],
            expected_finish_position=max(1, grid_pos - 3),  # Hope to gain positions
            risk_level=0.8,  # High risk, high reward
            description=f"Alternative: HARD→SOFT long stint (pit lap {pit_lap})"
        )
    
    def _choose_team_strategy(self, team_name: str, strategy_options: List[PitStrategy], grid_pos: int) -> PitStrategy:
        """Choose strategy based on team preferences and execution ability."""
        
        if not strategy_options:
            # Fallback strategy
            return PitStrategy(
                strategy_type=StrategyType.ONE_STOP,
                pit_laps=[35],
                tire_compounds=['MEDIUM', 'HARD'],
                expected_finish_position=grid_pos,
                risk_level=0.5,
                description="Default one-stop strategy"
            )
        
        # Get team characteristics
        strategy_rating = self.TEAM_STRATEGY_RATINGS.get(team_name, 0.7)
        risk_preference = self.TEAM_RISK_PREFERENCES.get(team_name, 0.5)
        
        # Teams with poor strategy execution might choose wrong strategy
        if strategy_rating < 0.7:  # Poor strategy teams
            if random.random() < 0.3:  # 30% chance of poor decision
                # Choose a suboptimal strategy
                worst_option = max(strategy_options, key=lambda s: s.expected_finish_position)
                worst_option.description += " (POOR STRATEGY CHOICE)"
                return worst_option
        
        # Choose based on risk preference and expected outcome
        scored_strategies = []
        for strategy in strategy_options:
            # Score based on expected finish position (lower is better)
            position_score = 25 - strategy.expected_finish_position  # Invert (higher = better)
            
            # Adjust for team risk preference
            risk_adjustment = 0
            if strategy.risk_level > 0.7 and risk_preference < 0.5:  # Conservative team, risky strategy
                risk_adjustment = -5  # Penalty for risky strategy
            elif strategy.risk_level < 0.4 and risk_preference > 0.7:  # Aggressive team, safe strategy
                risk_adjustment = -3  # Penalty for conservative strategy
            
            total_score = position_score + risk_adjustment
            scored_strategies.append((strategy, total_score))
        
        # Choose best scoring strategy
        best_strategy = max(scored_strategies, key=lambda x: x[1])[0]
        
        # Apply strategy execution quality
        execution_modifier = random.uniform(0.8, 1.2) * strategy_rating
        if execution_modifier < 0.9:  # Poor execution
            best_strategy.expected_finish_position += 1
            best_strategy.description += " (POOR EXECUTION)"
        elif execution_modifier > 1.1:  # Excellent execution
            best_strategy.expected_finish_position = max(1, best_strategy.expected_finish_position - 1)
            best_strategy.description += " (EXCELLENT EXECUTION)"
        
        return best_strategy
    
    def get_strategy_summary(self, strategies: Dict[str, PitStrategy]) -> Dict:
        """Get summary of strategies being used."""
        summary = {
            'one_stop_count': 0,
            'two_stop_count': 0,
            'alternative_count': 0,
            'strategy_distribution': {},
            'risky_strategies': [],
            'conservative_strategies': []
        }
        
        for driver_name, strategy in strategies.items():
            if strategy.strategy_type == StrategyType.ONE_STOP:
                summary['one_stop_count'] += 1
            elif strategy.strategy_type == StrategyType.TWO_STOP:
                summary['two_stop_count'] += 1
            else:
                summary['alternative_count'] += 1
            
            # Track risky vs conservative
            if strategy.risk_level > 0.7:
                summary['risky_strategies'].append(driver_name)
            elif strategy.risk_level < 0.4:
                summary['conservative_strategies'].append(driver_name)
        
        return summary

# Interactive strategy override system
class StrategyOverride:
    """Allow user to override team strategies."""
    
    def __init__(self, strategies: Dict[str, PitStrategy]):
        self.strategies = strategies
    
    def interactive_strategy_override(self) -> Dict[str, PitStrategy]:
        """Interactive menu to override team strategies."""
        
        print(f"\n🔧 STRATEGY OVERRIDE OPTIONS")
        print(f"=" * 50)
        print(f"Current strategy distribution:")
        
        summary = AdvancedStrategyPredictor().get_strategy_summary(self.strategies)
        print(f"• One-stop strategies: {summary['one_stop_count']}")
        print(f"• Two-stop strategies: {summary['two_stop_count']}")
        
        if summary['risky_strategies']:
            print(f"• Risky strategies: {', '.join(summary['risky_strategies'][:3])}")
        
        print(f"\nOverride options:")
        print(f"1. Force specific team to 1-stop")
        print(f"2. Force specific team to 2-stop")
        print(f"3. Make Ferrari use poor strategy (realistic!)")
        print(f"4. Make all teams conservative")
        print(f"5. Keep current strategies")
        
        choice = input(f"\nSelect option (1-5): ").strip()
        
        if choice == "1":
            return self._force_team_strategy(StrategyType.ONE_STOP)
        elif choice == "2":
            return self._force_team_strategy(StrategyType.TWO_STOP)
        elif choice == "3":
            return self._make_ferrari_strategy_poor()
        elif choice == "4":
            return self._make_all_conservative()
        else:
            return self.strategies
    
    def _force_team_strategy(self, strategy_type: StrategyType) -> Dict[str, PitStrategy]:
        """Force a specific team to use a particular strategy."""
        team_name = input("Enter team name (e.g., Ferrari, Mercedes): ").strip()
        
        count = 0
        for driver_name, strategy in self.strategies.items():
            # Find drivers from this team (simplified matching)
            if team_name.lower() in strategy.description.lower():
                # Modify strategy
                if strategy_type == StrategyType.ONE_STOP:
                    strategy.strategy_type = StrategyType.ONE_STOP
                    strategy.pit_laps = [35]
                    strategy.description = f"FORCED 1-stop: {team_name}"
                else:
                    strategy.strategy_type = StrategyType.TWO_STOP
                    strategy.pit_laps = [20, 40]
                    strategy.description = f"FORCED 2-stop: {team_name}"
                count += 1
        
        print(f"✅ Modified {count} driver strategies for {team_name}")
        return self.strategies
    
    def _make_ferrari_strategy_poor(self) -> Dict[str, PitStrategy]:
        """Make Ferrari use historically poor strategy."""
        count = 0
        for driver_name, strategy in self.strategies.items():
            if 'ferrari' in driver_name.lower() or 'leclerc' in driver_name.lower() or 'hamilton' in driver_name.lower():
                # Make strategy worse
                strategy.expected_finish_position += 2
                strategy.risk_level = 0.9
                strategy.description += " (FERRARI STRATEGY BLUNDER)"
                count += 1
        
        print(f"✅ Applied poor Ferrari strategy to {count} drivers")
        return self.strategies
    
    def _make_all_conservative(self) -> Dict[str, PitStrategy]:
        """Make all teams use conservative strategies."""
        for strategy in self.strategies.values():
            strategy.strategy_type = StrategyType.ONE_STOP
            strategy.risk_level = 0.2
            strategy.description = "Conservative one-stop"
        
        print("✅ All teams now using conservative strategies")
        return self.strategies


# Integration function for main simulator
def enhance_race_with_advanced_strategy(simulator, grid_positions, track, weather, allow_overrides=True):
    """Enhance race with advanced pit strategy modeling."""
    
    predictor = AdvancedStrategyPredictor()
    
    # Determine strategies for all drivers
    strategies = predictor.determine_optimal_strategies(grid_positions, track, weather)
    
    # Show strategy summary
    summary = predictor.get_strategy_summary(strategies)
    print(f"\n🔧 PIT STRATEGY ANALYSIS:")
    print(f"📊 {summary['one_stop_count']} drivers on 1-stop, {summary['two_stop_count']} on 2-stop")
    
    if summary['risky_strategies']:
        print(f"⚠️  Risky strategies: {', '.join(summary['risky_strategies'][:5])}")
    
    # Optional: Allow user to override strategies
    if allow_overrides:
        override_strategies = input(f"\n🔧 Override pit strategies? (y/n): ").lower().startswith('y')
        if override_strategies:
            override_system = StrategyOverride(strategies)
            strategies = override_system.interactive_strategy_override()
    
    # Apply strategies to simulator
    simulator.pit_strategies = strategies
    
    return strategies