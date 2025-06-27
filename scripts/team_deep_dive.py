"""
Deep Dive Analysis for Specific Teams
Let's investigate why Arkansas moved so much and how BYU ranks
"""

import pandas as pd
import numpy as np

def analyze_team_in_detail(team_name, data_dir='data'):
    """Analyze a specific team across all models"""
    
    print(f"\n{'='*80}")
    print(f"DEEP DIVE ANALYSIS: {team_name}")
    print(f"{'='*80}")
    
    # Load all ranking files
    try:
        # Kenpom original
        kenpom = pd.read_csv(f'{data_dir}/kenpom_rankings_latest.csv')
        kenpom_row = kenpom[kenpom['Team'] == team_name].iloc[0] if len(kenpom[kenpom['Team'] == team_name]) > 0 else None
        
        # Weighted model
        weighted = pd.read_csv(f'{data_dir}/weighted_rankings_latest.csv')
        weighted_row = weighted[weighted['Team'] == team_name].iloc[0] if len(weighted[weighted['Team'] == team_name]) > 0 else None
        
        # Hybrid model
        hybrid = pd.read_csv(f'{data_dir}/hybrid_rankings_latest.csv')
        hybrid_row = hybrid[hybrid['Team'] == team_name].iloc[0] if len(hybrid[hybrid['Team'] == team_name]) > 0 else None
        
        if kenpom_row is None:
            print(f"Team {team_name} not found in data!")
            return
            
        # Basic info
        print(f"\nTeam: {team_name}")
        print(f"Conference: {kenpom_row['Conference']}")
        print(f"KenPom AdjEM: {kenpom_row['AdjEM']:.2f}")
        print(f"Offensive Efficiency: {kenpom_row['AdjOE']:.2f} (Rank: #{kenpom_row['AdjOE.Rank']:.0f})")
        print(f"Defensive Efficiency: {kenpom_row['AdjDE']:.2f} (Rank: #{kenpom_row['AdjDE.Rank']:.0f})")
        
        # Rankings comparison
        print(f"\n{'-'*50}")
        print(f"RANKINGS ACROSS MODELS:")
        print(f"{'-'*50}")
        print(f"KenPom Rank: #{kenpom_row['AdjEM_Rank']:.0f}")
        
        if weighted_row is not None:
            print(f"Weighted Model Rank: #{weighted_row['Weighted_Rank']:.0f} (Score: {weighted_row['Weighted_Score']:.2f})")
        
        if hybrid_row is not None:
            print(f"Hybrid Model Rank: #{hybrid_row['Hybrid_Rank']:.0f} (Score: {hybrid_row['Hybrid_Score']:.2f})")
            print(f"\nHybrid Model Breakdown:")
            print(f"- Base Efficiency Score: {hybrid_row['Base_Score']:.1f}/100")
            print(f"- Game Results Score: {hybrid_row['Results_Score']:.1f}/100")
            print(f"- Total Movement: {kenpom_row['AdjEM_Rank'] - hybrid_row['Hybrid_Rank']:+.0f} spots")
        
        # Look for this team in upset/exciting games
        print(f"\n{'-'*50}")
        print(f"GAME RESULTS ANALYSIS:")
        print(f"{'-'*50}")
        
        # Check upset games
        upsets = pd.read_csv(f'{data_dir}/kenpom_upset_games_latest.csv')
        team_upsets = []
        
        for col in upsets.columns:
            mask = upsets[col].astype(str).str.contains(team_name, case=False, na=False)
            if mask.any():
                team_upsets.extend(upsets[mask].index.tolist())
        
        if team_upsets:
            print(f"\nFound in {len(set(team_upsets))} upset games:")
            for idx in set(team_upsets):
                game_row = upsets.iloc[idx]
                # Print relevant game info
                for col in game_row.index:
                    if pd.notna(game_row[col]) and str(game_row[col]).strip():
                        print(f"  {col}: {game_row[col]}")
                print()
        
        # Check exciting games
        exciting = pd.read_csv(f'{data_dir}/kenpom_exciting_games_latest.csv')
        team_exciting = []
        
        for col in exciting.columns:
            mask = exciting[col].astype(str).str.contains(team_name, case=False, na=False)
            if mask.any():
                team_exciting.extend(exciting[mask].index.tolist())
        
        if team_exciting:
            print(f"\nFound in {len(set(team_exciting))} exciting/close games")
        
    except Exception as e:
        print(f"Error analyzing {team_name}: {e}")

