"""
Formula 1 Race Prediction Simulator
Main application entry point for simulating F1 race outcomes.

This application simulates F1 race results based on:
- Driver statistics and skills
- Team/car performance
- Track characteristics
- Weather conditions
"""

import os
import sys
from tabulate import tabulate as tabulate_func  # Import and rename for clarity

# Load environment variables for API keys
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
except ImportError:
    # dotenv not installed, environment variables should be set manually
    pass

# Setup comprehensive Fast-F1 logging suppression before any other imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
from loading_screen import setup_global_logging_suppression
setup_global_logging_suppression()

# Import our data models
from data.drivers import get_all_drivers, get_driver_by_name
from data.teams import get_all_teams, get_team_by_name
from data.tracks import get_all_tracks, get_track_by_name, get_calendar
from data.real_data_integration import real_data_enhancer

# Import our simulation models
from models.race_model import RaceSimulator
from models.enhanced_race_model import create_enhanced_simulator
from models.weather import generate_weather, get_race_weather
from models.strategy import TireCompound, get_tire_strategy

# Import visualization and stats utilities
from utils.visualization import (
    display_race_header, display_qualifying_results, display_race_results,
    plot_race_progress, simulate_live_race_progress
)
from utils.visualization_graphs import (
    plot_tire_degradation, plot_lap_time_progression,
    plot_driver_comparison, plot_team_performance,
    generate_all_visualizations
)
from utils.stats import SeasonStats, analyze_qualifying_performance, calculate_performance_metrics
from utils.loading_screen import show_data_loading_screen, suppress_fastf1_logging, loading_with_animation


def print_welcome():
    """Print welcome message with app information."""
    print("\n" + "=" * 80)
    print("FORMULA 1 RACE PREDICTION SIMULATOR - 2026 SEASON")
    print("=" * 80)
    print("This application simulates F1 race outcomes based on driver skills, car performance,")
    print("track characteristics, and variable weather conditions.")
    print("\n🏎️  2026 REGULATION CHANGES:")
    print("  • New power units with 350kW MGU-K")
    print("  • Active aerodynamics (X-Mode replaces DRS)")
    print("  • 100% sustainable fuels")
    print("  • Audi enters as factory team")
    print("\nAll data is fictional and represents a hypothetical 2026 F1 season.")
    print("=" * 80 + "\n")


def select_track():
    """Prompt user to select a track from the 2026 calendar."""
    tracks = get_calendar()
    
    print("\nAvailable races in the 2026 F1 Calendar:")
    print("-" * 60)
    
    table_data = []
    for i, track in enumerate(tracks, 1):
        table_data.append([i, track.name, track.country, track.date])
    
    headers = ["Option", "Circuit", "Country", "Race Date"]
    print(tabulate_func(table_data, headers=headers, tablefmt="pipe"))
    
    while True:
        try:
            choice = input("\nSelect a race by number (or 'q' to quit): ")
            if choice.lower() == 'q':
                sys.exit(0)
                
            choice = int(choice)
            if 1 <= choice <= len(tracks):
                return tracks[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(tracks)}")
        except ValueError:
            print("Please enter a valid number")


def select_weather_option(track):
    """Allow user to choose weather options."""
    # Check if API key is available
    has_api_key = bool(os.getenv('OPENWEATHER_API_KEY'))
    
    print("\nChoose weather conditions for the race:")
    if has_api_key:
        print("1. Real Weather Forecast (using OpenWeatherMap API)")
        print("2. Realistic Simulation (based on track location and season)")
        print("3. Dry race")
        print("4. Wet race")
        print("5. Mixed conditions")
        max_option = 5
    else:
        print("ℹ️  Note: Set OPENWEATHER_API_KEY in .env for real weather forecasts")
        print("1. Realistic (based on track location and season)")
        print("2. Dry race")
        print("3. Wet race")
        print("4. Mixed conditions")
        max_option = 4
    
    while True:
        choice = input(f"\nSelect an option (1-{max_option}): ")
        
        # Strip any whitespace and check if it's a digit
        choice = choice.strip()
        if choice.isdigit():
            choice_num = int(choice)
            
            if has_api_key:
                if choice_num == 1:
                    print("🌤️  Fetching real weather forecast...")
                    return get_race_weather(track, use_api=True)
                elif choice_num == 2:
                    return get_race_weather(track, use_api=False)
                elif choice_num == 3:
                    return get_race_weather(track, forced_condition="dry", use_api=False)
                elif choice_num == 4:
                    return get_race_weather(track, forced_condition="wet", use_api=False)
                elif choice_num == 5:
                    return get_race_weather(track, forced_condition="mixed", use_api=False)
                else:
                    print(f"Please enter a number between 1 and {max_option}")
            else:
                if choice_num == 1:
                    return get_race_weather(track, use_api=False)
                elif choice_num == 2:
                    return get_race_weather(track, forced_condition="dry", use_api=False)
                elif choice_num == 3:
                    return get_race_weather(track, forced_condition="wet", use_api=False)
                elif choice_num == 4:
                    return get_race_weather(track, forced_condition="mixed", use_api=False)
                else:
                    print(f"Please enter a number between 1 and {max_option}")
        else:
            print("Please enter a valid number")


