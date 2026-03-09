"""
Live Qualifying Result Injector for 2026 F1 Season.

This module allows manual input of actual 2026 qualifying results to improve 
race predictions, especially important for the new regulation era.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class QualifyingResult:
    """Represents actual qualifying results."""
    position: int
    driver_name: str
    team_name: str
    q1_time: Optional[str] = None
    q2_time: Optional[str] = None
    q3_time: Optional[str] = None
    best_time: str = ""
    gap_to_pole: str = ""
    session_type: str = "Q"  # Q, SQ (Sprint Qualifying), etc.
    
class LiveQualifyingInjector:
    """Inject actual 2026 qualifying results for better race predictions."""
    
    def __init__(self, data_dir="qualifying_results"):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), data_dir)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_qualifying_results(self, track_name: str, results: List[QualifyingResult], 
                               race_date: str = None):
        """Save actual qualifying results to file."""
        if not race_date:
            race_date = datetime.now().strftime("%Y-%m-%d")
        
        filename = f"{self._normalize_track_name(track_name)}_{race_date}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # Convert to serializable format
        results_data = {
            "track_name": track_name,
            "race_date": race_date,
            "qualifying_results": [asdict(result) for result in results],
            "updated_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"Saved qualifying results for {track_name} to {filename}")
    
    def load_qualifying_results(self, track_name: str, race_date: str = None) -> Optional[List[QualifyingResult]]:
        """Load actual qualifying results from file."""
        if race_date:
            filename = f"{self._normalize_track_name(track_name)}_{race_date}.json"
        else:
            # Find most recent file for this track
            track_prefix = self._normalize_track_name(track_name)
            matching_files = [f for f in os.listdir(self.data_dir) 
                            if f.startswith(track_prefix) and f.endswith('.json')]
            
            if not matching_files:
                return None
            
            # Get most recent
            filename = sorted(matching_files)[-1]
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            results = []
            for result_data in data['qualifying_results']:
                results.append(QualifyingResult(**result_data))
            
            logger.info(f"Loaded qualifying results for {track_name} from {filename}")
            return results
            
        except FileNotFoundError:
            logger.info(f"No qualifying results found for {track_name}")
            return None
        except Exception as e:
            logger.error(f"Error loading qualifying results: {e}")
            return None
    
    def manual_input_qualifying(self, drivers: List, track_name: str) -> List[QualifyingResult]:
        """Interactive input of qualifying results."""
        print("\n" + "="*70)
        print(f"🏁 MANUAL QUALIFYING RESULTS INPUT - {track_name.upper()}")
        print("="*70)
        print("Enter actual 2026 qualifying results for better race prediction")
        print("Format: Position, Driver Name, Best Time (e.g., '1:18.234')")
        print("Type 'skip' to use simulated qualifying, 'done' when finished")
        print("-"*70)
        
        results = []
        available_drivers = {driver.name.lower(): driver for driver in drivers}
        
        for pos in range(1, len(drivers) + 1):
            while True:
                try:
                    user_input = input(f"P{pos:2d}: ").strip()
                    
                    if user_input.lower() == 'skip':
                        print("⏭️  Skipping manual input, using simulated qualifying")
                        return []
                    
                    if user_input.lower() == 'done' and len(results) >= 10:
                        break
                    
                    # Parse input: "Driver Name, 1:18.234" or "Driver Name 1:18.234"
                    parts = user_input.replace(',', ' ').split()
                    if len(parts) < 2:
                        print("❌ Format: Driver Name, Best Time (e.g., 'Max Verstappen 1:18.234')")
                        continue
                    
                    # Extract time (last part)
                    time_str = parts[-1]
                    if not self._is_valid_lap_time(time_str):
                        print("❌ Invalid time format. Use 'M:SS.SSS' (e.g., '1:18.234')")
                        continue
                    
                    # Extract driver name (all parts except last)
                    driver_name = ' '.join(parts[:-1])
                    
                    # Find matching driver (fuzzy match)
                    matched_driver = self._find_driver_match(driver_name, available_drivers)
                    if not matched_driver:
                        print(f"❌ Driver '{driver_name}' not found. Available drivers:")
                        print(f"   {', '.join([d.name for d in drivers[:8]])}...")
                        continue
                    
                    # Check if driver already entered
                    if any(r.driver_name == matched_driver.name for r in results):
                        print(f"❌ {matched_driver.name} already entered")
                        continue
                    
                    # Create result
                    result = QualifyingResult(
                        position=pos,
                        driver_name=matched_driver.name,
                        team_name=matched_driver.team,
                        best_time=time_str,
                        gap_to_pole=self._calculate_gap_to_pole(time_str, results)
                    )
                    
                    results.append(result)
                    print(f"✅ P{pos}: {matched_driver.name} ({matched_driver.team}) - {time_str}")
                    break
                    
                except KeyboardInterrupt:
                    print("\n⏹️  Input cancelled, using simulated qualifying")
                    return []
                except Exception as e:
                    print(f"❌ Error: {e}. Please try again.")
        
        if results:
            # Sort by position
            results.sort(key=lambda x: x.position)
            
            # Save results
            save_choice = input(f"\n💾 Save results for future use? (y/n): ").lower()
            if save_choice.startswith('y'):
                self.save_qualifying_results(track_name, results)
            
            print(f"\n✅ Entered {len(results)} qualifying results")
            return results
        
        return []
    
    def quick_input_top10(self, drivers: List, track_name: str) -> List[QualifyingResult]:
        """Quick input for just the top 10 (Q3 results)."""
        print(f"\n🏁 QUICK TOP 10 INPUT - {track_name}")
        print("Enter top 10 drivers in order (Q3 results)")
        print("Just type driver names separated by commas")
        print("Example: Verstappen, Norris, Leclerc, Hamilton...")
        
        while True:
            try:
                user_input = input("\nTop 10: ").strip()
                if not user_input or user_input.lower() == 'skip':
                    return []
                
                # Parse driver names
                driver_names = [name.strip() for name in user_input.split(',')]
                if len(driver_names) < 10:
                    print(f"❌ Please enter 10 drivers (got {len(driver_names)})")
                    continue
                
                # Match drivers
                available_drivers = {driver.name.lower(): driver for driver in drivers}
                results = []
                
                for pos, driver_name in enumerate(driver_names[:10], 1):
                    matched_driver = self._find_driver_match(driver_name, available_drivers)
                    if not matched_driver:
                        print(f"❌ Could not find driver: {driver_name}")
                        break
                    
                    # Generate realistic times
                    base_time = 78.0 + pos * 0.2  # Rough times
                    time_str = self._seconds_to_lap_time(base_time)
                    
                    result = QualifyingResult(
                        position=pos,
                        driver_name=matched_driver.name,
                        team_name=matched_driver.team,
                        best_time=time_str
                    )
                    results.append(result)
                
                if len(results) == 10:
                    print("\n✅ Quick Q3 input complete:")
                    for r in results:
                        print(f"P{r.position:2d}: {r.driver_name}")
                    return results
                    
            except KeyboardInterrupt:
                return []
    
    def _normalize_track_name(self, track_name: str) -> str:
        """Normalize track name for filename."""
        return track_name.lower().replace(' ', '_').replace('-', '_')
    
    def _is_valid_lap_time(self, time_str: str) -> bool:
        """Check if time string is valid lap time format."""
        try:
            # Check format: M:SS.SSS or MM:SS.SSS
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            
            minutes = int(parts[0])
            seconds_parts = parts[1].split('.')
            if len(seconds_parts) != 2:
                return False
            
            seconds = int(seconds_parts[0])
            milliseconds = int(seconds_parts[1])
            
            return 0 <= minutes <= 9 and 0 <= seconds <= 59 and 0 <= milliseconds <= 999
        except:
            return False
    
    def _find_driver_match(self, input_name: str, available_drivers: Dict) -> Optional[object]:
        """Find best matching driver from available drivers."""
        input_lower = input_name.lower()
        
        # Exact match first
        if input_lower in available_drivers:
            return available_drivers[input_lower]
        
        # Partial matches
        for driver_name, driver_obj in available_drivers.items():
            # Last name match
            if input_lower in driver_name or driver_name.split()[-1].lower().startswith(input_lower):
                return driver_obj
            # First name match
            if driver_name.split()[0].lower().startswith(input_lower):
                return driver_obj
        
        return None
    
    def _calculate_gap_to_pole(self, time_str: str, existing_results: List[QualifyingResult]) -> str:
        """Calculate gap to pole position."""
        if not existing_results:
            return "POLE"
        
        pole_time = existing_results[0].best_time
        try:
            current_seconds = self._lap_time_to_seconds(time_str)
            pole_seconds = self._lap_time_to_seconds(pole_time)
            gap = current_seconds - pole_seconds
            
            if gap == 0:
                return "POLE"
            else:
                return f"+{gap:.3f}"
        except:
            return ""
    
    def _lap_time_to_seconds(self, time_str: str) -> float:
        """Convert M:SS.SSS to seconds."""
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    
    def _seconds_to_lap_time(self, seconds: float) -> str:
        """Convert seconds to M:SS.SSS format."""
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}:{remaining_seconds:06.3f}"

# Integration with enhanced race model
def inject_qualifying_into_simulation(simulator, track_name: str, drivers: List) -> bool:
    """Inject actual qualifying results into simulator."""
    injector = LiveQualifyingInjector()
    
    # Check for saved results first
    saved_results = injector.load_qualifying_results(track_name)
    if saved_results:
        use_saved = input(f"📁 Found saved qualifying results for {track_name}. Use them? (y/n): ")
        if use_saved.lower().startswith('y'):
            qualifying_results = saved_results
        else:
            qualifying_results = None
    else:
        qualifying_results = None
    
    # If no saved results, offer manual input
    if not qualifying_results:
        print(f"\n🏁 {track_name} Qualifying Results")
        print("1. Enter full qualifying results (all 22 drivers)")
        print("2. Enter top 10 only (Q3 results)")
        print("3. Skip and use simulation")
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == "1":
            qualifying_results = injector.manual_input_qualifying(drivers, track_name)
        elif choice == "2":
            qualifying_results = injector.quick_input_top10(drivers, track_name)
        else:
            return False
    
    # Apply results to simulator
    if qualifying_results:
        # Convert to driver objects in correct order
        driver_map = {d.name: d for d in drivers}
        grid_order = []
        
        for result in sorted(qualifying_results, key=lambda x: x.position):
            if result.driver_name in driver_map:
                grid_order.append(driver_map[result.driver_name])
        
        # Add remaining drivers not in qualifying results
        remaining_drivers = [d for d in drivers if d not in grid_order]
        grid_order.extend(remaining_drivers)
        
        # Set grid positions in simulator
        simulator.grid_positions = grid_order[:len(drivers)]
        
        print(f"✅ Applied actual qualifying results to {track_name} simulation")
        print(f"📊 Grid: P1-{grid_order[0].name}, P2-{grid_order[1].name}, P3-{grid_order[2].name}")
        return True
    
    return False