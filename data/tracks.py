"""
Module containing data for F1 2026 tracks with their attributes and statistics.
Updated for the 2026 season calendar.
"""

class Track:
    def __init__(self, name, country, city, length_km, laps, corners, 
                 straight_count, top_speed, downforce_level, tyre_wear, 
                 braking_severity, overtaking_difficulty, date,
                 active_aero_advantage=5, energy_demand=5):
        self.name = name
        self.country = country
        self.city = city
        self.length_km = length_km  # Circuit length in km
        self.laps = laps  # Number of laps in the race
        self.corners = corners  # Number of corners
        self.straight_count = straight_count  # Number of straights
        self.top_speed = top_speed  # Expected top speed in km/h
        self.downforce_level = downforce_level  # Required downforce (1-10) where 10 is maximum
        self.tyre_wear = tyre_wear  # Tyre degradation (1-10) where 10 is highest wear
        self.braking_severity = braking_severity  # Braking intensity (1-10) where 10 is highest
        self.overtaking_difficulty = overtaking_difficulty  # Difficulty to overtake (1-10) where 10 is hardest
        self.date = date  # Race date for 2026 season
        # New 2026 attributes
        self.active_aero_advantage = active_aero_advantage  # How much X-Mode helps (1-10)
        self.energy_demand = energy_demand  # Energy recovery importance (1-10)
    
    def __str__(self):
        return f"{self.name} ({self.country})"
    
    def race_distance(self):
        """Calculate total race distance in km."""
        return self.length_km * self.laps
    
    def track_type(self):
        """Determine track type based on characteristics."""
        if self.downforce_level >= 8:
            return "High Downforce"
        elif self.downforce_level <= 4:
            return "Low Downforce"
        else:
            return "Medium Downforce"
    
    def track_summary(self):
        """Return a summary of track characteristics."""
        return {
            "name": self.name,
            "country": self.country,
            "length": self.length_km,
            "laps": self.laps,
            "corners": self.corners,
            "type": self.track_type(),
            "top_speed": self.top_speed,
            "tyre_wear": self.tyre_wear,
            "overtaking": 10 - self.overtaking_difficulty,  # Convert to overtaking potential (10 is best)
            "active_aero_advantage": self.active_aero_advantage,
            "energy_demand": self.energy_demand,
            "date": self.date
        }