def run_race_simulation(track, weather_option):
    """Run the complete race simulation with real F1 data integration."""
    print("\n" + "=" * 60)
    print("🏎️  INTEGRATING REAL F1 DATA FOR ENHANCED PREDICTION")
    print("=" * 60)
    
    # Auto-detect sprint weekends — no prompt needed, fetch immediately
    from models.simple_qualifying_injector import is_sprint_weekend
    _is_sprint = is_sprint_weekend(track.name)

    if _is_sprint:
        print(f"\n🏁 Sprint weekend detected — auto-fetching Sprint Qualifying results...")
        use_actual_qualifying = True
        _auto_fetch = True
    else:
        use_actual_qualifying = input("\n🏁 Use actual 2026 qualifying results if available? (y/n): ").lower().startswith('y')
        _auto_fetch = False

    actual_qualifying_used = False
    
    # Get all drivers and teams
    drivers = get_all_drivers()
    teams = get_all_teams()
    
    # Enhance with real F1 data using loading animation
    try:
        enhanced_drivers, enhanced_teams = loading_with_animation(
            "Fetching and processing real F1 performance data",
            lambda: real_data_enhancer.enhance_race_prediction(drivers, teams, track)
        )
        
        # Show enhancement summary
        print("\n📈 DATA ENHANCEMENT SUMMARY:")
        print("-" * 40)
        
        # Get real data for summary
        real_driver_data = real_data_enhancer.get_enhanced_driver_data()
        real_team_data = real_data_enhancer.get_enhanced_team_data()
        
        if real_driver_data:
            enhanced_count = 0
            for driver in enhanced_drivers:
                driver_abbrev = real_data_enhancer._get_driver_abbreviation(driver.name)
                if driver_abbrev in real_driver_data:
                    enhanced_count += 1
            print(f"• Drivers enhanced with real data: {enhanced_count}/{len(drivers)}")
        
        if real_team_data:
            enhanced_count = 0
            for team in enhanced_teams:
                team_name_clean = real_data_enhancer._clean_team_name(team.name)
                for real_team_name in real_team_data.keys():
                    if team_name_clean.lower() in real_team_name.lower():
                        enhanced_count += 1
                        break
            print(f"• Teams enhanced with real data: {enhanced_count}/{len(teams)}")
            
        # Get track insights with loading animation
        track_insights = loading_with_animation(
            "Analyzing track-specific performance data",
            lambda: real_data_enhancer.get_track_insights(track.name)
        )
        if track_insights['lap_times']:
            print(f"• Track data available for {len(track_insights['lap_times'])} drivers")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"⚠️  Warning: Could not fetch real F1 data: {e}")
        print("🎯 Proceeding with original simulation data...")
        enhanced_drivers, enhanced_teams = drivers, teams
    
    # Create enhanced race simulator with real data
    weather = weather_option
    simulator = create_enhanced_simulator(track, enhanced_drivers, enhanced_teams, weather, real_data_enhancer)
    
    # Handle qualifying (real or simulated)
    if use_actual_qualifying:
        try:
            from models.simple_qualifying_injector import inject_qualifying_results

            # Sprint weekends: silent auto-fetch (no menu stop)
            # Conventional weekends: show the interactive menu
            injected_grid = inject_qualifying_results(track_name=track.name, auto=_auto_fetch)
            
            if injected_grid:
                simulator.grid_positions = injected_grid
                qualifying_results = injected_grid
                actual_qualifying_used = True
                print("✅ Using actual 2026 qualifying results!")
            else:
                print("⏭️ Proceeding with simulated qualifying...")
                qualifying_results = simulator.simulate_qualifying()
        except Exception as e:
            print(f"❌ Error with actual qualifying: {e}")
            print("⏭️ Falling back to simulated qualifying...")
            qualifying_results = simulator.simulate_qualifying()
    else:
        # Simulate qualifying
        print("\n🏎️ Simulating qualifying session...")
        qualifying_results = simulator.simulate_qualifying()
    
    # Optional: Grid adjustments (crashes, penalties, etc.)
    grid_adjustments_made = False
    try:
        from models.grid_adjustments import GridAdjustmentManager
        
        adjust_grid = input("\n🔧 Make grid adjustments before race? (formation lap crash, penalties, etc.) (y/n): ").lower().startswith('y')
        
        if adjust_grid:
            adjustment_manager = GridAdjustmentManager()
            adjustment_manager.set_original_grid(qualifying_results)
            
            adjustments_applied = adjustment_manager.interactive_grid_adjustment()
            
            if adjustments_applied:
                # Apply adjusted grid to simulator
                final_grid = adjustment_manager.get_final_grid()
                simulator.grid_positions = final_grid
                qualifying_results = final_grid  # Update for display
                grid_adjustments_made = True
                
                print(f"\n✅ Grid adjustments applied!")
                print(f"📝 {adjustment_manager.get_adjustment_summary()}")
                
                removed_drivers = adjustment_manager.get_removed_drivers()
                if removed_drivers:
                    print(f"🚨 Drivers removed from race: {', '.join(removed_drivers)}")
                    
    except Exception as e:
        print(f"❌ Grid adjustment error: {e}")
        print("⏭️ Proceeding with original grid...")
    
    # Optional: Enhanced race start simulation
    race_start_enhanced = False
    try:
        from models.race_start_predictor import enhance_race_with_start_simulation
        
        enhance_start = input("\n🏁 Use enhanced race start modeling? (analyzes driver-specific start performance) (y/n): ").lower().startswith('y')
        
        if enhance_start:
            # Apply race start modeling
            post_start_grid = enhance_race_with_start_simulation(simulator, qualifying_results, track)
            race_start_enhanced = True
            print("✅ Enhanced race start modeling applied!")
            
    except Exception as e:
        print(f"❌ Race start enhancement error: {e}")
        print("⏭️ Proceeding with standard race start...")
    
    # Optional: Advanced pit strategy modeling
    strategy_enhanced = False
    try:
        from models.advanced_strategy_predictor import enhance_race_with_advanced_strategy
        
        enhance_strategy = input("\n🔧 Use advanced pit strategy modeling? (1-stop vs 2-stop analysis) (y/n): ").lower().startswith('y')
        
        if enhance_strategy:
            # Apply advanced strategy modeling with optional overrides
            strategies_applied = enhance_race_with_advanced_strategy(simulator, qualifying_results, track, weather)
            strategy_enhanced = True
            print("✅ Advanced pit strategy modeling applied!")
            
    except Exception as e:
        print(f"❌ Strategy enhancement error: {e}")
        print("⏭️ Proceeding with standard strategy modeling...")
    
    # Simulate race
    print("\n🏁 Simulating race...")
    race_results = simulator.simulate_race()
    
    # Display results
    display_race_header(track, weather)
    display_qualifying_results(qualifying_results)
    display_race_results(race_results)
    
    # Show data source information
    print("\n" + "=" * 60)
    print("📊 DATA SOURCE INFORMATION")
    print("=" * 60)
    print("This simulation combines:")
    if actual_qualifying_used:
        print("• ✅ ACTUAL 2026 qualifying results (web-scraped)")
    else:
        print("• 🎯 Simulated qualifying (form-based prediction)")
    if grid_adjustments_made:
        print("• 🔧 Pre-race grid adjustments applied")
    if race_start_enhanced:
        print("• 🏁 Enhanced race start performance modeling")
    if strategy_enhanced:
        print("• ⚙️ Advanced pit strategy analysis (1-stop vs 2-stop)")
    print("• Real F1 performance data (Fast-F1 API)")
    print("• Historical race statistics")
    print("• Advanced simulation algorithms")
    print("• Weather and track condition modeling")
    if actual_qualifying_used:
        print("\n🎯 ENHANCED ACCURACY: Using real 2026 qualifying data!")
    if grid_adjustments_made:
        print("⚠️  RACE CONDITIONS: Grid modified for real-world incidents")
    if race_start_enhanced or strategy_enhanced:
        print("🚀 ADVANCED MODELING: Enhanced race dynamics applied!")
    print("=" * 60)
    
    # Offer further analysis
    return simulator, qualifying_results, race_results


