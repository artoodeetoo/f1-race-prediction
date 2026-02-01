"""
Module containing data for F1 2026 drivers with their attributes and statistics.
Updated for the 2026 season with new regulations and team changes.
"""

class Driver:
    def __init__(self, name, team, number, nationality, age, experience, 
                 skill_wet, skill_dry, skill_overtaking, consistency, aggression,
                 tire_management=80, racecraft=80, qualifying_pace=80):
        self.name = name
        self.team = team
        self.number = number
        self.nationality = nationality
        self.age = age
        self.experience = experience  # Years in F1
        self.skill_wet = skill_wet  # Performance in wet conditions (1-100)
        self.skill_dry = skill_dry  # Performance in dry conditions (1-100)
        self.skill_overtaking = skill_overtaking  # Overtaking ability (1-100)
        self.consistency = consistency  # Consistency during race (1-100)
        self.aggression = aggression  # Aggressive driving style (1-100)
        # New attributes for 2026
        self.tire_management = tire_management  # Tire preservation skill (1-100)
        self.racecraft = racecraft  # Wheel-to-wheel racing ability (1-100)
        self.qualifying_pace = qualifying_pace  # Single lap speed (1-100)
        
    def __str__(self):
        return f"{self.name} ({self.team})"
    
    def get_overall_rating(self):
        """Calculate the overall driver rating based on their skills."""
        return (self.skill_dry * 0.25 + 
                self.skill_wet * 0.10 + 
                self.skill_overtaking * 0.15 + 
                self.consistency * 0.15 + 
                self.tire_management * 0.10 +
                self.racecraft * 0.10 +
                self.qualifying_pace * 0.10 +
                min(self.experience * 0.5, 5))  # Experience capped contribution
    
    def get_race_rating(self):
        """Calculate race-specific rating."""
        return (self.skill_dry * 0.30 +
                self.consistency * 0.25 +
                self.tire_management * 0.20 +
                self.racecraft * 0.15 +
                self.skill_overtaking * 0.10)
    
    def get_qualifying_rating(self):
        """Calculate qualifying-specific rating."""
        return (self.qualifying_pace * 0.40 +
                self.skill_dry * 0.35 +
                self.consistency * 0.15 +
                self.aggression * 0.10)


