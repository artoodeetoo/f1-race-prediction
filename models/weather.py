"""
Module for simulating weather conditions for Formula 1 races.
Weather has significant impact on race strategy and performance.
"""

import random
import requests
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class WeatherCondition:
    """Represents weather conditions during a race."""
    condition: str  # 'dry', 'wet', 'mixed'
    temperature: float  # in Celsius
    humidity: float  # percentage
    wind_speed: float  # km/h
    rain_chance: float  # percentage chance of rain
    rain_intensity: float  # 0-10 scale, 0 is no rain, 10 is monsoon
    track_temperature: float  # in Celsius
    
    def __str__(self):
        return f"{self.condition.title()} - {self.temperature}°C, Rain: {int(self.rain_chance)}%"
    
    @property
    def is_wet(self):
        """Check if conditions are wet."""
        return self.condition == 'wet' or (self.condition == 'mixed' and self.rain_intensity > 3)

    @property
    def weather_factor(self):
        """Calculate impact of weather on race conditions.
        Returns a value between 0-1, where 0 is extreme weather impact, 1 is ideal conditions.
        """
        if self.condition == 'dry':
            # Perfect conditions
            if 18 <= self.temperature <= 26 and self.wind_speed < 20:
                return 1.0
            # Very hot or windy
            elif self.temperature > 35 or self.wind_speed > 40:
                return 0.85
            # Cold
            elif self.temperature < 10:
                return 0.9
            # Normal
            else:
                return 0.95
        elif self.condition == 'wet':
            # Heavy rain
            if self.rain_intensity > 7:
                return 0.6
            # Medium rain
            elif 4 <= self.rain_intensity <= 7:
                return 0.7
            # Light rain
            else:
                return 0.8
        else:  # mixed
            # Changing conditions
            base = 0.85
            rain_factor = 0.1 * self.rain_intensity / 10
            return base - rain_factor


# Track coordinates for OpenWeatherMap API
TRACK_COORDINATES = {
    "australia": (-37.8497, 144.9681),  # Albert Park, Melbourne
    "china": (31.3389, 121.2197),      # Shanghai International Circuit
    "japan": (34.8431, 136.5413),      # Suzuka Circuit
    "bahrain": (26.0325, 50.5106),     # Bahrain International Circuit
    "saudi_arabia": (21.6319, 39.1044), # Jeddah Corniche Circuit
    "miami": (25.9581, -80.2389),      # Miami International Autodrome
    "canada": (45.5017, -73.5273),     # Circuit Gilles Villeneuve
    "monaco": (43.7347, 7.4206),       # Circuit de Monaco
    "barcelona": (41.5700, 2.2611),    # Circuit de Barcelona-Catalunya
    "austria": (47.2197, 14.7647),     # Red Bull Ring
    "britain": (52.0786, -1.0169),     # Silverstone Circuit
    "belgium": (50.4372, 5.9714),      # Circuit de Spa-Francorchamps
    "hungary": (47.5789, 19.2486),     # Hungaroring
    "netherlands": (52.3886, 4.5419),  # Circuit Zandvoort
    "monza": (45.6156, 9.2811),        # Autodromo Nazionale Monza
    "spain": (40.4168, -3.7038),       # Madrid Street Circuit
    "azerbaijan": (40.3725, 49.8533),  # Baku City Circuit
    "singapore": (1.2914, 103.8640),   # Marina Bay Street Circuit
    "austin": (30.1328, -97.6411),     # Circuit of the Americas
    "mexico": (19.4042, -99.0907),     # Autodromo Hermanos Rodriguez
    "brazil": (-23.7036, -46.6997),    # Interlagos
    "las_vegas": (36.1147, -115.1728), # Las Vegas Strip Circuit
    "qatar": (25.4901, 51.4542),       # Losail International Circuit
    "abu_dhabi": (24.4672, 54.6031)    # Yas Marina Circuit
}


