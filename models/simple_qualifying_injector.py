"""
Simple Qualifying Injector for 2026 F1 Race Simulation.

Fetches real qualifying/sprint-qualifying results via FastF1 for the selected
track, then falls back to manual input if data is unavailable.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── FastF1 helpers ────────────────────────────────────────────────────────────

def _load_fastf1_session(event_name: str, session_type: str):
    """
    Load a FastF1 session for a 2026 event.

    Args:
        event_name: Full event name, e.g. 'Chinese Grand Prix'
        session_type: FastF1 session identifier, e.g. 'Q', 'Sprint Qualifying',
                      'Qualifying', 'Sprint'
    Returns:
        fastf1.core.Session or None
    """
    try:
        import fastf1
        import warnings
        warnings.filterwarnings("ignore")

        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

        session = fastf1.get_session(2026, event_name, session_type)
        # messages=True is required for Sprint Qualifying result calculation
        session.load(laps=True, telemetry=False, weather=False, messages=True)
        return session
    except Exception as e:
        logger.warning(f"FastF1 could not load {event_name} / {session_type}: {e}")
        return None


def _session_type_for_event(event_name: str) -> Tuple[str, str]:
    """
    Return the preferred FastF1 session type string and a human label for the
    given event.  Sprint-weekend events use 'Sprint Qualifying'; conventional
    weekends use 'Qualifying'.

    Returns:
        (fastf1_session_type, human_label)
    """
    try:
        import fastf1
        import warnings
        warnings.filterwarnings("ignore")

        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

        event = fastf1.get_event(2026, event_name)
        fmt = event.get("EventFormat", "conventional")
        if "sprint" in str(fmt).lower():
            return "Sprint Qualifying", "Sprint Qualifying (SQ)"
        return "Qualifying", "Qualifying (Q)"
    except Exception:
        return "Qualifying", "Qualifying (Q)"


def _results_from_session(session) -> Optional[List[dict]]:
    """
    Extract an ordered list of qualifying results from a loaded FastF1 session.

    Each dict has keys: position, abbreviation, full_name, team_name, best_time_str
    Returns None if no usable data is found.
    """
    try:
        import pandas as pd

        results = session.results
        if results is None or results.empty:
            return None

        # Filter rows that have a valid position
        positioned = results[results["Position"].notna()].copy()
        if positioned.empty:
            return None

        positioned = positioned.sort_values("Position")

        output = []
        for _, row in positioned.iterrows():
            pos = int(row["Position"])
            abbrev = str(row.get("Abbreviation", "???"))
            full_name = str(row.get("FullName", abbrev))
            team = str(row.get("TeamName", "Unknown"))

            # Best time: prefer Q3 → Q2 → Q1
            best_td = None
            for col in ("Q3", "Q2", "Q1"):
                val = row.get(col)
                if val is not None and pd.notna(val):
                    best_td = val
                    break

            if best_td is not None:
                total_s = best_td.total_seconds()
                mins = int(total_s // 60)
                secs = total_s % 60
                best_time_str = f"{mins}:{secs:06.3f}"
            else:
                best_time_str = "N/A"

            output.append({
                "position": pos,
                "abbreviation": abbrev,
                "full_name": full_name,
                "team_name": team,
                "best_time_str": best_time_str,
            })

        return output if output else None

    except Exception as e:
        logger.warning(f"Could not extract results from session: {e}")
        return None


# ── Driver matching ───────────────────────────────────────────────────────────

class SimpleQualifyingInjector:
    """Qualifying injection: FastF1-first, manual-input fallback."""

    def __init__(self):
        from data.drivers import get_all_drivers
        self.drivers = get_all_drivers()
        self._build_driver_map()

    def _build_driver_map(self):
        """Build a flexible name → driver lookup."""
        self.driver_map = {}
        for driver in self.drivers:
            # Full name (lower)
            self.driver_map[driver.name.lower()] = driver
            parts = driver.name.split()
            if len(parts) >= 2:
                # Last name only
                self.driver_map[parts[-1].lower()] = driver
                # First + last
                self.driver_map[f"{parts[0].lower()} {parts[-1].lower()}"] = driver

        # 2026 driver abbreviation → driver object
        ABBREV_MAP = {
            "RUS": "George Russell",
            "ANT": "Kimi Antonelli",
            "NOR": "Lando Norris",
            "PIA": "Oscar Piastri",
            "LEC": "Charles Leclerc",
            "HAM": "Lewis Hamilton",
            "VER": "Max Verstappen",
            "HAD": "Isack Hadjar",
            "GAS": "Pierre Gasly",
            "COL": "Franco Colapinto",
            "HUL": "Nico Hulkenberg",
            "BOR": "Gabriel Bortoleto",
            "LAW": "Liam Lawson",
            "LIN": "Arvid Lindblad",
            "ALO": "Fernando Alonso",
            "STR": "Lance Stroll",
            "ALB": "Alexander Albon",
            "SAI": "Carlos Sainz",
            "BEA": "Oliver Bearman",
            "OCO": "Esteban Ocon",
            "BOT": "Valtteri Bottas",
            "PER": "Sergio Perez",
        }
        name_to_driver = {d.name: d for d in self.drivers}
        for abbrev, full_name in ABBREV_MAP.items():
            if full_name in name_to_driver:
                self.driver_map[abbrev.lower()] = name_to_driver[full_name]

    def _find_driver(self, name: str):
        """Flexible driver lookup by name or abbreviation."""
        key = name.lower().strip()
        if key in self.driver_map:
            return self.driver_map[key]
        # Partial match
        for map_key, driver in self.driver_map.items():
            if key in map_key or map_key in key:
                return driver
        return None

    # ── FastF1 auto-fetch ─────────────────────────────────────────────────────

    def fetch_from_fastf1(
        self, track_name: str, qualifying_session: str = "auto"
    ) -> Optional[List]:
        """
        Try to fetch qualifying results from FastF1 for the given track.

        Args:
            track_name: Internal track name.
            qualifying_session: Which qualifying session to load:
                'Sprint Qualifying' — SQ session (grid for Sprint Race)
                'Qualifying'        — full Q session (grid for Full Race)
                'auto'              — auto-detect based on event format (default)

        Returns ordered list of driver objects, or None on failure.
        """
        # Map our internal track names to F1 event names
        TRACK_TO_EVENT = {
            "albert park circuit": "Australian Grand Prix",
            "shanghai international circuit": "Chinese Grand Prix",
            "suzuka circuit": "Japanese Grand Prix",
            "bahrain international circuit": "Bahrain Grand Prix",
            "jeddah corniche circuit": "Saudi Arabian Grand Prix",
            "miami international autodrome": "Miami Grand Prix",
            "circuit gilles villeneuve": "Canadian Grand Prix",
            "circuit de monaco": "Monaco Grand Prix",
            "circuit de barcelona-catalunya": "Barcelona Grand Prix",
            "red bull ring": "Austrian Grand Prix",
            "silverstone circuit": "British Grand Prix",
            "circuit de spa-francorchamps": "Belgian Grand Prix",
            "hungaroring": "Hungarian Grand Prix",
            "circuit zandvoort": "Dutch Grand Prix",
            "autodromo nazionale monza": "Italian Grand Prix",
            "madrid street circuit": "Spanish Grand Prix",
            "baku city circuit": "Azerbaijan Grand Prix",
            "marina bay street circuit": "Singapore Grand Prix",
            "circuit of the americas": "United States Grand Prix",
            "autodromo hermanos rodriguez": "Mexico City Grand Prix",
            "autodromo jose carlos pace": "São Paulo Grand Prix",
            "las vegas strip circuit": "Las Vegas Grand Prix",
            "losail international circuit": "Qatar Grand Prix",
            "yas marina circuit": "Abu Dhabi Grand Prix",
        }

        event_name = TRACK_TO_EVENT.get(track_name.lower())
        if not event_name:
            # Try partial match
            for key, val in TRACK_TO_EVENT.items():
                if track_name.lower() in key or key in track_name.lower():
                    event_name = val
                    break

        if not event_name:
            print(f"  ⚠️  No event mapping found for track: {track_name}")
            return None

        # Determine which qualifying session to load
        if qualifying_session == "auto":
            session_type, human_label = _session_type_for_event(event_name)
        else:
            # Explicit override — use exactly what was requested
            session_type = qualifying_session
            human_label = qualifying_session
        print(f"  🔍 Fetching {human_label} results for {event_name} via FastF1...")

        session = _load_fastf1_session(event_name, session_type)
        if session is None:
            return None

        results = _results_from_session(session)
        if not results:
            print(f"  ⚠️  FastF1 returned no usable results for {event_name} {session_type}")
            return None

        # Print what we found
        print(f"\n  ✅ {human_label} results fetched ({len(results)} drivers):")
        print(f"  {'Pos':<4} {'Driver':<22} {'Team':<22} {'Best Time'}")
        print(f"  {'-'*4} {'-'*22} {'-'*22} {'-'*10}")
        for r in results:
            print(f"  P{r['position']:<3} {r['full_name']:<22} {r['team_name']:<22} {r['best_time_str']}")

        # Build ordered driver list
        grid_order = []
        unmatched = []
        for r in results:
            # Try abbreviation first, then full name
            driver = self._find_driver(r["abbreviation"]) or self._find_driver(r["full_name"])
            if driver:
                grid_order.append(driver)
            else:
                unmatched.append(r["full_name"])

        if unmatched:
            print(f"\n  ⚠️  Could not match: {', '.join(unmatched)}")

        # Append any drivers not in the results (e.g. PER with no lap time)
        used = set(grid_order)
        remaining = [d for d in self.drivers if d not in used]
        grid_order.extend(remaining)

        print(f"\n  ✅ Grid built: {len(grid_order)} drivers")
        return grid_order

    # ── Manual input ──────────────────────────────────────────────────────────

    def interactive_manual_input(self) -> Optional[List]:
        """Interactive manual qualifying input."""
        print(f"\n🏁 MANUAL QUALIFYING INPUT")
        print(f"{'='*40}")
        print(f"Available drivers:")
        for i, driver in enumerate(self.drivers[:12], 1):
            print(f"  {i:2d}. {driver.name} ({driver.team})")
        print(f"     ... and {len(self.drivers) - 12} more")

        print(f"\nEnter top 10 drivers in qualifying order (comma-separated):")
        user_input = input("Top 10: ").strip()

        if not user_input:
            print("❌ No input provided")
            return None

        driver_names = [name.strip() for name in user_input.split(",")]
        grid_order = []

        print(f"\n🔍 Matching drivers:")
        for i, name in enumerate(driver_names[:10], 1):
            matched = self._find_driver(name)
            if matched:
                grid_order.append(matched)
                print(f"  ✅ P{i}: {name} → {matched.name}")
            else:
                print(f"  ❌ P{i}: {name} → NOT FOUND")

        # Append remaining drivers
        used = set(grid_order)
        remaining = [d for d in self.drivers if d not in used]
        grid_order.extend(remaining)

        if len(grid_order) >= 10:
            print(f"✅ Created qualifying grid with {len(grid_order)} drivers")
            return grid_order
        else:
            print(f"❌ Only matched {len(grid_order)} drivers")
            return None


# ── Public entry point ────────────────────────────────────────────────────────

# Tracks with a Sprint Qualifying session in 2026
_SPRINT_WEEKEND_TRACKS = {
    'shanghai international circuit',
    'miami international autodrome',
    'circuit gilles villeneuve',
    'silverstone circuit',
    'circuit zandvoort',
    'marina bay street circuit',
}


def is_sprint_weekend(track_name: str) -> bool:
    """
    Return True if the given track hosts a Sprint Qualifying session in 2026.

    Checks the hardcoded set first; falls back to FastF1 event metadata.
    """
    if track_name.lower() in _SPRINT_WEEKEND_TRACKS:
        return True

    # Confirm via FastF1 for any edge cases
    try:
        import fastf1, warnings, os
        warnings.filterwarnings("ignore")
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

        TRACK_TO_EVENT = {
            'albert park circuit': 'Australian Grand Prix',
            'shanghai international circuit': 'Chinese Grand Prix',
            'suzuka circuit': 'Japanese Grand Prix',
            'bahrain international circuit': 'Bahrain Grand Prix',
            'jeddah corniche circuit': 'Saudi Arabian Grand Prix',
            'miami international autodrome': 'Miami Grand Prix',
            'circuit gilles villeneuve': 'Canadian Grand Prix',
            'circuit de monaco': 'Monaco Grand Prix',
            'circuit de barcelona-catalunya': 'Barcelona Grand Prix',
            'red bull ring': 'Austrian Grand Prix',
            'silverstone circuit': 'British Grand Prix',
            'circuit de spa-francorchamps': 'Belgian Grand Prix',
            'hungaroring': 'Hungarian Grand Prix',
            'circuit zandvoort': 'Dutch Grand Prix',
            'autodromo nazionale monza': 'Italian Grand Prix',
            'madrid street circuit': 'Spanish Grand Prix',
            'baku city circuit': 'Azerbaijan Grand Prix',
            'marina bay street circuit': 'Singapore Grand Prix',
            'circuit of the americas': 'United States Grand Prix',
            'autodromo hermanos rodriguez': 'Mexico City Grand Prix',
            'autodromo jose carlos pace': 'São Paulo Grand Prix',
            'las vegas strip circuit': 'Las Vegas Grand Prix',
            'losail international circuit': 'Qatar Grand Prix',
            'yas marina circuit': 'Abu Dhabi Grand Prix',
        }
        key = track_name.lower()
        event_name = TRACK_TO_EVENT.get(key)
        if not event_name:
            for k, v in TRACK_TO_EVENT.items():
                if key in k or k in key:
                    event_name = v
                    break
        if event_name:
            event = fastf1.get_event(2026, event_name)
            fmt = event.get("EventFormat", "conventional")
            return "sprint" in str(fmt).lower()
    except Exception:
        pass

    return False


def inject_qualifying_results(
    track_name: str = "",
    auto: bool = False,
    qualifying_session: str = "auto",
) -> Optional[List]:
    """
    Main function called from main.py to inject qualifying results.

    Args:
        track_name: Internal track name (e.g. 'Shanghai International Circuit').
                    Used for FastF1 auto-fetch.
        auto: If True, skip the interactive menu and silently auto-fetch from
              FastF1 (used for sprint-qualifying weekends where no stop is needed).
        qualifying_session: Which qualifying session to fetch:
            'Sprint Qualifying' — SQ session (grid for Sprint Race)
            'Qualifying'        — full Q session (grid for Full Race)
            'auto'              — auto-detect based on track format (default)

    Returns:
        Ordered list of driver objects representing the starting grid, or None.
    """
    injector = SimpleQualifyingInjector()

    if auto:
        # No menu, no prompt — just fetch and return
        if not track_name:
            return None
        return injector.fetch_from_fastf1(track_name, qualifying_session=qualifying_session)

    print(f"\n🏁 QUALIFYING RESULTS INPUT")
    print(f"{'='*50}")
    print(f"1. Auto-fetch from FastF1 (uses real 2026 data)")
    print(f"2. Manual input (enter driver names)")
    print(f"3. Skip (use simulated qualifying)")

    choice = input(f"\nSelect option (1-3): ").strip()

    if choice == "1":
        if not track_name:
            track_name = input("Enter track name (e.g. 'Shanghai International Circuit'): ").strip()
        return injector.fetch_from_fastf1(track_name, qualifying_session=qualifying_session)

    elif choice == "2":
        return injector.interactive_manual_input()

    else:
        print(f"⏭️  Using simulated qualifying")
        return None