def show_analysis_menu(simulator, qualifying_results, race_results):
    """Show menu for additional analysis options."""
    track = simulator.track
    
    while True:
        print("\nAnalysis Options:")
        print("1. Show qualifying vs race performance analysis")
        print("2. Show detailed race statistics")
        print("3. Show real F1 data insights")
        print("4. Visualize basic race progress")
        print("5. Generate advanced visualizations")
        print("6. Generate all visualizations (saves to visualized-graphs folder)")
        print("7. Simulate another race")
        print("8. Quit")
        
        try:
            choice = input("\nSelect an option (1-8): ")
            choice = int(choice)
            
            if choice == 1:
                # Qualifying vs race analysis
                analysis_df = analyze_qualifying_performance(qualifying_results, race_results)
                print("\nQualifying vs Race Performance:")
                print(tabulate_func(analysis_df, headers='keys', tablefmt='pipe', showindex=False))
                
            elif choice == 2:
                # Race statistics
                metrics = calculate_performance_metrics(race_results)
                print("\nRace Statistics:")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        print(f"{key}: {value:.2f}")
                    else:
                        print(f"{key}: {value}")
                        
            elif choice == 3:
                # Real F1 data insights
                show_real_data_insights(simulator)
                
            elif choice == 4:
                # Visualize race progress
                print("\nGenerating race progress visualization...")
                plot_race_progress(race_results, track.laps)
                simulate_live_race_progress(race_results, track.laps, track.name)
                
            elif choice == 5:
                # Advanced visualizations submenu
                show_visualization_menu(race_results, track)
                
            elif choice == 6:
                # Generate all visualizations
                print("\nGenerating all visualizations...")
                visualizations = generate_all_visualizations(race_results, track.laps, track.name)
                print("\nAll visualizations saved to the 'visualized-graphs' folder:")
                for viz_type, path in visualizations.items():
                    print(f"- {viz_type}: {os.path.basename(path)}")
                
            elif choice == 7:
                # Simulate another race
                return True
                
            elif choice == 8:
                return False
                
            else:
                print("Please enter a number between 1 and 8")
                
        except ValueError:
            print("Please enter a valid number")


