"""
Race Start Performance Predictor for F1 Simulation.

Models how drivers perform at race starts, separate from qualifying pace.
"""

import random
import numpy as np
from typing import List, Dict

class RaceStartPredictor:
    """Predicts first-lap position changes based on driver start performance."""
    
    # Historical start performance ratings (0.0 = terrible, 1.0 = excellent)
    START_PERFORMANCE_RATINGS = {
        # 2026 Grid - based on historical data
        'Charles Leclerc': 0.90,     # Historically excellent starter
        'Lewis Hamilton': 0.85,      # Great starter, especially in key moments  
        'George Russell': 0.75,      # Solid starter
        'Max Verstappen': 0.70,      # Decent but not exceptional
        'Lando Norris': 0.80,        # Good starter
        'Oscar Piastri': 0.65,       # Learning, improving
        'Fernando Alonso': 0.85,     # Veteran excellence
        'Lance Stroll': 0.60,        # Tends to lose positions
        'Kimi Antonelli': 0.70,      # Rookie estimate
        'Isack Hadjar': 0.65,        # Rookie estimate
        # Add more drivers as needed
    }
    
    def __init__(self):
        pass
    
    def simulate_race_start(self, grid_positions: List, track) -> List:
        """
        Simulate race start and first lap position changes.
        
        Args:
            grid_positions: List of drivers in qualifying order
            track: Track object with characteristics
            
        Returns:
            List of drivers in post-start order
        """
        print("🏁 Simulating race start...")
        
        # Calculate start performance for each driver
        start_results = []
        
        for i, driver in enumerate(grid_positions):
            original_position = i + 1
            
            # Get driver's start performance rating
            start_rating = self.START_PERFORMANCE_RATINGS.get(driver.name, 0.75)
            
            # Calculate potential position change
            max_gain = min(3, original_position - 1)  # Can't gain more than 3 or go beyond P1
            max_loss = min(3, len(grid_positions) - original_position)  # Can't lose more than 3
            
            # Performance-based position change
            if start_rating > 0.8:  # Excellent starter
                position_change = random.uniform(-0.5, max_gain * 0.8)
            elif start_rating > 0.7:  # Good starter  
                position_change = random.uniform(-1, max_gain * 0.6)
            else:  # Average/poor starter
                position_change = random.uniform(-max_loss * 0.6, max_gain * 0.4)
            
            # Apply some randomness (race starts are unpredictable)
            randomness = random.uniform(-0.5, 0.5)
            total_change = position_change + randomness
            
            # Calculate new position
            new_position = original_position - total_change  # Negative change = better position
            new_position = max(1, min(len(grid_positions), new_position))
            
            start_results.append({
                'driver': driver,
                'original_pos': original_position,
                'new_pos': new_position,
                'change': total_change
            })
        
        # Sort by new position
        start_results.sort(key=lambda x: x['new_pos'])
        
        # Create new grid order
        new_grid = [result['driver'] for result in start_results]
        
        # Log significant changes
        for result in start_results:
            change = result['original_pos'] - result['new_pos']
            if abs(change) >= 1:
                direction = "gained" if change > 0 else "lost"
                print(f"  📈 {result['driver'].name}: P{result['original_pos']} → P{int(result['new_pos'])} ({direction} {abs(change):.0f})")
        
        return new_grid
    
    def get_start_analysis(self, grid_positions: List) -> Dict:
        """Analyze expected start performance for the grid."""
        analysis = {
            'likely_gainers': [],
            'likely_losers': [],
            'risk_assessment': {}
        }
        
        for i, driver in enumerate(grid_positions[:10]):  # Top 10 only
            position = i + 1
            rating = self.START_PERFORMANCE_RATINGS.get(driver.name, 0.75)
            
            if rating > 0.8 and position > 3:
                analysis['likely_gainers'].append(f"{driver.name} (P{position})")
            elif rating < 0.7 and position <= 6:
                analysis['likely_losers'].append(f"{driver.name} (P{position})")
            
            # Risk assessment
            if rating > 0.85:
                risk = "Strong starter - likely to gain"
            elif rating < 0.65:
                risk = "Weak starter - may lose positions"  
            else:
                risk = "Average start performance"
                
            analysis['risk_assessment'][driver.name] = risk
        
        return analysis

# Integration function for main race simulator
def enhance_race_with_start_simulation(simulator, grid_positions, track):
    """Enhance race simulator with realistic start performance."""
    
    start_predictor = RaceStartPredictor()
    
    # Get start analysis
    analysis = start_predictor.get_start_analysis(grid_positions)
    
    print(f"\n🔍 RACE START ANALYSIS:")
    if analysis['likely_gainers']:
        print(f"📈 Likely to gain positions: {', '.join(analysis['likely_gainers'])}")
    if analysis['likely_losers']:
        print(f"📉 Likely to lose positions: {', '.join(analysis['likely_losers'])}")
    
    # Simulate the start
    post_start_grid = start_predictor.simulate_race_start(grid_positions, track)
    
    # Update simulator with post-start positions
    simulator.grid_positions = post_start_grid
    
    return post_start_grid