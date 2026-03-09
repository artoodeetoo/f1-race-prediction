# Grid Adjustments System - Quick Reference

## 🔧 Overview
The Grid Adjustments System allows you to modify the starting grid after qualifying but before the race starts. Perfect for handling real-world scenarios like crashes, penalties, and other incidents.

## 🚀 How to Access
When running `python main.py`, after qualifying results are determined:

```
🔧 Make grid adjustments before race? (formation lap crash, penalties, etc.) (y/n): y
```

## 📋 Available Adjustments

### 1. 🚨 Remove Driver (Crash/DNS)
**Use for:** Formation lap crashes, technical failures, medical issues
- **Action:** Completely removes driver from race
- **Effect:** All other drivers move up one position
- **Grid Size:** Reduces from 22 to 21 (or fewer) drivers

**Example:**
```
Driver: Kimi Antonelli
Reason: Formation lap crash
Result: Antonelli out, Russell P1 → P1, Hadjar P3 → P2, etc.
```

### 2. ⚡ Apply Position Penalty
**Use for:** Engine penalties, gearbox penalties, technical violations
- **Action:** Moves driver back X positions on grid
- **Effect:** Other drivers move up to fill gap
- **Grid Size:** Remains at 22 drivers

**Example:**
```
Driver: Max Verstappen
Penalty: 10 positions (engine penalty)
Result: P4 → P14, drivers behind move up
```

### 3. 🔄 Move to Back of Grid
**Use for:** Major technical violations, multiple penalties
- **Action:** Moves driver to last position
- **Effect:** All drivers behind original position move up one
- **Grid Size:** Remains at 22 drivers

### 4. 🏁 Move to Pit Lane Start
**Use for:** Setup changes after qualifying, major violations
- **Action:** Driver starts from pit lane (effectively last)
- **Effect:** Similar to back of grid but marked as pit lane start
- **Grid Size:** Remains at 22 drivers

### 5. ↩️ Undo Last Adjustment
**Use for:** Correcting mistakes, changing your mind
- **Action:** Reverses the most recent adjustment
- **Effect:** Restores grid to previous state

### 6. 🔄 Reset to Original Qualifying
**Use for:** Starting over with adjustments
- **Action:** Removes all adjustments
- **Effect:** Returns to original qualifying order

## 🎯 Common Scenarios

### Formation Lap Crash
```
Original: P1-Russell, P2-Antonelli, P3-Hadjar
Adjustment: Remove Antonelli (formation lap crash)
Result: P1-Russell, P2-Hadjar, P3-Verstappen (21 drivers)
```

### Engine Penalty
```
Original: P1-Russell, P2-Antonelli, P3-Hadjar, P4-Verstappen
Adjustment: Verstappen +10 positions
Result: P1-Russell, P2-Antonelli, P3-Hadjar, P4-Leclerc... P14-Verstappen
```

### Multiple Adjustments
```
1. Antonelli crashes (DNS) → 21 drivers
2. Hamilton +5 penalty (P6→P11)
3. Alonso pit lane start (→P21)
Final grid significantly shuffled
```

## 🔍 Smart Features

### Driver Name Matching
- **Full names:** "George Russell" ✅
- **Last names:** "Russell" ✅
- **First names:** "George" ✅
- **Partial match:** "Rus" ✅

### Real-Time Grid Display
- Shows current grid positions after each adjustment
- Highlights penalized drivers with symbols (⚡🏁🚨)
- Displays running count of adjustments made

### Undo/Reset Protection
- Undo last adjustment if you make a mistake
- Reset everything to start over
- Adjustments applied in sequence for accuracy

## 📊 Impact on Race Simulation

### Starting Positions
- Race simulation uses your adjusted grid
- Qualifying results display shows final grid
- Position tracking accounts for adjustments

### Driver Removal Effects
- Removed drivers don't participate in race
- Points, statistics, and analysis exclude DNS drivers
- Grid size affects race dynamics (21 vs 22 drivers)

### Penalty Effects
- Penalized drivers start from new positions
- Race predictions adjust for grid position changes
- Overtaking opportunities change based on new neighbors

## 💡 Best Practices

### When to Use
- ✅ After real qualifying results are known
- ✅ When formation lap incidents occur
- ✅ For engine/gearbox penalty applications
- ✅ Simulating "what if" scenarios

### Adjustment Order
1. **Remove drivers first** (crashes, DNS)
2. **Apply penalties** (position changes)
3. **Handle pit lane starts** (last)
4. **Review final grid** before confirming

### Double-Check
- Verify driver names are correct
- Confirm penalty positions are realistic
- Review final grid order makes sense
- Use undo if needed

## 🚨 Error Handling

### Driver Not Found
```
❌ Driver 'Hamilton' not found in grid
Available options: ['Lewis Hamilton', 'Hamilton Lewis']
```
**Solution:** Use full name or check spelling

### Invalid Penalty
```
❌ Penalty must be positive number
```
**Solution:** Enter positive integer (5, 10, etc.)

### Grid Too Small
If grid becomes too small (<10 drivers), system will warn you but allow continuation.

## 📈 Real-World Examples

### 2023 Brazilian GP Style
```
Qualifying: P1-Leclerc, P2-Verstappen, P3-Alonso
Formation lap: Verstappen technical issue (DNS)
Final grid: P1-Leclerc, P2-Alonso, P3-Hamilton (21 drivers)
Race impact: Completely different race dynamics
```

### Multi-Penalty Weekend
```
Qualifying: Standard order
Penalties: 
- Verstappen: +10 (engine)
- Hamilton: +5 (gearbox)  
- Gasly: Pit lane start
Result: Massive grid shuffle, unexpected front-runners
```

---

**💡 Pro Tip:** The grid adjustment system makes your race predictions incredibly realistic by handling the unpredictable nature of F1 race weekends!