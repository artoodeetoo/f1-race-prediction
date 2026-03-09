"""
Web Scraper for 2026 F1 Qualifying Results.

This module scrapes actual 2026 qualifying results from racing news websites
to inject into race predictions for maximum accuracy.
"""

import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from models.live_qualifying_injector import QualifyingResult, LiveQualifyingInjector

logger = logging.getLogger(__name__)

@dataclass
class ScrapingSource:
    """Configuration for a racing news website."""
    name: str
    base_url: str
    pattern: str  # URL pattern for qualifying results
    selectors: Dict[str, str]  # CSS selectors for data extraction

class QualifyingScraper:
    """Scrape qualifying results from racing websites."""
    
    # Supported sources
    SOURCES = {
        'racingnews365': ScrapingSource(
            name='Racing News 365',
            base_url='https://racingnews365.com',
            pattern='/2026-f1-{track}-qualifying-results',
            selectors={
                'table': 'table.results-table, .qualifying-results table, table',
                'rows': 'tbody tr, tr',
                'position': 'td:first-child, .position',
                'driver': 'td:nth-child(2), .driver-name',
                'team': 'td:nth-child(3), .team-name',
                'time': 'td:nth-child(4), .time, .best-time'
            }
        ),
        'formula1': ScrapingSource(
            name='Formula1.com',
            base_url='https://www.formula1.com',
            pattern='/en/results/2026/races/{race_id}/qualifying.html',
            selectors={
                'table': '.resultsarchive-table',
                'rows': 'tbody tr',
                'position': 'td:nth-child(2)',
                'driver': 'td:nth-child(4)',
                'team': 'td:nth-child(5)',
                'time': 'td:nth-child(6)'
            }
        ),
        'motorsport': ScrapingSource(
            name='Motorsport.com',
            base_url='https://www.motorsport.com',
            pattern='/f1/results/2026/{track}-qualifying-results',
            selectors={
                'table': '.ms-table',
                'rows': 'tbody tr',
                'position': 'td:nth-child(1)',
                'driver': 'td:nth-child(2)',
                'team': 'td:nth-child(3)',
                'time': 'td:nth-child(4)'
            }
        )
    }
    
    TRACK_NAME_MAPPING = {
        # Map your track names to website URL formats
        'albert park circuit': 'australian-grand-prix',
        'shanghai international circuit': 'chinese-grand-prix',
        'suzuka circuit': 'japanese-grand-prix',
        'bahrain international circuit': 'bahrain-grand-prix',
        'jeddah corniche circuit': 'saudi-arabian-grand-prix',
        'miami international autodrome': 'miami-grand-prix',
        'circuit gilles villeneuve': 'canadian-grand-prix',
        'circuit de monaco': 'monaco-grand-prix',
        'circuit de barcelona-catalunya': 'spanish-grand-prix',
        'red bull ring': 'austrian-grand-prix',
        'silverstone circuit': 'british-grand-prix',
        'circuit de spa-francorchamps': 'belgian-grand-prix',
        'hungaroring': 'hungarian-grand-prix',
        'circuit zandvoort': 'dutch-grand-prix',
        'autodromo nazionale monza': 'italian-grand-prix',
        'madrid street circuit': 'madrid-grand-prix',
        'baku city circuit': 'azerbaijan-grand-prix',
        'marina bay street circuit': 'singapore-grand-prix',
        'circuit of the americas': 'united-states-grand-prix',
        'autodromo hermanos rodriguez': 'mexico-city-grand-prix',
        'autodromo jose carlos pace': 'brazil-grand-prix',
        'las vegas strip circuit': 'las-vegas-grand-prix',
        'losail international circuit': 'qatar-grand-prix',
        'yas marina circuit': 'abu-dhabi-grand-prix'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.injector = LiveQualifyingInjector()
    
    def scrape_qualifying_results(self, track_name: str, source: str = 'racingnews365') -> Optional[List[QualifyingResult]]:
        """Scrape qualifying results from specified source."""
        if source not in self.SOURCES:
            logger.error(f"Unsupported source: {source}")
            return None
        
        source_config = self.SOURCES[source]
        url = self._build_url(track_name, source_config)
        
        if not url:
            logger.error(f"Could not build URL for {track_name} on {source}")
            return None
        
        try:
            logger.info(f"Scraping qualifying results from: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._parse_qualifying_table(soup, source_config)
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping qualifying results: {e}")
            return None
    
    def _build_url(self, track_name: str, source: ScrapingSource) -> Optional[str]:
        """Build URL for qualifying results."""
        track_key = track_name.lower()
        
        if track_key not in self.TRACK_NAME_MAPPING:
            # Try to find partial match
            for key, value in self.TRACK_NAME_MAPPING.items():
                if track_key in key or key in track_key:
                    track_key = key
                    break
            else:
                return None
        
        race_slug = self.TRACK_NAME_MAPPING[track_key]
        
        if source.name == 'Racing News 365':
            return source.base_url + source.pattern.format(track=race_slug)
        elif source.name == 'Formula1.com':
            # F1.com uses race IDs - would need mapping
            return None  # Implement if needed
        elif source.name == 'Motorsport.com':
            return source.base_url + source.pattern.format(track=race_slug)
        
        return None
    
    def _parse_qualifying_table(self, soup: BeautifulSoup, source: ScrapingSource) -> List[QualifyingResult]:
        """Parse qualifying results table from HTML."""
        results = []
        
        # Find the results table
        table = soup.select_one(source.selectors['table'])
        if not table:
            logger.error("Could not find qualifying results table")
            return results
        
        # Find all result rows
        rows = table.select(source.selectors['rows'])
        
        for row in rows:
            try:
                # Extract position
                pos_elem = row.select_one(source.selectors['position'])
                if not pos_elem:
                    continue
                
                position_text = pos_elem.get_text().strip()
                position = self._extract_position(position_text)
                if position is None:
                    continue
                
                # Extract driver name
                driver_elem = row.select_one(source.selectors['driver'])
                if not driver_elem:
                    continue
                driver_name = self._clean_driver_name(driver_elem.get_text().strip())
                
                # Extract team name
                team_elem = row.select_one(source.selectors['team'])
                team_name = team_elem.get_text().strip() if team_elem else ""
                team_name = self._clean_team_name(team_name)
                
                # Extract time
                time_elem = row.select_one(source.selectors['time'])
                if not time_elem:
                    continue
                
                time_text = time_elem.get_text().strip()
                lap_time = self._clean_lap_time(time_text)
                
                if lap_time and position <= 22:  # Valid F1 grid position
                    result = QualifyingResult(
                        position=position,
                        driver_name=driver_name,
                        team_name=team_name,
                        best_time=lap_time
                    )
                    results.append(result)
                    
            except Exception as e:
                logger.debug(f"Error parsing row: {e}")
                continue
        
        logger.info(f"Scraped {len(results)} qualifying results")
        return sorted(results, key=lambda x: x.position)
    
    def _extract_position(self, position_text: str) -> Optional[int]:
        """Extract position number from text."""
        # Remove common prefixes/suffixes
        position_text = position_text.replace('P', '').replace('#', '').strip()
        
        # Extract first number
        match = re.search(r'(\d+)', position_text)
        if match:
            pos = int(match.group(1))
            return pos if 1 <= pos <= 22 else None
        
        return None\n    \n    def _clean_driver_name(self, name: str) -> str:\n        \"\"\"Clean and normalize driver name.\"\"\"\n        # Remove common prefixes/suffixes\n        name = re.sub(r'^\\d+\\.?\\s*', '', name)  # Remove position numbers\n        name = re.sub(r'\\s*\\([^)]*\\)', '', name)  # Remove parentheses content\n        \n        # Handle \"SURNAME First Name\" format\n        parts = name.split()\n        if len(parts) >= 2 and parts[0].isupper() and len(parts[0]) > 2:\n            # Likely \"VERSTAPPEN Max\" format\n            name = f\"{parts[1]} {parts[0].title()}\"\n        \n        return name.strip()\n    \n    def _clean_team_name(self, team: str) -> str:\n        \"\"\"Clean and normalize team name.\"\"\"\n        # Common team name mappings\n        team_mappings = {\n            'red bull racing': 'Red Bull Racing',\n            'mclaren': 'McLaren',\n            'ferrari': 'Ferrari',\n            'mercedes': 'Mercedes',\n            'aston martin': 'Aston Martin',\n            'alpine': 'Alpine',\n            'williams': 'Williams',\n            'alphatauri': 'AlphaTauri',\n            'alfa romeo': 'Alfa Romeo',\n            'haas': 'Haas',\n            'audi': 'Audi',  # 2026 new entry\n            'cadillac': 'Cadillac'  # 2026 new entry\n        }\n        \n        team_lower = team.lower().strip()\n        for key, value in team_mappings.items():\n            if key in team_lower:\n                return value\n        \n        return team.strip()\n    \n    def _clean_lap_time(self, time_text: str) -> Optional[str]:\n        \"\"\"Extract and clean lap time.\"\"\"\n        # Remove extra whitespace and common prefixes\n        time_text = time_text.strip()\n        \n        # Skip if it's clearly not a time\n        if any(word in time_text.lower() for word in ['dnf', 'dns', 'dsq', 'nc', 'retired']):\n            return None\n        \n        # Extract time pattern: M:SS.SSS\n        time_match = re.search(r'(\\d{1,2}):(\\d{2})\\.(\\d{3})', time_text)\n        if time_match:\n            minutes, seconds, milliseconds = time_match.groups()\n            return f\"{minutes}:{seconds}.{milliseconds}\"\n        \n        # Try without milliseconds: M:SS\n        time_match = re.search(r'(\\d{1,2}):(\\d{2})', time_text)\n        if time_match:\n            minutes, seconds = time_match.groups()\n            return f\"{minutes}:{seconds}.000\"\n        \n        return None\n    \n    def auto_scrape_and_inject(self, track_name: str, drivers: List) -> bool:\n        \"\"\"Automatically scrape and inject qualifying results.\"\"\"\n        print(f\"\\n🔍 Searching for actual {track_name} qualifying results...\")\n        \n        # Try different sources\n        for source_name in ['racingnews365', 'motorsport']:\n            try:\n                results = self.scrape_qualifying_results(track_name, source_name)\n                \n                if results and len(results) >= 10:  # At least top 10\n                    print(f\"✅ Found qualifying results on {source_name}\")\n                    print(f\"📊 Top 3: P1-{results[0].driver_name}, P2-{results[1].driver_name}, P3-{results[2].driver_name}\")\n                    \n                    # Save results\n                    self.injector.save_qualifying_results(track_name, results)\n                    \n                    return self._inject_results_into_drivers(results, drivers)\n                    \n            except Exception as e:\n                logger.debug(f\"Failed to scrape from {source_name}: {e}\")\n                continue\n        \n        print(f\"❌ Could not find qualifying results for {track_name}\")\n        return False\n    \n    def _inject_results_into_drivers(self, results: List[QualifyingResult], drivers: List) -> List:\n        \"\"\"Convert scraped results to driver objects in grid order.\"\"\"\n        driver_map = {self._normalize_name(d.name): d for d in drivers}\n        grid_order = []\n        \n        # Match scraped results to driver objects\n        for result in sorted(results, key=lambda x: x.position):\n            normalized_name = self._normalize_name(result.driver_name)\n            \n            # Try exact match first\n            if normalized_name in driver_map:\n                grid_order.append(driver_map[normalized_name])\n                continue\n            \n            # Try fuzzy matching\n            matched = False\n            for driver_key, driver_obj in driver_map.items():\n                if self._names_match(normalized_name, driver_key):\n                    grid_order.append(driver_obj)\n                    matched = True\n                    break\n            \n            if not matched:\n                logger.warning(f\"Could not match scraped driver: {result.driver_name}\")\n        \n        # Add any remaining drivers not in results\n        remaining_drivers = [d for d in drivers if d not in grid_order]\n        grid_order.extend(remaining_drivers)\n        \n        return grid_order[:len(drivers)]\n    \n    def _normalize_name(self, name: str) -> str:\n        \"\"\"Normalize name for matching.\"\"\"\n        return name.lower().replace('-', ' ').replace('.', '').strip()\n    \n    def _names_match(self, name1: str, name2: str) -> bool:\n        \"\"\"Check if two names likely refer to the same person.\"\"\"\n        name1_parts = name1.split()\n        name2_parts = name2.split()\n        \n        # Check if last names match\n        if name1_parts[-1] == name2_parts[-1]:\n            return True\n        \n        # Check if first name + first letter of last name match\n        if (len(name1_parts) >= 2 and len(name2_parts) >= 2 and \n            name1_parts[0] == name2_parts[0] and \n            name1_parts[-1][0] == name2_parts[-1][0]):\n            return True\n        \n        return False"}