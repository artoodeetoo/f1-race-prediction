"""
Grid Adjustments System for F1 Race Simulation.

This module allows post-qualifying adjustments such as:
- Driver crashes/withdrawals (formation lap, warm-up lap)
- Engine penalties
- Grid drops for technical violations
- DNS (Did Not Start) scenarios
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AdjustmentType(Enum):
    """Types of grid adjustments."""
    CRASH = "crash"
    DNS = "dns"  # Did Not Start
    ENGINE_PENALTY = "engine_penalty"
    GEARBOX_PENALTY = "gearbox_penalty"
    TECHNICAL_VIOLATION = "technical_violation"
    FORMATION_LAP_CRASH = "formation_lap_crash"
    PIT_LANE_START = "pit_lane_start"
    BACK_OF_GRID = "back_of_grid"

@dataclass
class GridAdjustment:
    """Represents a single grid adjustment."""
    driver_name: str
    adjustment_type: AdjustmentType
    positions: int = 0  # Number of positions (for penalties)
    description: str = ""
    remove_from_race: bool = False  # True for DNS/crash

class GridAdjustmentManager:
    """Manages grid adjustments before race start."""
    
    def __init__(self):
        self.adjustments = []
        self.original_grid = None
        self.adjusted_grid = None
    
    def set_original_grid(self, grid_positions: List):
        """Set the original qualifying grid positions."""
        self.original_grid = grid_positions.copy()
        self.adjusted_grid = grid_positions.copy()
        logger.info(f"Set original grid: P1-{grid_positions[0].name}")
    
    def interactive_grid_adjustment(self) -> bool:
        """Interactive menu for grid adjustments."""
        if not self.original_grid:
            print("❌ No qualifying grid set")
            return False
        
        print("\n" + "="*70)
        print("🔧 GRID ADJUSTMENTS - Pre-Race Modifications")
        print("="*70)
        print("Make adjustments for crashes, penalties, or other incidents")
        print("before the race starts.\n")
        
        while True:
            self._display_current_grid()
            print("\nAdjustment Options:")
            print("1. Remove driver (crash/DNS)")
            print("2. Apply position penalty")
            print("3. Move to back of grid")
            print("4. Move to pit lane start")
            print("5. Undo last adjustment")
            print("6. Reset to original qualifying")
            print("7. Finish adjustments")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                self._handle_driver_removal()
            elif choice == "2":
                self._handle_position_penalty()
            elif choice == "3":
                self._handle_back_of_grid()
            elif choice == "4":
                self._handle_pit_lane_start()
            elif choice == "5":
                self._undo_last_adjustment()
            elif choice == "6":
                self._reset_grid()
            elif choice == "7":
                break
            else:
                print("❌ Invalid option")
        
        return len(self.adjustments) > 0
    
    def _display_current_grid(self):
        """Display current grid positions."""
        print(f"\n📊 CURRENT GRID ({len(self.adjusted_grid)} drivers):")
        print("-" * 50)
        
        for i, driver in enumerate(self.adjusted_grid[:10], 1):
            # Check if this driver has adjustments
            adjustment_info = ""
            for adj in self.adjustments:
                if adj.driver_name == driver.name:
                    if adj.adjustment_type == AdjustmentType.FORMATION_LAP_CRASH:
                        adjustment_info = " 🚨 CRASHED"
                    elif adj.adjustment_type == AdjustmentType.ENGINE_PENALTY:
                        adjustment_info = f" ⚡ +{adj.positions} penalty"
                    elif adj.adjustment_type == AdjustmentType.PIT_LANE_START:
                        adjustment_info = " 🏁 Pit lane start"
                    break
            
            print(f"P{i:2d}: {driver.name:20} ({driver.team:12}){adjustment_info}")
        
        if len(self.adjusted_grid) > 10:
            print(f"     ... and {len(self.adjusted_grid) - 10} more drivers")
        
        if self.adjustments:
            print(f"\n📝 Applied {len(self.adjustments)} adjustment(s)")
    
    def _handle_driver_removal(self):
        """Handle driver removal from grid."""
        print("\n🚨 REMOVE DRIVER FROM RACE")
        print("-" * 30)
        
        driver_name = input("Enter driver name to remove: ").strip()
        matched_driver = self._find_driver(driver_name)
        
        if not matched_driver:
            print(f"❌ Driver '{driver_name}' not found in grid")
            return
        
        print(f"\nReason for removal:")
        print("1. Formation lap crash")
        print("2. Technical issue (DNS)")
        print("3. Medical issue")
        print("4. Other")
        
        reason_choice = input("Select reason (1-4): ").strip()
        
        reasons = {
            "1": (AdjustmentType.FORMATION_LAP_CRASH, "Formation lap crash"),
            "2": (AdjustmentType.DNS, "Technical issue - Did not start"),
            "3": (AdjustmentType.DNS, "Medical issue - Did not start"),
            "4": (AdjustmentType.DNS, "Other - Did not start")
        }
        
        if reason_choice in reasons:
            adj_type, description = reasons[reason_choice]
            
            # Remove driver from grid
            self.adjusted_grid = [d for d in self.adjusted_grid if d.name != matched_driver.name]
            
            # Add adjustment record
            adjustment = GridAdjustment(
                driver_name=matched_driver.name,
                adjustment_type=adj_type,
                description=description,
                remove_from_race=True
            )
            self.adjustments.append(adjustment)
            
            print(f"✅ Removed {matched_driver.name} from race: {description}")
            print(f"📊 Grid size reduced to {len(self.adjusted_grid)} drivers")
        else:
            print("❌ Invalid selection")
    
    def _handle_position_penalty(self):
        """Handle position penalties."""
        print("\n⚡ APPLY POSITION PENALTY")
        print("-" * 25)
        
        driver_name = input("Enter driver name: ").strip()
        matched_driver = self._find_driver(driver_name)
        
        if not matched_driver:
            print(f"❌ Driver '{driver_name}' not found in grid")
            return
        
        try:
            positions = int(input("Penalty positions (e.g., 5 for 5-place penalty): "))
            if positions <= 0:
                print("❌ Penalty must be positive number")
                return
        except ValueError:
            print("❌ Invalid number")
            return
        
        print(f"\nPenalty type:")
        print("1. Engine penalty")
        print("2. Gearbox penalty")
        print("3. Technical violation")
        print("4. Other penalty")
        
        penalty_choice = input("Select type (1-4): ").strip()
        
        penalty_types = {
            "1": (AdjustmentType.ENGINE_PENALTY, "Engine penalty"),
            "2": (AdjustmentType.GEARBOX_PENALTY, "Gearbox penalty"),
            "3": (AdjustmentType.TECHNICAL_VIOLATION, "Technical violation"),
            "4": (AdjustmentType.TECHNICAL_VIOLATION, "Other penalty")
        }
        
        if penalty_choice in penalty_types:
            adj_type, description = penalty_types[penalty_choice]
            
            # Apply penalty
            current_pos = self.adjusted_grid.index(matched_driver)
            new_pos = min(len(self.adjusted_grid) - 1, current_pos + positions)
            
            # Move driver in grid
            self.adjusted_grid.pop(current_pos)
            self.adjusted_grid.insert(new_pos, matched_driver)
            
            # Record adjustment
            adjustment = GridAdjustment(
                driver_name=matched_driver.name,
                adjustment_type=adj_type,
                positions=positions,
                description=f"{description} - {positions} places"
            )
            self.adjustments.append(adjustment)
            
            print(f"✅ Applied {positions}-place penalty to {matched_driver.name}")
            print(f"📊 Moved from P{current_pos + 1} to P{new_pos + 1}")
        else:
            print("❌ Invalid selection")
    
    def _handle_back_of_grid(self):
        """Move driver to back of grid."""
        print("\n🔄 MOVE TO BACK OF GRID")
        print("-" * 25)
        
        driver_name = input("Enter driver name: ").strip()
        matched_driver = self._find_driver(driver_name)
        
        if not matched_driver:
            print(f"❌ Driver '{driver_name}' not found in grid")
            return
        
        current_pos = self.adjusted_grid.index(matched_driver)
        
        # Move to back
        self.adjusted_grid.pop(current_pos)
        self.adjusted_grid.append(matched_driver)
        
        # Record adjustment
        adjustment = GridAdjustment(
            driver_name=matched_driver.name,
            adjustment_type=AdjustmentType.BACK_OF_GRID,
            description="Moved to back of grid"
        )
        self.adjustments.append(adjustment)
        
        print(f"✅ Moved {matched_driver.name} to back of grid")
        print(f"📊 Now starting P{len(self.adjusted_grid)}")
    
    def _handle_pit_lane_start(self):
        """Set driver to start from pit lane."""
        print("\n🏁 PIT LANE START")
        print("-" * 18)
        
        driver_name = input("Enter driver name: ").strip()
        matched_driver = self._find_driver(driver_name)
        
        if not matched_driver:
            print(f"❌ Driver '{driver_name}' not found in grid")
            return
        
        # Move to back (pit lane starts last)
        current_pos = self.adjusted_grid.index(matched_driver)
        self.adjusted_grid.pop(current_pos)
        self.adjusted_grid.append(matched_driver)
        
        # Record adjustment
        adjustment = GridAdjustment(
            driver_name=matched_driver.name,
            adjustment_type=AdjustmentType.PIT_LANE_START,
            description="Starting from pit lane"
        )
        self.adjustments.append(adjustment)
        
        print(f"✅ {matched_driver.name} will start from pit lane")
    
    def _undo_last_adjustment(self):
        """Undo the last adjustment."""
        if not self.adjustments:
            print("❌ No adjustments to undo")
            return
        
        last_adjustment = self.adjustments.pop()
        
        # Reset grid and reapply remaining adjustments
        self.adjusted_grid = self.original_grid.copy()
        temp_adjustments = self.adjustments.copy()
        self.adjustments = []
        
        for adj in temp_adjustments:
            self._reapply_adjustment(adj)
        
        print(f"✅ Undid: {last_adjustment.description} for {last_adjustment.driver_name}")
    
    def _reset_grid(self):
        """Reset to original qualifying grid."""
        self.adjusted_grid = self.original_grid.copy()
        self.adjustments = []
        print("✅ Reset to original qualifying grid")
    
    def _find_driver(self, driver_name: str):
        """Find driver in current grid."""
        driver_name_lower = driver_name.lower()
        
        # Exact match first
        for driver in self.adjusted_grid:
            if driver.name.lower() == driver_name_lower:
                return driver
        
        # Partial match
        for driver in self.adjusted_grid:
            if driver_name_lower in driver.name.lower():
                return driver
            # Try last name
            if driver_name_lower in driver.name.lower().split()[-1]:
                return driver
        
        return None
    
    def _reapply_adjustment(self, adjustment: GridAdjustment):
        """Reapply an adjustment (for undo functionality)."""
        # This is a simplified reapplication - in practice, you'd need
        # more sophisticated logic to handle complex adjustment sequences
        self.adjustments.append(adjustment)
    
    def get_final_grid(self) -> List:
        """Get the final adjusted grid."""
        return self.adjusted_grid.copy() if self.adjusted_grid else self.original_grid.copy()
    
    def get_adjustment_summary(self) -> str:
        """Get summary of all adjustments made."""
        if not self.adjustments:
            return "No adjustments made"
        
        summary = f"Grid adjustments made ({len(self.adjustments)}):\n"
        for i, adj in enumerate(self.adjustments, 1):
            summary += f"{i}. {adj.driver_name}: {adj.description}\n"
        
        return summary.strip()
    
    def get_removed_drivers(self) -> List[str]:
        """Get list of drivers removed from the race."""
        return [adj.driver_name for adj in self.adjustments if adj.remove_from_race]
    
    def export_adjustments(self) -> Dict:
        """Export adjustments for saving/loading."""
        return {
            "adjustments": [
                {
                    "driver_name": adj.driver_name,
                    "adjustment_type": adj.adjustment_type.value,
                    "positions": adj.positions,
                    "description": adj.description,
                    "remove_from_race": adj.remove_from_race
                }
                for adj in self.adjustments
            ],
            "final_grid_size": len(self.adjusted_grid) if self.adjusted_grid else 0
        }