# 2026 F1 Drivers with realistic attributes
# Data is based on 2026 season - new regulations era
# Official lineup from formula1.com
# Note: 2026 brings major regulation changes (new power units, active aero)
DRIVERS = {
    # Red Bull Racing - Verstappen with rookie Hadjar
    "verstappen": Driver("Max Verstappen", "Red Bull Racing", 1, "Dutch", 29, 12, 
                         95, 97, 94, 93, 86, tire_management=91, racecraft=96, qualifying_pace=97),
    "hadjar": Driver("Isack Hadjar", "Red Bull Racing", 6, "French", 21, 2, 
                     83, 85, 82, 78, 81, tire_management=76, racecraft=80, qualifying_pace=86),
    
    # Ferrari - Hamilton's second year with Leclerc
    "leclerc": Driver("Charles Leclerc", "Ferrari", 16, "Monegasque", 29, 9, 
                      90, 92, 89, 86, 83, tire_management=87, racecraft=90, qualifying_pace=94),
    "hamilton": Driver("Lewis Hamilton", "Ferrari", 44, "British", 41, 20, 
                       93, 94, 91, 90, 76, tire_management=95, racecraft=96, qualifying_pace=92),
    
    # Mercedes - Russell leads with young Antonelli
    "russell": Driver("George Russell", "Mercedes", 63, "British", 28, 7, 
                      91, 93, 90, 89, 82, tire_management=88, racecraft=89, qualifying_pace=93),
    "antonelli": Driver("Kimi Antonelli", "Mercedes", 12, "Italian", 20, 2, 
                        88, 90, 86, 83, 84, tire_management=80, racecraft=85, qualifying_pace=91),
    
    # McLaren - Defending champions
    "norris": Driver("Lando Norris", "McLaren", 4, "British", 27, 8, 
                     94, 96, 93, 94, 85, tire_management=90, racecraft=93, qualifying_pace=95),
    "piastri": Driver("Oscar Piastri", "McLaren", 81, "Australian", 25, 4, 
                      91, 93, 90, 91, 84, tire_management=89, racecraft=91, qualifying_pace=92),
    
    # Aston Martin - Honda power unit partnership
    "alonso": Driver("Fernando Alonso", "Aston Martin", 14, "Spanish", 45, 25, 
                     92, 93, 90, 88, 87, tire_management=94, racecraft=95, qualifying_pace=89),
    "stroll": Driver("Lance Stroll", "Aston Martin", 18, "Canadian", 28, 11, 
                     80, 82, 78, 77, 74, tire_management=76, racecraft=77, qualifying_pace=80),
    
    # Alpine - Gasly with Colapinto
    "gasly": Driver("Pierre Gasly", "Alpine", 10, "French", 30, 10, 
                    84, 86, 84, 82, 80, tire_management=82, racecraft=84, qualifying_pace=86),
    "colapinto": Driver("Franco Colapinto", "Alpine", 43, "Argentine", 22, 2, 
                        80, 82, 79, 76, 78, tire_management=75, racecraft=78, qualifying_pace=83),
    
    # Audi (formerly Sauber) - Factory Audi entry
    "hulkenberg": Driver("Nico Hulkenberg", "Audi", 27, "German", 39, 14, 
                         84, 86, 83, 85, 78, tire_management=86, racecraft=84, qualifying_pace=84),
    "bortoleto": Driver("Gabriel Bortoleto", "Audi", 5, "Brazilian", 22, 2, 
                        80, 82, 79, 76, 77, tire_management=75, racecraft=78, qualifying_pace=83),
    
    # Cadillac - New F1 team entry for 2026
    "perez": Driver("Sergio Perez", "Cadillac", 11, "Mexican", 36, 16, 
                    85, 87, 83, 82, 75, tire_management=88, racecraft=85, qualifying_pace=84),
    "bottas": Driver("Valtteri Bottas", "Cadillac", 77, "Finnish", 37, 14, 
                     84, 86, 80, 85, 72, tire_management=87, racecraft=82, qualifying_pace=86),
    
    # Racing Bulls (VCARB) - Red Bull junior team
    "lawson": Driver("Liam Lawson", "Racing Bulls", 30, "New Zealander", 24, 3, 
                     82, 84, 82, 80, 80, tire_management=78, racecraft=82, qualifying_pace=84),
    "lindblad": Driver("Arvid Lindblad", "Racing Bulls", 17, "British", 18, 1, 
                       79, 81, 78, 75, 80, tire_management=73, racecraft=77, qualifying_pace=82),
    
    # Williams - Mercedes power
    "sainz": Driver("Carlos Sainz", "Williams", 55, "Spanish", 32, 12, 
                    89, 91, 88, 90, 79, tire_management=90, racecraft=89, qualifying_pace=90),
    "albon": Driver("Alexander Albon", "Williams", 23, "Thai", 30, 8, 
                    85, 87, 83, 84, 78, tire_management=86, racecraft=85, qualifying_pace=85),
    
    # Haas - Ferrari power
    "ocon": Driver("Esteban Ocon", "Haas", 31, "French", 30, 10, 
                   85, 86, 84, 83, 81, tire_management=82, racecraft=83, qualifying_pace=84),
    "bearman": Driver("Oliver Bearman", "Haas", 87, "British", 21, 2, 
                      82, 85, 82, 79, 83, tire_management=77, racecraft=80, qualifying_pace=84)
}

def get_driver_by_name(name):
    """Get a driver by their full or partial name."""
    name = name.lower()
    for driver_id, driver in DRIVERS.items():
        if name in driver.name.lower():
            return driver
    return None

def get_all_drivers():
    """Return all drivers."""
    return list(DRIVERS.values())

def get_drivers_by_team(team_name):
    """Get all drivers from a specific team."""
    team_name = team_name.lower()
    return [driver for driver in DRIVERS.values() if team_name in driver.team.lower()]