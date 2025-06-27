"""
Check what additional metrics we have available in our data
"""

import pandas as pd

def check_available_data():
    """Check all available metrics in our scraped data"""
    
    print("CHECKING AVAILABLE METRICS")
    print("="*80)
    
    # Check four factors data
    print("\n1. FOUR FACTORS DATA:")
    print("-"*80)
    four_factors = pd.read_csv('data/kenpom_four_factors_latest.csv')
    print(f"Columns: {list(four_factors.columns)}")
    
    # Check team stats
    print("\n\n2. TEAM STATS DATA:")
    print("-"*80)
    team_stats = pd.read_csv('data/kenpom_team_stats_latest.csv')
    print(f"Columns: {list(team_stats.columns)}")
    
    # Look for turnover and shooting metrics
    print("\n\n3. KEY METRICS AVAILABLE:")
    print("-"*80)
    
    # In four factors
    ff_metrics = [col for col in four_factors.columns if any(term in col.lower() for term in ['to%', 'turnover', 'efg', 'fg%', 'eff'])]
    print("From Four Factors:")
    for metric in ff_metrics:
        print(f"  - {metric}")
    
    # In team stats
    ts_metrics = [col for col in team_stats.columns if any(term in col.lower() for term in ['to%', 'turnover', 'efg', 'fg%', '3p', '2p', 'ft'])]
    print("\nFrom Team Stats:")
    for metric in ts_metrics:
        print(f"  - {metric}")
    
    # Show sample data
    print("\n\n4. SAMPLE DATA (Top 5 teams):")
    print("-"*80)
    
    # Merge rankings with four factors
    rankings = pd.read_csv('data/kenpom_rankings_latest.csv')
    merged = pd.merge(rankings, four_factors, on='Team', how='inner', suffixes=('', '_ff'))
    
    # Get specific metrics for top teams
    top_teams = merged.nsmallest(5, 'AdjEM_Rank')
    
    if 'Off-TO%' in merged.columns and 'Def-TO%' in merged.columns:
        print("\nTurnover Rates (Top 5 teams):")
        print(f"{'Team':<15} {'Off TO%':<10} {'Off Rank':<10} {'Def TO%':<10} {'Def Rank':<10}")
        print("-"*60)
        for idx, row in top_teams.iterrows():
            print(f"{row['Team']:<15} {row['Off-TO%']:<10} {row['Off-TO%.Rank']:<10.0f} "
                  f"{row['Def-TO%']:<10} {row['Def-TO%.Rank']:<10.0f}")
    
    if 'Off-eFG%' in merged.columns:
        print("\n\nEffective FG% (Top 5 teams):")
        print(f"{'Team':<15} {'Off eFG%':<10} {'Off Rank':<10} {'Def eFG%':<10} {'Def Rank':<10}")
        print("-"*60)
        for idx, row in top_teams.iterrows():
            print(f"{row['Team']:<15} {row['Off-eFG%']:<10} {row['Off-eFG%.Rank']:<10.0f} "
                  f"{row['Def-eFG%']:<10} {row['Def-eFG%.Rank']:<10.0f}")

if __name__ == "__main__":
    check_available_data()