"""
Module containing data for F1 2026 teams with their attributes and statistics.
Updated for the 2026 season with new power unit regulations.
"""

class Team:
    def __init__(self, name, constructor, engine, performance, reliability, 
                 pit_efficiency, development_rate, aerodynamics, power,
                 active_aero=80, energy_recovery=80, budget_cap_efficiency=80):
        self.name = name
        self.constructor = constructor
        self.engine = engine
        self.performance = performance  # Overall car performance (1-100)
        self.reliability = reliability  # Car reliability rating (1-100)
        self.pit_efficiency = pit_efficiency  # Pit stop efficiency (1-100)
        self.development_rate = development_rate  # In-season development rate (1-100)
        self.aerodynamics = aerodynamics  # Aerodynamic efficiency (1-100)
        self.power = power  # Engine power (1-100)
        # New 2026 regulation attributes
        self.active_aero = active_aero  # Active aerodynamics system efficiency (1-100)
        self.energy_recovery = energy_recovery  # ERS/battery efficiency (1-100)
        self.budget_cap_efficiency = budget_cap_efficiency  # Resource management (1-100)
    
    def __str__(self):
        return f"{self.name} ({self.engine})"
    
    def get_car_rating(self):
        """Calculate the overall car rating for 2026 regulations."""
        return (self.performance * 0.20 + 
                self.reliability * 0.15 + 
                self.aerodynamics * 0.20 + 
                self.power * 0.15 +
                self.active_aero * 0.15 +
                self.energy_recovery * 0.15)
    
    def get_race_pace(self):
        """Calculate race-specific performance."""
        return (self.performance * 0.25 +
                self.reliability * 0.20 +
                self.energy_recovery * 0.20 +
                self.aerodynamics * 0.20 +
                self.power * 0.15)
    
    def get_qualifying_pace(self):
        """Calculate qualifying-specific performance."""
        return (self.performance * 0.20 +
                self.power * 0.25 +
                self.aerodynamics * 0.25 +
                self.active_aero * 0.20 +
                self.energy_recovery * 0.10)


# 2026 F1 Teams with realistic attributes
# New era with major regulation changes:
# - New power units with increased electrical power (350kW MGU-K)
# - Active aerodynamics (DRS replaced by X-Mode)
# - Sustainable fuels
# - Audi officially joins as factory team (formerly Sauber)
# - Cadillac enters F1 as the 11th team (GM/Andretti partnership)
# Updated based on 2026 China GP actual results (Race 2, March 2026)
TEAMS = {
    # Mercedes: #1 team — dominated S3/energy recovery, Antonelli P1, Russell P2
    "red_bull": Team("Red Bull Racing", "Red Bull", "Red Bull Ford",
                     85, 88, 93, 88, 87, 82,
                     active_aero=85, energy_recovery=82, budget_cap_efficiency=88),
    
    # Ferrari: Strong #2 team — Hamilton P3, Leclerc P4
    "ferrari": Team("Ferrari", "Ferrari", "Ferrari",
                    94, 89, 93, 92, 93, 95,
                    active_aero=92, energy_recovery=93, budget_cap_efficiency=88),
    
    # Mercedes: Upgraded to #1 — S3/energy dominance, 1-2 finish in China
    "mercedes": Team("Mercedes", "Mercedes", "Mercedes",
                     97, 93, 96, 94, 95, 97,
                     active_aero=96, energy_recovery=98, budget_cap_efficiency=92),
    
    # McLaren: Strong #3 — Piastri P5, Norris P6, not quite matching Mercedes/Ferrari
    "mclaren": Team("McLaren", "McLaren", "Mercedes",
                    93, 91, 94, 94, 94, 94,
                    active_aero=94, energy_recovery=92, budget_cap_efficiency=93),
    
    # Aston Martin: Critical downgrade — P19/P21, Honda PU transition failed, 3+ sec off pace
    "aston_martin": Team("Aston Martin", "Aston Martin", "Honda",
                         76, 82, 88, 84, 78, 80,
                         active_aero=76, energy_recovery=78, budget_cap_efficiency=83),
    
    # Alpine: Upgraded — Gasly P7 consistently, Renault PU significantly improved
    "alpine": Team("Alpine", "Alpine", "Renault",
                   87, 83, 87, 86, 87, 88,
                   active_aero=86, energy_recovery=87, budget_cap_efficiency=83),
    
    # Williams: Slight downgrade — Mercedes PU helps but chassis is weak, P17/P18
    "williams": Team("Williams", "Williams", "Mercedes",
                     83, 85, 87, 86, 83, 93,
                     active_aero=82, energy_recovery=85, budget_cap_efficiency=87),
    
    # Racing Bulls: Similar — Lawson/Lindblad P13-14 as expected
    "racing_bulls": Team("Racing Bulls", "Racing Bulls", "Red Bull Ford",
                         83, 86, 86, 84, 84, 82,
                         active_aero=82, energy_recovery=82, budget_cap_efficiency=82),
    
    # Audi: Similar — Hulkenberg P11 is about right for lower-midfield
    "audi": Team("Audi", "Audi", "Audi",
                 82, 80, 85, 88, 83, 85,
                 active_aero=86, energy_recovery=88, budget_cap_efficiency=90),
    
    # Haas: Upgraded — Bearman P9 shows genuine upper-midfield pace, Ferrari PU strong
    "haas": Team("Haas", "Haas", "Ferrari",
                 85, 83, 83, 82, 84, 96,
                 active_aero=83, energy_recovery=84, budget_cap_efficiency=79),
    
    # Cadillac: Slight downgrade — Bottas/Perez clearly slowest, P20/P22
    "cadillac": Team("Cadillac", "Cadillac", "Cadillac",
                     75, 76, 79, 80, 77, 78,
                     active_aero=74, energy_recovery=75, budget_cap_efficiency=83)
}

def get_team_by_name(name):
    """Get a team by their full or partial name."""
    name = name.lower()
    for team_id, team in TEAMS.items():
        if name in team.name.lower():
            return team
    return None

def get_all_teams():
    """Return all teams."""
    return list(TEAMS.values())

def get_team_by_engine(engine):
    """Get all teams using a specific engine manufacturer."""
    engine = engine.lower()
    return [team for team in TEAMS.values() if engine in team.engine.lower()]