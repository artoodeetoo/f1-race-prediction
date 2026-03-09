"""
Enhanced Qualifying Predictor for F1 Race Simulation.

This module uses real qualifying data patterns to improve grid position predictions.
"""

import logging
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class QualifyingForm:
    """Represents a driver's recent qualifying form."""
    driver_name: str
    recent_grid_positions: List[int]  # Last 5 races
    avg_grid_position: float
    q3_appearances: int  # How often they reach Q3
    pole_positions: int
    front_row_starts: int
    qualifying_improvement_trend: float  # Positive = improving

class EnhancedQualifyingPredictor:
    """Enhanced qualifying predictor using form and real data patterns."""
    
    def __init__(self, real_data_enhancer=None):
        self.real_data_enhancer = real_data_enhancer
        self._qualifying_form_cache = {}
        
    def calculate_qualifying_form(self, driver_name: str) -> QualifyingForm:
        """Calculate driver's recent qualifying form from real data."""
        if driver_name in self._qualifying_form_cache:
            return self._qualifying_form_cache[driver_name]
            
        if not self.real_data_enhancer:
            # Default form for simulation
            return QualifyingForm(
                driver_name=driver_name,
                recent_grid_positions=[10, 9, 11, 8, 12],
                avg_grid_position=10.0,
                q3_appearances=3,
                pole_positions=0,
                front_row_starts=1,
                qualifying_improvement_trend=0.0
            )
        
        try:
            # Get real qualifying data from enhancer
            driver_abbrev = self.real_data_enhancer._get_driver_abbreviation(driver_name)
            driver_data = self.real_data_enhancer.get_enhanced_driver_data()
            
            if driver_abbrev in driver_data:
                real_data = driver_data[driver_abbrev]
                grid_positions = real_data.get('grid_positions', [10])
                
                # Calculate form metrics
                recent_positions = grid_positions[-5:] if len(grid_positions) >= 5 else grid_positions
                avg_position = np.mean(recent_positions)
                
                # Calculate improvement trend (recent vs older performance)
                if len(grid_positions) >= 6:
                    recent_avg = np.mean(grid_positions[-3:])
                    older_avg = np.mean(grid_positions[-6:-3])
                    improvement_trend = older_avg - recent_avg  # Positive = improving (lower positions)
                else:
                    improvement_trend = 0.0
                
                # Count Q3 appearances (top 10 grid positions)
                q3_count = len([pos for pos in recent_positions if pos <= 10])
                poles = len([pos for pos in recent_positions if pos == 1])
                front_rows = len([pos for pos in recent_positions if pos <= 2])
                
                form = QualifyingForm(
                    driver_name=driver_name,
                    recent_grid_positions=recent_positions,
                    avg_grid_position=avg_position,
                    q3_appearances=q3_count,
                    pole_positions=poles,
                    front_row_starts=front_rows,
                    qualifying_improvement_trend=improvement_trend
                )
                
                self._qualifying_form_cache[driver_name] = form
                return form
                
        except Exception as e:
            logger.warning(f"Could not calculate qualifying form for {driver_name}: {e}")
        
        # Fallback default form
        return QualifyingForm(
            driver_name=driver_name,
            recent_grid_positions=[10],
            avg_grid_position=10.0,
            q3_appearances=1,
            pole_positions=0,
            front_row_starts=0,
            qualifying_improvement_trend=0.0
        )
    
    def predict_qualifying_position(self, driver, team, track, weather) -> Tuple[float, int]:
        """
        Predict qualifying position using form, car performance, and track factors.
        
        Returns:
            Tuple of (predicted_lap_time, predicted_grid_position)
        """
        # Get driver's qualifying form
        form = self.calculate_qualifying_form(driver.name)
        
        # Base qualifying performance (1-22 scale)
        base_position = form.avg_grid_position
        
        # Adjust for recent form trend
        form_adjustment = form.qualifying_improvement_trend * 0.5  # Max ±0.5 positions
        
        # Car performance factor (stronger effect in qualifying)
        car_rating = team.get_car_rating() if hasattr(team, 'get_car_rating') else team.performance
        car_factor = (car_rating - 85) / 10  # Normalize around P85 team
        car_adjustment = -car_factor * 2  # Better car = better position (negative)
        
        # Track-specific adjustment
        track_adjustment = self._calculate_track_specific_adjustment(driver, team, track)
        
        # Weather adjustment
        weather_adjustment = self._calculate_weather_adjustment(driver, weather)
        
        # Q3 experience bonus
        q3_experience_bonus = -0.2 if form.q3_appearances >= 4 else 0.1
        
        # Calculate predicted position
        predicted_position = (base_position + form_adjustment + car_adjustment + 
                            track_adjustment + weather_adjustment + q3_experience_bonus)
        
        # Clamp to valid grid positions
        predicted_position = max(1, min(22, predicted_position))
        
        # Convert to lap time for sorting
        base_lap_time = 90.0 + (track.length_km - 5) * 4.5  # Rough base time
        time_per_position = 0.3  # ~0.3s per grid position
        predicted_lap_time = base_lap_time + (predicted_position - 1) * time_per_position
        
        # Add realistic variance
        variance = 0.2 * (1 - (driver.consistency / 100))
        predicted_lap_time += np.random.normal(0, variance)
        
        return predicted_lap_time, int(round(predicted_position))
    
    def _calculate_track_specific_adjustment(self, driver, team, track) -> float:
        """Calculate track-specific qualifying adjustment."""
        adjustment = 0.0
        
        # Monaco/Street circuit specialists
        if track.overtaking_difficulty >= 8:  # Street circuits
            if driver.skill_overtaking <= 75:  # Patient drivers do better in qualifying here
                adjustment -= 0.3
        
        # High-speed circuits (Monza, Spa)
        if track.top_speed >= 340:
            if team.power >= 90:  # Strong power unit
                adjustment -= 0.4
        
        # High downforce circuits
        if track.downforce_level >= 8:
            if team.aerodynamics >= 90:
                adjustment -= 0.3
        
        return adjustment
    
    def _calculate_weather_adjustment(self, driver, weather) -> float:
        """Calculate weather-specific qualifying adjustment."""
        if weather.condition == 'wet':
            wet_skill = driver.skill_wet / 100
            # Rain specialists gain positions, others lose them
            return (wet_skill - 0.8) * 3  # Max ±0.6 positions
        elif weather.condition == 'mixed':
            adaptability = (driver.skill_wet + driver.skill_dry) / 200
            return (adaptability - 0.8) * 2  # Max ±0.4 positions
        
        return 0.0
    
    def get_form_summary(self, drivers: List) -> Dict:
        """Get qualifying form summary for all drivers."""
        summary = {
            'form_leaders': [],  # Drivers on upward trend
            'pole_contenders': [], # Drivers likely for pole
            'q3_certainties': [], # Drivers likely to reach Q3
            'struggling_drivers': []  # Drivers on downward trend
        }
        
        for driver in drivers:
            form = self.calculate_qualifying_form(driver.name)
            
            if form.qualifying_improvement_trend > 0.5:
                summary['form_leaders'].append(driver.name)
            
            if form.avg_grid_position <= 3:
                summary['pole_contenders'].append(driver.name)
            
            if form.q3_appearances >= 4:
                summary['q3_certainties'].append(driver.name)
            
            if form.qualifying_improvement_trend < -0.5:
                summary['struggling_drivers'].append(driver.name)
        
        return summary