def compare_all_rankings(data_dir='data'):
    """Show how all teams moved between models"""
    
    print(f"\n{'='*80}")
    print("BIGGEST MOVERS: KENPOM vs HYBRID MODEL")
    print(f"{'='*80}")
    
    try:
        # Load data
        kenpom = pd.read_csv(f'{data_dir}/kenpom_rankings_latest.csv')
        hybrid = pd.read_csv(f'{data_dir}/hybrid_rankings_latest.csv')
        
        # Merge on team name
        comparison = pd.merge(
            kenpom[['Team', 'Conference', 'AdjEM_Rank', 'AdjEM']],
            hybrid[['Team', 'Hybrid_Rank', 'Hybrid_Score', 'Results_Score']],
            on='Team'
        )
        
        # Calculate movement
        comparison['Movement'] = comparison['AdjEM_Rank'] - comparison['Hybrid_Rank']
        
        # Top risers
        print("\nTOP 10 RISERS (Teams that jumped up):")
        print(f"{'Team':<20} {'Conf':<8} {'KP':<6} {'Hybrid':<8} {'Move':<8} {'Results Score':<15}")
        print("-" * 75)
        
        risers = comparison.nlargest(10, 'Movement')
        for idx, row in risers.iterrows():
            print(f"{row['Team']:<20} {row['Conference']:<8} "
                  f"#{row['AdjEM_Rank']:<5.0f} #{row['Hybrid_Rank']:<7.0f} "
                  f"↑{row['Movement']:<7.0f} {row['Results_Score']:<15.1f}")
        
        # Top fallers
        print("\nTOP 10 FALLERS (Teams that dropped):")
        print(f"{'Team':<20} {'Conf':<8} {'KP':<6} {'Hybrid':<8} {'Move':<8} {'Results Score':<15}")
        print("-" * 75)
        
        fallers = comparison.nsmallest(10, 'Movement')
        for idx, row in fallers.iterrows():
            print(f"{row['Team']:<20} {row['Conference']:<8} "
                  f"#{row['AdjEM_Rank']:<5.0f} #{row['Hybrid_Rank']:<7.0f} "
                  f"↓{abs(row['Movement']):<7.0f} {row['Results_Score']:<15.1f}")
        
    except Exception as e:
        print(f"Error in comparison: {e}")

# Main analysis
if __name__ == "__main__":
    # Analyze Arkansas (big mover)
    analyze_team_in_detail('Arkansas')
    
    # Analyze BYU
    analyze_team_in_detail('BYU')
    
    # Show overall movement patterns
    compare_all_rankings()
    
    # Look for patterns in results scores
    print(f"\n{'='*80}")
    print("RESULTS SCORE PATTERNS")
    print(f"{'='*80}")
    
    hybrid = pd.read_csv('data/hybrid_rankings_latest.csv')
    
    # Teams with perfect results scores
    perfect_results = hybrid[hybrid['Results_Score'] == 100.0]
    print(f"\nTeams with PERFECT (100.0) Results Scores: {len(perfect_results)}")
    for idx, row in perfect_results.head(10).iterrows():
        print(f"- {row['Team']} (KP: #{row['KenPom_Rank']:.0f}, Hybrid: #{row['Hybrid_Rank']:.0f})")
    
    # Teams with poor results scores
    poor_results = hybrid[hybrid['Results_Score'] < 50.0]
    print(f"\nTeams with POOR (<50) Results Scores: {len(poor_results)}")
    for idx, row in poor_results.head(10).iterrows():
        print(f"- {row['Team']} (Score: {row['Results_Score']:.1f}, KP: #{row['KenPom_Rank']:.0f})")