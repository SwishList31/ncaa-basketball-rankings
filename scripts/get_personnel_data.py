"""
Get the actual player/personnel data from Kenpom
Let's use the correct functions to get Height, Experience, and Player stats
"""

import pandas as pd
import os
from dotenv import load_dotenv
from kenpompy.utils import login
import kenpompy.summary as kp_summary

def get_personnel_data():
    """Get all personnel-related data from Kenpom"""
    
    # Load credentials
    load_dotenv()
    EMAIL = os.getenv('KENPOM_EMAIL')
    PASSWORD = os.getenv('KENPOM_PASSWORD')
    
    if not EMAIL or not PASSWORD:
        print("No credentials found!")
        return
    
    print("Logging into Kenpom...")
    browser = login(EMAIL, PASSWORD)
    print("Login successful!\n")
    
    # 1. Get Height/Experience data
    print("1. FETCHING HEIGHT/EXPERIENCE DATA:")
    print("-"*60)
    try:
        height_data = kp_summary.get_height(browser)
        print(f"Success! Got data for {len(height_data)} teams")
        print(f"Columns: {list(height_data.columns)}")
        print("\nSample data:")
        print(height_data.head(3))
        
        # Save it
        height_data.to_csv('data/kenpom_height_experience_latest.csv', index=False)
        print("\nSaved to: data/kenpom_height_experience_latest.csv")
        
    except Exception as e:
        print(f"Error getting height data: {e}")
    
    # 2. Get Player Stats
    print("\n\n2. FETCHING PLAYER STATS:")
    print("-"*60)
    try:
        player_stats = kp_summary.get_playerstats(browser)
        print(f"Success! Got player statistics")
        print(f"Shape: {player_stats.shape}")
        print(f"Columns: {list(player_stats.columns)}")
        print("\nSample data:")
        print(player_stats.head(5))
        
        # Save it
        player_stats.to_csv('data/kenpom_player_stats_latest.csv', index=False)
        print("\nSaved to: data/kenpom_player_stats_latest.csv")
        
    except Exception as e:
        print(f"Error getting player stats: {e}")
    
    # 3. Get KPOY (Player of Year) Rankings
    print("\n\n3. FETCHING KPOY RANKINGS:")
    print("-"*60)
    try:
        kpoy_data = kp_summary.get_kpoy(browser)
        print(f"Success! Got KPOY rankings")
        print(f"Shape: {kpoy_data.shape}")
        print(f"Columns: {list(kpoy_data.columns)}")
        print("\nTop 10 KPOY candidates:")
        print(kpoy_data.head(10))
        
        # Save it
        kpoy_data.to_csv('data/kenpom_kpoy_rankings_latest.csv', index=False)
        print("\nSaved to: data/kenpom_kpoy_rankings_latest.csv")
        
    except Exception as e:
        print(f"Error getting KPOY data: {e}")
    
    # 4. Try to get individual team rosters
    print("\n\n4. CHECKING TEAM-SPECIFIC DATA:")
    print("-"*60)
    try:
        # Get a scouting report for Duke
        duke_report = kp_team.get_scouting_report(browser, team='Duke')
        print("Got Duke scouting report!")
        print(f"Keys: {duke_report.keys() if isinstance(duke_report, dict) else 'Not a dict'}")
        
    except Exception as e:
        print(f"Error getting team data: {e}")
    
    print("\n\nDONE! Check the data folder for new files.")

def analyze_personnel_impact():
    """Analyze how height/experience might impact our model"""
    
    print("\n\n" + "="*60)
    print("ANALYZING PERSONNEL IMPACT")
    print("="*60)
    
    try:
        # Load height/experience data
        height_exp = pd.read_csv('data/kenpom_height_experience_latest.csv')
        rankings = pd.read_csv('data/kenpom_rankings_latest.csv')
        
        # Merge with rankings
        merged = pd.merge(rankings, height_exp, on='Team', how='inner')
        
        # Show correlations
        print("\nCORRELATIONS WITH SUCCESS:")
        print("-"*40)
        
        # Check if these columns exist and calculate correlations
        if 'Avg.Hgt' in merged.columns:
            height_corr = merged['AdjEM'].corr(merged['Avg.Hgt'])
            print(f"Height vs AdjEM: {height_corr:.3f}")
            
        if 'Experience' in merged.columns:
            exp_corr = merged['AdjEM'].corr(merged['Experience'])
            print(f"Experience vs AdjEM: {exp_corr:.3f}")
            
        # Find extremes
        print("\n\nTALLEST TEAMS:")
        print(merged.nlargest(5, 'Avg.Hgt')[['Team', 'Avg.Hgt', 'AdjEM_Rank']])
        
        print("\n\nMOST EXPERIENCED TEAMS:")
        print(merged.nlargest(5, 'Experience')[['Team', 'Experience', 'AdjEM_Rank']])
        
    except Exception as e:
        print(f"Error in analysis: {e}")

if __name__ == "__main__":
    # Get the personnel data
    get_personnel_data()
    
    # Analyze it
    analyze_personnel_impact()