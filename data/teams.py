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
TEAMS = {
    "red_bull": Team("Red Bull Racing", "Red Bull", "Red Bull Ford", 
                     94, 91, 95, 92, 95, 93,
                     active_aero=94, energy_recovery=91, budget_cap_efficiency=90),
    
    "ferrari": Team("Ferrari", "Ferrari", "Ferrari", 
                    95, 89, 93, 93, 94, 96,
                    active_aero=93, energy_recovery=94, budget_cap_efficiency=88),
    
    "mercedes": Team("Mercedes", "Mercedes", "Mercedes", 
                     93, 93, 96, 94, 93, 94,
                     active_aero=95, energy_recovery=96, budget_cap_efficiency=92),
    
    "mclaren": Team("McLaren", "McLaren", "Mercedes", 
                    96, 91, 94, 95, 96, 94,
                    active_aero=96, energy_recovery=93, budget_cap_efficiency=94),
    
    "aston_martin": Team("Aston Martin", "Aston Martin", "Honda", 
                         89, 88, 91, 90, 90, 92,
                         active_aero=88, energy_recovery=90, budget_cap_efficiency=87),
    
    "alpine": Team("Alpine", "Alpine", "Renault", 
                   84, 82, 87, 85, 85, 86,
                   active_aero=84, energy_recovery=85, budget_cap_efficiency=83),
    
    "williams": Team("Williams", "Williams", "Mercedes", 
                     86, 87, 88, 88, 86, 94,
                     active_aero=85, energy_recovery=87, budget_cap_efficiency=89),
    
    "racing_bulls": Team("Racing Bulls", "Racing Bulls", "Red Bull Ford", 
                         83, 86, 86, 84, 84, 93,
                         active_aero=82, energy_recovery=85, budget_cap_efficiency=82),
    
    "audi": Team("Audi", "Audi", "Audi", 
                 82, 80, 85, 88, 83, 85,
                 active_aero=86, energy_recovery=88, budget_cap_efficiency=90),
    
    "haas": Team("Haas", "Haas", "Ferrari", 
                 81, 82, 82, 81, 82, 96,
                 active_aero=80, energy_recovery=81, budget_cap_efficiency=78),
    
    "cadillac": Team("Cadillac", "Cadillac", "Cadillac", 
                     78, 77, 80, 82, 79, 80,
                     active_aero=77, energy_recovery=78, budget_cap_efficiency=85)
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