def show_visualization_menu(race_results, track):
    """Show submenu for advanced visualization options."""
    while True:
        print("\nAdvanced Visualization Options:")
        print("1. Tire degradation chart")
        print("2. Lap time progression")
        print("3. Driver performance comparison")
        print("4. Team performance analysis")
        print("5. Return to main menu")
        
        try:
            choice = input("\nSelect visualization type (1-5): ")
            choice = int(choice)
            
            if choice == 1:
                print("\nGenerating tire degradation visualization...")
                path = plot_tire_degradation(track.laps, race_results, track.name)
                print(f"Visualization saved to: {path}")
                
            elif choice == 2:
                print("\nGenerating lap time progression visualization...")
                path = plot_lap_time_progression(race_results, track.laps, track.name)
                print(f"Visualization saved to: {path}")
                
            elif choice == 3:
                print("\nGenerating driver comparison visualizations...")
                paths = plot_driver_comparison(race_results, track.name)
                print(f"Visualizations saved to:")
                for path in paths:
                    print(f"- {path}")
                    
            elif choice == 4:
                print("\nGenerating team performance visualizations...")
                paths = plot_team_performance(race_results)
                print(f"Visualizations saved to:")
                for path in paths:
                    print(f"- {path}")
                    
            elif choice == 5:
                return
                
            else:
                print("Please enter a number between 1 and 5")
                
        except ValueError:
            print("Please enter a valid number")