# 2026 F1 Calendar with track data
# Updated for the 2026 season with official calendar from formula1.com
# Note: Imola removed from 2026 calendar, Spain has 2 races (Barcelona-Catalunya + Madrid)
TRACKS = {
    "australia": Track("Albert Park Circuit", "Australia", "Melbourne", 5.278, 58, 14, 4, 325, 5, 6, 7, 5, 
                       "March 6-8, 2026", active_aero_advantage=6, energy_demand=6),
    "china": Track("Shanghai International Circuit", "China", "Shanghai", 5.451, 56, 16, 3, 327, 6, 7, 8, 5, 
                   "March 13-15, 2026", active_aero_advantage=7, energy_demand=7),
    "japan": Track("Suzuka Circuit", "Japan", "Suzuka", 5.807, 53, 18, 2, 315, 9, 6, 7, 7, 
                   "March 27-29, 2026", active_aero_advantage=5, energy_demand=6),
    "bahrain": Track("Bahrain International Circuit", "Bahrain", "Sakhir", 5.412, 57, 15, 4, 330, 6, 7, 7, 5, 
                     "April 10-12, 2026", active_aero_advantage=7, energy_demand=8),
    "saudi_arabia": Track("Jeddah Corniche Circuit", "Saudi Arabia", "Jeddah", 6.174, 50, 27, 3, 350, 4, 5, 8, 6, 
                          "April 17-19, 2026", active_aero_advantage=8, energy_demand=6),
    "miami": Track("Miami International Autodrome", "USA", "Miami", 5.412, 57, 19, 3, 340, 5, 6, 7, 4, 
                   "May 1-3, 2026", active_aero_advantage=7, energy_demand=6),
    "canada": Track("Circuit Gilles Villeneuve", "Canada", "Montreal", 4.361, 70, 14, 3, 330, 6, 8, 8, 4, 
                    "May 22-24, 2026", active_aero_advantage=8, energy_demand=9),
    "monaco": Track("Circuit de Monaco", "Monaco", "Monte Carlo", 3.337, 78, 19, 1, 290, 10, 3, 10, 10, 
                    "June 5-7, 2026", active_aero_advantage=2, energy_demand=8),
    "barcelona": Track("Circuit de Barcelona-Catalunya", "Spain", "Barcelona", 4.675, 66, 16, 2, 325, 8, 7, 6, 7, 
                       "June 12-14, 2026", active_aero_advantage=5, energy_demand=6),
    "austria": Track("Red Bull Ring", "Austria", "Spielberg", 4.318, 71, 10, 3, 340, 5, 6, 7, 3, 
                     "June 26-28, 2026", active_aero_advantage=9, energy_demand=7),
    "britain": Track("Silverstone Circuit", "Great Britain", "Silverstone", 5.891, 52, 18, 2, 330, 8, 7, 7, 5, 
                     "July 3-5, 2026", active_aero_advantage=6, energy_demand=6),
    "belgium": Track("Circuit de Spa-Francorchamps", "Belgium", "Spa", 7.004, 44, 19, 2, 350, 6, 5, 9, 4, 
                     "July 17-19, 2026", active_aero_advantage=8, energy_demand=5),
    "hungary": Track("Hungaroring", "Hungary", "Budapest", 4.381, 70, 14, 1, 315, 9, 5, 7, 9, 
                     "July 24-26, 2026", active_aero_advantage=3, energy_demand=7),
    "netherlands": Track("Circuit Zandvoort", "Netherlands", "Zandvoort", 4.259, 72, 14, 2, 315, 8, 7, 7, 7, 
                         "August 21-23, 2026", active_aero_advantage=4, energy_demand=6),
    "monza": Track("Autodromo Nazionale Monza", "Italy", "Monza", 5.793, 53, 11, 4, 360, 1, 8, 9, 4, 
                   "September 4-6, 2026", active_aero_advantage=10, energy_demand=5),
    "spain": Track("Madrid Street Circuit", "Spain", "Madrid", 5.473, 56, 18, 3, 335, 5, 6, 7, 5, 
                   "September 11-13, 2026", active_aero_advantage=7, energy_demand=6),
    "azerbaijan": Track("Baku City Circuit", "Azerbaijan", "Baku", 6.003, 51, 20, 2, 350, 4, 5, 8, 6, 
                        "September 24-26, 2026", active_aero_advantage=9, energy_demand=6),
    "singapore": Track("Marina Bay Street Circuit", "Singapore", "Singapore", 4.94, 62, 23, 2, 325, 8, 9, 9, 7, 
                       "October 9-11, 2026", active_aero_advantage=4, energy_demand=8),
    "usa": Track("Circuit of the Americas", "USA", "Austin", 5.513, 56, 20, 3, 330, 7, 6, 7, 5, 
                 "October 23-25, 2026", active_aero_advantage=7, energy_demand=6),
    "mexico": Track("Autódromo Hermanos Rodríguez", "Mexico", "Mexico City", 4.304, 71, 17, 3, 350, 6, 7, 8, 6, 
                    "October 30-November 1, 2026", active_aero_advantage=8, energy_demand=7),
    "brazil": Track("Autódromo José Carlos Pace", "Brazil", "São Paulo", 4.309, 71, 15, 2, 335, 7, 8, 7, 4, 
                    "November 6-8, 2026", active_aero_advantage=7, energy_demand=6),
    "las_vegas": Track("Las Vegas Strip Circuit", "USA", "Las Vegas", 6.12, 50, 17, 3, 345, 3, 6, 7, 5, 
                       "November 19-21, 2026", active_aero_advantage=9, energy_demand=5),
    "qatar": Track("Losail International Circuit", "Qatar", "Lusail", 5.38, 57, 16, 1, 330, 8, 9, 7, 6, 
                   "November 27-29, 2026", active_aero_advantage=5, energy_demand=7),
    "abu_dhabi": Track("Yas Marina Circuit", "UAE", "Abu Dhabi", 5.281, 58, 16, 2, 335, 7, 6, 7, 7, 
                       "December 4-6, 2026", active_aero_advantage=7, energy_demand=6)
}

def get_track_by_name(name):
    """Get a track by its full or partial name."""
    name = name.lower()
    for track_id, track in TRACKS.items():
        if name in track.name.lower() or name in track.country.lower():
            return track
    return None

def get_all_tracks():
    """Return all tracks."""
    return list(TRACKS.values())

def get_calendar():
    """Return the tracks in calendar order (by date)."""
    import datetime
    
    def parse_date(date_string):
        """Parse date string from format like 'March 13-15, 2026' or 'July 31-August 2, 2026'."""
        import re
        
        # Try to extract month, day, and year
        # Handle format: "March 13-15, 2026" or "July 31-August 2, 2026"
        try:
            # Check for month range format (e.g., "July 31-August 2, 2026")
            month_range_match = re.match(r'(\w+)\s+(\d+)-\w+\s+\d+,\s+(\d{4})', date_string)
            if month_range_match:
                month = month_range_match.group(1)
                day = month_range_match.group(2)
                year = month_range_match.group(3)
                return datetime.datetime.strptime(f"{month} {day} {year}", "%B %d %Y")
            
            # Handle standard format: "March 13-15, 2026"
            standard_match = re.match(r'(\w+)\s+(\d+)-\d+,\s+(\d{4})', date_string)
            if standard_match:
                month = standard_match.group(1)
                day = standard_match.group(2)
                year = standard_match.group(3)
                return datetime.datetime.strptime(f"{month} {day} {year}", "%B %d %Y")
            
            # Fallback: just extract month and year
            parts = date_string.replace(',', '').split()
            if len(parts) >= 2:
                month = parts[0]
                day = parts[1].split('-')[0]
                year = parts[-1]
                return datetime.datetime.strptime(f"{month} {day} {year}", "%B %d %Y")
                
        except (ValueError, IndexError, AttributeError):
            pass
        
        # Final fallback
        return datetime.datetime(2026, 1, 1)
    
    return sorted(TRACKS.values(), key=lambda track: parse_date(track.date))