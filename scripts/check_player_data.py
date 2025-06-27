"""
Check what player/personnel data is available from Kenpom
"""

import pandas as pd
import os
from kenpompy.utils import login
import kenpompy.summary as kp_summary
import kenpompy.team as kp_team
import kenpompy.misc as kp_misc

def explore_available_data():
    """Check all available data types from kenpompy"""
    
    print("CHECKING AVAILABLE KENPOM DATA")
    print("="*60)
    
    # Check what CSV files we already have
    print("\n1. EXISTING DATA FILES:")
    print("-"*60)
    data_dir = 'data'
    for file in os.listdir(data_dir):
        if file.endswith('.csv') and 'kenpom' in file and 'latest' in file:
            print(f"  - {file}")
            
    # Check what kenpompy can theoretically get
    print("\n2. AVAILABLE KENPOMPY FUNCTIONS:")
    print("-"*60)
    
    # Summary module functions
    print("\nSummary module (kp_summary):")
    summary_funcs = [attr for attr in dir(kp_summary) if callable(getattr(kp_summary, attr)) and not attr.startswith('_')]
    for func in summary_funcs:
        print(f"  - {func}")
        
    # Team module functions  
    print("\nTeam module (kp_team):")
    team_funcs = [attr for attr in dir(kp_team) if callable(getattr(kp_team, attr)) and not attr.startswith('_')]
    for func in team_funcs:
        print(f"  - {func}")
        
    # Misc module functions
    print("\nMisc module (kp_misc):")
    misc_funcs = [attr for attr in dir(kp_misc) if callable(getattr(kp_misc, attr)) and not attr.startswith('_')]
    for func in misc_funcs:
        print(f"  - {func}")

def check_team_stats_details():
    """Look at what's in the team_stats file"""
    print("\n3. CHECKING TEAM_STATS CONTENT:")
    print("-"*60)
    
    try:
        team_stats = pd.read_csv('data/kenpom_team_stats_latest.csv')
        print(f"Shape: {team_stats.shape}")
        print(f"\nColumns: {list(team_stats.columns)}")
        print(f"\nFirst few rows:")
        print(team_stats.head(3))
    except Exception as e:
        print(f"Error loading team_stats: {e}")

def test_player_stats_retrieval():
    """Try to get player-specific data"""
    print("\n4. ATTEMPTING TO GET PLAYER DATA:")
    print("-"*60)
    
    # Load credentials from .env
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    EMAIL = os.getenv('KENPOM_EMAIL')
    PASSWORD = os.getenv('KENPOM_PASSWORD')
    
    if not EMAIL or not PASSWORD:
        print("No credentials found in .env file")
        return
        
    try:
        print("Logging into Kenpom...")
        browser = login(EMAIL, PASSWORD)
        
        # Check if get_teamstats has player options
        print("\nTrying different teamstats options:")
        stat_types = ['OffDef', 'FourFactors', 'TeamStats', 'PointDist', 
                     'Height', 'PlayerStats', 'Kpoy']
        
        for stat_type in stat_types:
            try:
                print(f"\n  Trying {stat_type}...")
                stats = kp_summary.get_teamstats(browser, defense=stat_type)
                print(f"    Success! Shape: {stats.shape}")
                if 'player' in str(stats.columns).lower() or stat_type in ['PlayerStats', 'Kpoy', 'Height']:
                    print(f"    POTENTIAL PLAYER DATA FOUND!")
                    print(f"    Columns: {list(stats.columns)[:5]}...")  # First 5 columns
                    # Save this data
                    stats.to_csv(f'data/kenpom_{stat_type.lower()}_latest.csv', index=False)
            except Exception as e:
                print(f"    Failed: {e}")
                
        # Try team-specific data
        print("\n\nTrying team-specific player data for Duke:")
        try:
            # Get Duke's player stats if available
            duke_players = kp_team.get_roster(browser, team='Duke')
            print(f"  Success! Got Duke roster data")
            print(f"  Columns: {list(duke_players.columns)}")
            duke_players.to_csv('data/sample_roster_duke.csv', index=False)
        except Exception as e:
            print(f"  No get_roster function or error: {e}")
            
        # Check what else is in kp_team
        print("\n\nChecking other team-specific functions:")
        if hasattr(kp_team, 'get_team_players'):
            print("  Found get_team_players!")
        if hasattr(kp_team, 'get_player_stats'):
            print("  Found get_player_stats!")
            
    except Exception as e:
        print(f"Error during retrieval: {e}")

if __name__ == "__main__":
    # First check what we have
    explore_available_data()
    
    # Check team stats content
    check_team_stats_details()
    
    # Try to get player data
    test_player_stats_retrieval()
    
    print("\n\nSUMMARY:")
    print("="*60)
    print("Kenpom DOES track player/personnel data including:")
    print("- Height/Experience of teams")
    print("- Player stats and KPOY (Kenpom Player of Year) rankings")
    print("- Team-specific roster information")
    print("\nBut we need to specifically scrape these with the right functions!")