def show_real_data_insights(simulator):
    """Show detailed insights from real F1 data integration."""
    print("\n" + "=" * 70)
    print("📊 REAL F1 DATA INSIGHTS")
    print("=" * 70)
    
    # Check if enhanced simulator is being used
    if hasattr(simulator, 'real_data_enhancer') and simulator.real_data_enhancer:
        enhancer = simulator.real_data_enhancer
        
        # Show driver insights
        print("\n🏎️ DRIVER PERFORMANCE INSIGHTS:")
        print("-" * 40)
        
        with suppress_fastf1_logging():
            real_driver_data = enhancer.get_enhanced_driver_data()
        
        if real_driver_data:
            top_performers = sorted(real_driver_data.items(), 
                                  key=lambda x: x[1]['skill_dry'], 
                                  reverse=True)[:5]
            
            print("Top 5 Drivers by Real Performance Data:")
            for i, (driver, data) in enumerate(top_performers, 1):
                print(f"{i}. {driver}")
                print(f"   Dry Skill: {data['skill_dry']}/100")
                print(f"   Consistency: {data['consistency']}/100")
                print(f"   Overtaking: {data['skill_overtaking']}/100")
                print(f"   Races Analyzed: {data['total_races']}")
                print()
        else:
            print("No real driver data available.")
        
        # Show team insights
        print("\n🏁 TEAM PERFORMANCE INSIGHTS:")
        print("-" * 40)
        
        with suppress_fastf1_logging():
            real_team_data = enhancer.get_enhanced_team_data()
        
        if real_team_data:
            top_teams = sorted(real_team_data.items(), 
                             key=lambda x: x[1]['performance'], 
                             reverse=True)[:5]
            
            print("Top 5 Teams by Real Performance Data:")
            for i, (team, data) in enumerate(top_teams, 1):
                print(f"{i}. {team}")
                print(f"   Performance: {data['performance']}/100")
                print(f"   Reliability: {data['reliability']}/100")
                print(f"   Pit Efficiency: {data['pit_efficiency']}/100")
                print(f"   Races Analyzed: {data['total_races']}")
                print()
        else:
            print("No real team data available.")
        
        # Show track insights
        print("\n🏎️ TRACK-SPECIFIC INSIGHTS:")
        print("-" * 40)
        track_insights = simulator.track_insights
        
        if track_insights.get('lap_times'):
            print(f"Real lap times available for {len(track_insights['lap_times'])} drivers")
            
            # Show fastest drivers on this track
            lap_times = track_insights['lap_times']
            fastest_drivers = sorted(lap_times.items(), key=lambda x: x[1])[:3]
            
            print("Fastest Drivers on this Track (Real Data):")
            for i, (driver, time) in enumerate(fastest_drivers, 1):
                print(f"{i}. {driver}: {time:.3f}s")
        
        if track_insights.get('weather_history'):
            weather = track_insights['weather_history']
            print(f"\nHistorical Weather Data:")
            print(f"• Average Temperature: {weather.get('avg_temp', 'N/A')}°C")
            print(f"• Average Humidity: {weather.get('avg_humidity', 'N/A')}%")
            print(f"• Rain Probability: {'High' if weather.get('rain_probability') else 'Low'}")
        
        # Show simulation metadata
        print("\n🔧 SIMULATION ENHANCEMENT:")
        print("-" * 40)
        metadata = simulator.get_simulation_metadata()
        
        for key, value in metadata.items():
            formatted_key = key.replace('_', ' ').title()
            print(f"• {formatted_key}: {value}")
    
    else:
        print("❌ Enhanced simulation not available.")
        print("Real F1 data integration is disabled or unavailable.")
    
    print("=" * 70)


def main():
    """Main application entry point."""
    print_welcome()
    
    while True:
        try:
            # Let user select track
            track = select_track()
            
            # Let user select weather conditions
            weather = select_weather_option(track)
            
            # Run simulation
            simulator, qualifying_results, race_results = run_race_simulation(track, weather)
            
            # Show analysis menu
            continue_simulation = show_analysis_menu(simulator, qualifying_results, race_results)
            if not continue_simulation:
                break
                
        except KeyboardInterrupt:
            print("\nExiting application...")
            break
            
    print("\nThank you for using the F1 Race Prediction Simulator!")


if __name__ == "__main__":
    # Check for required packages
    try:
        import numpy
        import pandas
        import matplotlib
        import tabulate
        import colorama
        import seaborn
    except ImportError:
        print("Missing required packages. Installing dependencies...")
        import subprocess
        subprocess.call([sys.executable, "-m", "pip", "install", 
                        "numpy", "pandas", "matplotlib", "tabulate", "colorama", "seaborn"])
        print("Dependencies installed. Starting application...")
    
    main()