class WeatherAPIClient:
    """Client for OpenWeatherMap API integration."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def get_race_weekend_forecast(self, track_name, race_date=None):
        """Get weather forecast for race weekend.
        
        Args:
            track_name: Name of the track (key from TRACK_COORDINATES)
            race_date: Optional datetime for the race
            
        Returns:
            Weather data from OpenWeatherMap or None if API unavailable
        """
        if not self.api_key:
            logger.info("OpenWeatherMap API key not found, using simulated weather")
            return None
            
        track_key = self._get_track_key(track_name)
        if track_key not in TRACK_COORDINATES:
            logger.warning(f"No coordinates found for track: {track_name}")
            return None
            
        lat, lon = TRACK_COORDINATES[track_key]
        
        try:
            # Get 5-day forecast (covers race weekend)
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            forecast_data = response.json()
            logger.info(f"Successfully fetched weather forecast for {track_name}")
            return forecast_data
            
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch weather data: {e}")
            return None
    
    def _get_track_key(self, track_name):
        """Convert track name to coordinate key."""
        # Map various track name formats to coordinate keys
        name_mapping = {
            'albert park circuit': 'australia',
            'shanghai international circuit': 'china',
            'suzuka circuit': 'japan',
            'bahrain international circuit': 'bahrain',
            'jeddah corniche circuit': 'saudi_arabia',
            'miami international autodrome': 'miami',
            'circuit gilles villeneuve': 'canada',
            'circuit de monaco': 'monaco',
            'circuit de barcelona-catalunya': 'barcelona',
            'red bull ring': 'austria',
            'silverstone circuit': 'britain',
            'circuit de spa-francorchamps': 'belgium',
            'hungaroring': 'hungary',
            'circuit zandvoort': 'netherlands',
            'autodromo nazionale monza': 'monza',
            'madrid street circuit': 'spain',
            'baku city circuit': 'azerbaijan',
            'marina bay street circuit': 'singapore',
            'circuit of the americas': 'austin',
            'autodromo hermanos rodriguez': 'mexico',
            'autodromo jose carlos pace': 'brazil',
            'las vegas strip circuit': 'las_vegas',
            'losail international circuit': 'qatar',
            'yas marina circuit': 'abu_dhabi'
        }
        
        return name_mapping.get(track_name.lower(), track_name.lower())
    
    def process_forecast_data(self, forecast_data):
        """Process OpenWeatherMap forecast data into race conditions.
        
        Args:
            forecast_data: Raw forecast data from OpenWeatherMap
            
        Returns:
            Dictionary with processed weather information
        """
        if not forecast_data or 'list' not in forecast_data:
            return None
            
        # Get race day forecast (typically Sunday)
        race_day_forecasts = forecast_data['list'][:8]  # Next 24 hours
        
        # Calculate averages for race conditions
        temps = [item['main']['temp'] for item in race_day_forecasts]
        humidity = [item['main']['humidity'] for item in race_day_forecasts]
        wind_speeds = [item['wind']['speed'] * 3.6 for item in race_day_forecasts]  # m/s to km/h
        
        # Check for precipitation
        rain_forecasts = [item.get('rain', {}).get('3h', 0) for item in race_day_forecasts]
        total_rain = sum(rain_forecasts)
        rain_probability = len([r for r in rain_forecasts if r > 0]) / len(rain_forecasts) * 100
        
        return {
            'temperature': sum(temps) / len(temps),
            'humidity': sum(humidity) / len(humidity),
            'wind_speed': sum(wind_speeds) / len(wind_speeds),
            'total_rain': total_rain,
            'rain_probability': rain_probability,
            'conditions': [item['weather'][0]['main'] for item in race_day_forecasts]
        }


def generate_weather_with_api(track, month=None, forced_condition=None):
    """Generate weather using real API data when available.
    
    Args:
        track: Track object
        month: Optional month to override track date
        forced_condition: Optional weather condition to force ('dry', 'wet', 'mixed')
        
    Returns:
        WeatherCondition object enhanced with real API data
    """
    # Try to get real weather data first
    weather_client = WeatherAPIClient()
    forecast_data = weather_client.get_race_weekend_forecast(track.name)
    
    if forecast_data:
        processed_data = weather_client.process_forecast_data(forecast_data)
        if processed_data:
            return _create_weather_from_api_data(processed_data, forced_condition)
    
    # Fallback to simulated weather
    logger.info(f"Using simulated weather for {track.name}")
    return generate_weather(track, month, forced_condition)


def _create_weather_from_api_data(api_data, forced_condition=None):
    """Create WeatherCondition from API data.
    
    Args:
        api_data: Processed weather data from API
        forced_condition: Optional condition override
        
    Returns:
        WeatherCondition object
    """
    # Determine condition based on API data
    if forced_condition:
        condition = forced_condition
    else:
        if api_data['rain_probability'] > 70 or api_data['total_rain'] > 5:
            condition = 'wet'
        elif 30 < api_data['rain_probability'] <= 70 or 0 < api_data['total_rain'] <= 5:
            condition = 'mixed'
        else:
            condition = 'dry'
    
    # Calculate rain intensity from API data
    if condition == 'wet':
        rain_intensity = min(10, max(3, api_data['total_rain']))
    elif condition == 'mixed':
        rain_intensity = min(6, max(1, api_data['total_rain'] * 2))
    else:
        rain_intensity = 0
    
    # Track temperature estimate
    air_temp = api_data['temperature']
    track_temp_bonus = 15 if condition == 'dry' else 5
    track_temp = air_temp + track_temp_bonus + random.uniform(-2, 2)
    
    return WeatherCondition(
        condition=condition,
        temperature=round(air_temp, 1),
        humidity=round(api_data['humidity'], 1),
        wind_speed=round(api_data['wind_speed'], 1),
        rain_chance=round(api_data['rain_probability'], 1),
        rain_intensity=round(rain_intensity, 1),
        track_temperature=round(track_temp, 1)
    )


def generate_weather(track, month=None, forced_condition=None):
    """Generate realistic weather conditions for a given track (original simulation).
    
    Args:
        track: Track object
        month: Optional month to override track date
        forced_condition: Optional weather condition to force ('dry', 'wet', 'mixed')
        
    Returns:
        WeatherCondition object
    """
    if month is None:
        # Extract month from track date
        import datetime
        import re
        
        # Handle date format like "April 4-6, 2025"
        # Extract just the month name using regex
        month_match = re.match(r'(\w+)\s+\d+', track.date)
        if month_match:
            month_name = month_match.group(1)
            # Convert month name to month number
            month_dict = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            month = month_dict.get(month_name, datetime.datetime.now().month)
        else:
            # Fallback to current month if parsing fails
            month = datetime.datetime.now().month
    
    # Weather probabilities based on location and month
    if forced_condition:
        condition = forced_condition
    else:
        # Default probabilities
        dry_prob = 0.7
        wet_prob = 0.2
        mixed_prob = 0.1
        
        # Adjust for certain tracks/seasons known for rain
        if track.country.lower() in ["malaysia", "japan", "brazil", "belgium", "great britain", "singapore"]:
            dry_prob -= 0.2
            wet_prob += 0.1
            mixed_prob += 0.1
            
        # Adjust for season (more rain in certain months)
        if month in [3, 4, 10, 11]:  # Spring and autumn months
            dry_prob -= 0.1
            wet_prob += 0.05
            mixed_prob += 0.05
            
        # Choose condition based on probabilities
        conditions = ['dry', 'wet', 'mixed']
        probabilities = [dry_prob, wet_prob, mixed_prob]
        condition = random.choices(conditions, weights=probabilities, k=1)[0]
    
    # Base temperature on month and location
    base_temp = 22  # Default base temperature
    
    # Adjust for season
    season_adj = {
        1: -5, 2: -4, 3: -2, 4: 0,     # Winter/Spring
        5: 3, 6: 5, 7: 7, 8: 7,        # Summer
        9: 4, 10: 0, 11: -3, 12: -5    # Autumn/Winter
    }
    
    # Adjust for location (rough approximations)
    location_adj = 0
    if track.country.lower() in ["bahrain", "saudi arabia", "qatar", "uae", "singapore"]:
        location_adj = 8  # Hot locations
    elif track.country.lower() in ["canada", "japan", "great britain", "belgium"]:
        location_adj = -3  # Cooler locations
        
    # Calculate temperature with some randomness
    temp_base = base_temp + season_adj[month] + location_adj
    temperature = round(temp_base + random.uniform(-3, 3), 1)
    
    # Generate other weather parameters
    if condition == 'dry':
        humidity = random.uniform(40, 70)
        wind_speed = random.uniform(0, 25)
        rain_chance = random.uniform(0, 15)
        rain_intensity = 0
        track_temp = temperature + random.uniform(10, 20)
    elif condition == 'wet':
        humidity = random.uniform(70, 95)
        wind_speed = random.uniform(5, 40)
        rain_chance = random.uniform(70, 100)
        rain_intensity = random.uniform(3, 10)
        track_temp = temperature + random.uniform(0, 7)
    else:  # mixed
        humidity = random.uniform(60, 85)
        wind_speed = random.uniform(3, 35)
        rain_chance = random.uniform(40, 80)
        rain_intensity = random.uniform(1, 6)
        track_temp = temperature + random.uniform(5, 15)
        
    return WeatherCondition(
        condition=condition,
        temperature=round(temperature, 1),
        humidity=round(humidity, 1),
        wind_speed=round(wind_speed, 1),
        rain_chance=round(rain_chance, 1),
        rain_intensity=round(rain_intensity, 1),
        track_temperature=round(track_temp, 1)
    )


# Main function that chooses between API and simulated weather
def get_race_weather(track, month=None, forced_condition=None, use_api=True):
    """Get race weather using API when available, fallback to simulation.
    
    Args:
        track: Track object
        month: Optional month override
        forced_condition: Force specific condition
        use_api: Whether to try API first (default: True)
        
    Returns:
        WeatherCondition object
    """
    if use_api:
        return generate_weather_with_api(track, month, forced_condition)
    else:
        return generate_weather(track, month, forced_condition)