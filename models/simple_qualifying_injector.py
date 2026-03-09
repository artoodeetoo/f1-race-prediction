"""
Simple Qualifying Injector for 2026 F1 Race Simulation.

This is a clean, working version of the qualifying injection system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from typing import List, Optional
from data.drivers import get_all_drivers

class SimpleQualifyingInjector:
    """Simple, reliable qualifying injection system."""
    
    def __init__(self):
        self.drivers = get_all_drivers()
        self.driver_map = {d.name.lower(): d for d in self.drivers}
        
        # Add alternative name mappings for better matching
        for driver in self.drivers:
            # Add first name + last name mapping
            parts = driver.name.split()
            if len(parts) >= 2:
                alt_key = f"{parts[0].lower()} {parts[-1].lower()}"
                self.driver_map[alt_key] = driver
                # Add last name only
                self.driver_map[parts[-1].lower()] = driver
    
    def inject_your_2026_results(self) -> Optional[List]:
        """Inject your specific 2026 qualifying results."""
        
        # Your actual 2026 qualifying results
        actual_results = [
            "George Russell",    # P1
            "Kimi Antonelli",    # P2 
            "Isack Hadjar",      # P3
            "Max Verstappen",    # P4 (assumed)
            "Charles Leclerc",   # P5 (assumed)
            "Lewis Hamilton",    # P6 (assumed)
            "Lando Norris",      # P7 (assumed)
            "Oscar Piastri",     # P8 (assumed)
            "Fernando Alonso",   # P9 (assumed)
            "Lance Stroll"       # P10 (assumed)
        ]
        
        print(f"\n🏁 Injecting your 2026 qualifying results:")
        print(f"📊 P1: George Russell, P2: Kimi Antonelli, P3: Isack Hadjar")
        
        grid_order = []
        
        # Match each result to a driver
        for i, driver_name in enumerate(actual_results, 1):
            key = driver_name.lower()
            
            if key in self.driver_map:
                matched_driver = self.driver_map[key]
                grid_order.append(matched_driver)
                print(f"  ✅ P{i}: {driver_name} → {matched_driver.name} ({matched_driver.team})")
            else:
                print(f"  ❌ P{i}: {driver_name} → NOT FOUND")
        
        # Add remaining drivers not in top 10
        used_drivers = set(grid_order)
        remaining_drivers = [d for d in self.drivers if d not in used_drivers]
        grid_order.extend(remaining_drivers)
        
        if len(grid_order) >= len(actual_results):
            print(f"✅ Successfully created grid with {len(grid_order)} drivers")
            return grid_order
        else:
            print(f"❌ Failed to create complete grid")
            return None
    
    def interactive_manual_input(self) -> Optional[List]:
        """Interactive manual qualifying input."""
        
        print(f"\n🏁 MANUAL QUALIFYING INPUT")
        print(f"=" * 40)
        print(f"Available drivers:")
        for i, driver in enumerate(self.drivers[:10], 1):
            print(f"  {i:2d}. {driver.name} ({driver.team})")
        print(f"     ... and {len(self.drivers) - 10} more")
        
        print(f"\nEnter drivers in qualifying order (or 'your' for your 2026 results):")
        user_input = input("Top 10 (comma-separated): ").strip()
        
        if user_input.lower() == 'your':
            return self.inject_your_2026_results()
        
        if not user_input:
            print("❌ No input provided")
            return None
        
        # Parse input
        driver_names = [name.strip() for name in user_input.split(',')]
        grid_order = []
        
        print(f"\n🔍 Matching drivers:")
        for i, name in enumerate(driver_names[:10], 1):
            matched = self._find_driver(name)
            if matched:
                grid_order.append(matched)
                print(f"  ✅ P{i}: {name} → {matched.name}")
            else:
                print(f"  ❌ P{i}: {name} → NOT FOUND")
        
        # Add remaining drivers
        used_drivers = set(grid_order)
        remaining_drivers = [d for d in self.drivers if d not in used_drivers]
        grid_order.extend(remaining_drivers)
        
        if len(grid_order) >= 10:
            print(f"✅ Created qualifying grid with {len(grid_order)} drivers")
            return grid_order
        else:
            print(f"❌ Only matched {len(grid_order)} drivers")
            return None
    
    def _find_driver(self, name: str):
        """Find driver by name with flexible matching."""
        name_lower = name.lower().strip()
        
        # Direct match
        if name_lower in self.driver_map:
            return self.driver_map[name_lower]
        
        # Partial match
        for key, driver in self.driver_map.items():
            if name_lower in key or key in name_lower:
                return driver
        
        return None

# Easy integration function for main.py
def inject_qualifying_results() -> Optional[List]:
    """Main function to inject qualifying results."""
    
    injector = SimpleQualifyingInjector()
    
    print(f"\n🏁 QUALIFYING RESULTS INPUT")
    print(f"=" * 50)
    print(f"1. Use your 2026 results (Russell P1, Antonelli P2, Hadjar P3)")
    print(f"2. Manual input (enter driver names)")
    print(f"3. Skip (use simulated qualifying)")
    
    choice = input(f"\nSelect option (1-3): ").strip()
    
    if choice == "1":
        return injector.inject_your_2026_results()
    elif choice == "2":
        return injector.interactive_manual_input()
    else:
        print(f"⏭️  Using simulated qualifying")
        return None