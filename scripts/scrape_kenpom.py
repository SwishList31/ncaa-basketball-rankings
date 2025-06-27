"""
Kenpom Data Scraper - Fixed Data Types Version
"""

import os
import pandas as pd
from datetime import datetime
from kenpompy.utils import login
import kenpompy.summary as kp_summary
import kenpompy.misc as kp_misc

# Direct credentials
EMAIL = "mitchwatkins@gmail.com"
PASSWORD = "ePDd2ZzTZX!A@Vn"
DATA_DIR = 'data'

def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs('models', exist_ok=True)

def scrape_current_data():
    """Main function to scrape all current Kenpom data"""
    
    print("NCAA Basketball Power Rankings - Data Collection")
    print("=" * 50)
    
    # Ensure directories exist
    ensure_directories()
    
    # Login to Kenpom
    print("\nLogging into Kenpom...")
    try:
        browser = login(EMAIL, PASSWORD)
        print("Login successful!")
    except Exception as e:
        print(f"Login failed: {e}")
        return
    
    # Collect data
    data_collected = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Get Four Factors (this has the AdjOE and AdjDE we need for rankings)
    print("\nFetching Four Factors (includes efficiency ratings)...")
    try:
        four_factors = kp_summary.get_fourfactors(browser)
        data_collected['four_factors'] = four_factors
        print(f"Retrieved data for {len(four_factors)} teams")
        
        # Convert efficiency columns to numeric
        four_factors['AdjOE'] = pd.to_numeric(four_factors['AdjOE'], errors='coerce')
        four_factors['AdjDE'] = pd.to_numeric(four_factors['AdjDE'], errors='coerce')
        
        # Calculate Adjusted EM (efficiency margin)
        four_factors['AdjEM'] = four_factors['AdjOE'] - four_factors['AdjDE']
        four_factors['AdjEM_Rank'] = four_factors['AdjEM'].rank(ascending=False, method='min').astype(int)
        
        # Create a rankings dataframe
        rankings = four_factors[['Team', 'Conference', 'AdjEM', 'AdjEM_Rank', 'AdjOE', 'AdjOE.Rank', 'AdjDE', 'AdjDE.Rank']].copy()
        rankings = rankings.sort_values('AdjEM_Rank')
        data_collected['rankings'] = rankings
        
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. Get efficiency/tempo stats
    print("\nFetching tempo stats...")
    try:
        efficiency = kp_summary.get_efficiency(browser)
        data_collected['tempo_stats'] = efficiency
        print(f"Retrieved tempo data for {len(efficiency)} teams")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Get team stats
    print("\nFetching additional team stats...")
    try:
        # Get offensive/defensive stats
        team_stats = kp_summary.get_teamstats(browser)
        data_collected['team_stats'] = team_stats
        print(f"Retrieved additional stats")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. Try to get some game data
    print("\nFetching game data...")
    try:
        # Get upset games
        upsets = kp_misc.get_gameattribs(browser, metric='Upsets')
        data_collected['upset_games'] = upsets
        print(f"Retrieved {len(upsets)} upset games")
        
        # Get exciting games
        exciting = kp_misc.get_gameattribs(browser, metric='Excitement')
        data_collected['exciting_games'] = exciting
        print(f"Retrieved {len(exciting)} exciting games")
    except Exception as e:
        print(f"Error getting games: {e}")
    
    # Save all data
    print("\nSaving data...")
    for name, df in data_collected.items():
        if df is not None and not df.empty:
            # Save with timestamp
            filename = os.path.join(DATA_DIR, f'kenpom_{name}_{timestamp}.csv')
            df.to_csv(filename, index=False)
            
            # Save as 'latest' for easy access
            latest_filename = os.path.join(DATA_DIR, f'kenpom_{name}_latest.csv')
            df.to_csv(latest_filename, index=False)
            
            print(f"   Saved {name}: {len(df)} records")
    
    print("\nData collection complete!")
    print(f"Files saved in: {os.path.abspath(DATA_DIR)}")
    
    # Show top teams by our calculated rankings
    if 'rankings' in data_collected:
        print("\n" + "="*80)
        print("TOP 25 TEAMS BY ADJUSTED EFFICIENCY MARGIN")
        print("="*80)
        print(f"{'Rank':<6}{'Team':<20}{'Conf':<8}{'AdjEM':<10}{'AdjO':<10}{'AdjD':<10}")
        print("-"*80)
        
        top_25 = data_collected['rankings'].head(25)
        for idx, row in top_25.iterrows():
            print(f"{row['AdjEM_Rank']:<6}{row['Team']:<20}{row['Conference']:<8}"
                  f"{row['AdjEM']:<10.2f}{row['AdjOE']:<10.2f}{row['AdjDE']:<10.2f}")
    
    # Also show what files we have
    print("\n" + "="*80)
    print("FILES CREATED:")
    print("="*80)
    for name in data_collected.keys():
        print(f"- kenpom_{name}_latest.csv")
    
    return data_collected

if __name__ == "__main__":
    # Run the scraper
    data = scrape_current_data()
    input("\nPress Enter to exit...")