"""
NCAA Basketball Weighted Power Ranking Model - Updated Version
Removed consistency metric and rebalanced weights
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class WeightedPowerRankingModel:
    def __init__(self, weights=None):
        """
        Initialize the model with custom weights for different factors
        Default weights sum to 1.0 (100%)
        """
        if weights is None:
            self.weights = {
                'offensive_efficiency': 0.35,  # 35% - How well team scores
                'defensive_efficiency': 0.35,  # 35% - How well team prevents scoring
                'momentum': 0.15,              # 15% - Recent performance trend
                'schedule_strength': 0.10,     # 10% - Quality of opponents
                'dominance': 0.05              # 5%  - Margin of victory
            }
        else:
            self.weights = weights
            
        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.001:
            print(f"Warning: Weights sum to {total}, normalizing to 1.0")
            for key in self.weights:
                self.weights[key] = self.weights[key] / total
    
    def load_data(self, data_dir='data'):
        """Load the latest Kenpom data"""
        print("Loading data...")
        
        # Load main data files
        self.rankings = pd.read_csv(f'{data_dir}/kenpom_rankings_latest.csv')
        self.four_factors = pd.read_csv(f'{data_dir}/kenpom_four_factors_latest.csv')
        self.team_stats = pd.read_csv(f'{data_dir}/kenpom_team_stats_latest.csv')
        
        # Load game data if available
        try:
            self.games = pd.read_csv(f'{data_dir}/kenpom_exciting_games_latest.csv')
            self.upsets = pd.read_csv(f'{data_dir}/kenpom_upset_games_latest.csv')
        except:
            self.games = None
            self.upsets = None
            
        print(f"Loaded data for {len(self.rankings)} teams")
        
    def calculate_offensive_score(self, row):
        """Calculate offensive efficiency score (0-100)"""
        # Use adjusted offensive efficiency
        # Normalize to 0-100 scale where best offense = 100
        max_oe = self.rankings['AdjOE'].max()
        min_oe = self.rankings['AdjOE'].min()
        
        return 100 * (row['AdjOE'] - min_oe) / (max_oe - min_oe)
    
    def calculate_defensive_score(self, row):
        """Calculate defensive efficiency score (0-100)"""
        # Use adjusted defensive efficiency (lower is better)
        # Normalize to 0-100 scale where best defense = 100
        max_de = self.rankings['AdjDE'].max()
        min_de = self.rankings['AdjDE'].min()
        
        # Invert because lower defensive rating is better
        return 100 * (max_de - row['AdjDE']) / (max_de - min_de)
    
    def calculate_momentum_score(self, team_name):
        """
        Calculate recent performance trend
        For now, we'll use a combination of factors as proxy
        In a full implementation, this would analyze last 5-10 games
        """
        # Find the team in our data
        team_row = self.rankings[self.rankings['Team'] == team_name]
        
        if len(team_row) == 0:
            return 50  # Default middle score
        
        # Use ranking position as a simple proxy
        # Teams ranked higher are likely playing better recently
        rank = team_row.iloc[0]['AdjEM_Rank']
        
        # Convert rank to 0-100 score (1st = 100, last = 0)
        total_teams = len(self.rankings)
        momentum_score = 100 * (total_teams - rank) / (total_teams - 1)
        
        # Add some randomness to simulate actual momentum analysis
        # In reality, you'd analyze recent game results here
        momentum_score = momentum_score * 0.8 + 20  # Compress to 20-100 range
        
        return momentum_score
    
    def calculate_schedule_strength_score(self, row):
        """Calculate strength of schedule score"""
        # Power conference teams generally play tougher schedules
        power_conferences = ['SEC', 'B12', 'B10', 'ACC', 'BE']
        
        # Base score on conference
        if row['Conference'] in power_conferences:
            base_score = 80
        elif row['Conference'] in ['Amer', 'A10', 'MWC', 'WCC']:
            base_score = 65
        else:
            base_score = 50
        
        # Adjust based on overall ranking (better teams usually play tougher schedules)
        rank_adjustment = (100 - row['AdjEM_Rank']) / 10
        
        return min(100, base_score + rank_adjustment)
    
    def calculate_dominance_score(self, row):
        """Calculate how much team dominates (margin of victory)"""
        # Use the efficiency margin as proxy
        margin = row['AdjOE'] - row['AdjDE']
        
        # Normalize to 0-100
        all_margins = self.rankings['AdjOE'] - self.rankings['AdjDE']
        max_margin = all_margins.max()
        min_margin = all_margins.min()
        
        return 100 * (margin - min_margin) / (max_margin - min_margin)
    
    def calculate_weighted_score(self, row):
        """Calculate the final weighted score for a team"""
        scores = {
            'offensive_efficiency': self.calculate_offensive_score(row),
            'defensive_efficiency': self.calculate_defensive_score(row),
            'momentum': self.calculate_momentum_score(row['Team']),
            'schedule_strength': self.calculate_schedule_strength_score(row),
            'dominance': self.calculate_dominance_score(row)
        }
        
        # Calculate weighted sum
        total_score = 0
        for factor, score in scores.items():
            total_score += self.weights[factor] * score
            
        return total_score, scores
    
    def generate_rankings(self):
        """Generate the weighted power rankings"""
        print("\nCalculating weighted scores...")
        
        # Calculate scores for each team
        results = []
        for idx, row in self.rankings.iterrows():
            total_score, component_scores = self.calculate_weighted_score(row)
            
            result = {
                'Team': row['Team'],
                'Conference': row['Conference'],
                'Weighted_Score': total_score,
                'KenPom_Rank': row['AdjEM_Rank'],
                'AdjEM': row['AdjEM'],
                'AdjOE': row['AdjOE'],
                'AdjDE': row['AdjDE']
            }
            
            # Add component scores
            for factor, score in component_scores.items():
                result[f'{factor}_score'] = score
                
            results.append(result)
        
        # Create DataFrame and sort by weighted score
        self.results_df = pd.DataFrame(results)
        self.results_df = self.results_df.sort_values('Weighted_Score', ascending=False)
        self.results_df['Weighted_Rank'] = range(1, len(self.results_df) + 1)
        
        # Calculate rank difference from KenPom
        self.results_df['Rank_Diff'] = self.results_df['KenPom_Rank'] - self.results_df['Weighted_Rank']
        
        return self.results_df
    
    def display_top_teams(self, n=25):
        """Display the top N teams with their rankings"""
        print(f"\n{'='*100}")
        print(f"TOP {n} TEAMS - WEIGHTED POWER RANKINGS")
        print(f"{'='*100}")
        print(f"Current Weights: {self.weights}")
        print(f"{'-'*100}")
        print(f"{'Rank':<6}{'Team':<20}{'Conf':<8}{'Score':<8}{'KP Rank':<10}{'Diff':<8}{'AdjEM':<8}")
        print(f"{'-'*100}")
        
        top_teams = self.results_df.head(n)
        for idx, row in top_teams.iterrows():
            rank_diff = row['Rank_Diff']
            diff_symbol = '↑' if rank_diff > 0 else '↓' if rank_diff < 0 else '='
            
            print(f"{row['Weighted_Rank']:<6}{row['Team']:<20}{row['Conference']:<8}"
                  f"{row['Weighted_Score']:<8.2f}{row['KenPom_Rank']:<10}"
                  f"{diff_symbol}{abs(rank_diff):<7}{row['AdjEM']:<8.2f}")
    
    def show_team_breakdown(self, team_name):
        """Show detailed score breakdown for a specific team"""
        team_data = self.results_df[self.results_df['Team'] == team_name]
        
        if len(team_data) == 0:
            print(f"Team '{team_name}' not found")
            return
            
        row = team_data.iloc[0]
        
        print(f"\n{'='*60}")
        print(f"DETAILED BREAKDOWN: {team_name}")
        print(f"{'='*60}")
        print(f"Overall Rank: #{row['Weighted_Rank']} (Score: {row['Weighted_Score']:.2f})")
        print(f"KenPom Rank: #{row['KenPom_Rank']}")
        print(f"{'-'*60}")
        print(f"{'Component':<25}{'Score':<10}{'Weight':<10}{'Contribution':<15}")
        print(f"{'-'*60}")
        
        for factor in self.weights.keys():
            score = row[f'{factor}_score']
            weight = self.weights[factor]
            contribution = score * weight
            print(f"{factor.replace('_', ' ').title():<25}{score:<10.2f}{weight:<10.2%}{contribution:<15.2f}")
    
    def find_biggest_movers(self, n=5):
        """Find teams that moved the most compared to KenPom"""
        print(f"\n{'='*60}")
        print("BIGGEST MOVERS VS KENPOM")
        print(f"{'='*60}")
        
        # Biggest risers
        risers = self.results_df.nlargest(n, 'Rank_Diff')
        print(f"\nTop {n} Risers:")
        for idx, row in risers.iterrows():
            print(f"{row['Team']:20} #{row['KenPom_Rank']} → #{row['Weighted_Rank']} (↑{row['Rank_Diff']})")
        
        # Biggest fallers
        fallers = self.results_df.nsmallest(n, 'Rank_Diff')
        print(f"\nTop {n} Fallers:")
        for idx, row in fallers.iterrows():
            print(f"{row['Team']:20} #{row['KenPom_Rank']} → #{row['Weighted_Rank']} (↓{abs(row['Rank_Diff'])})")
    
    def save_rankings(self, filename=None):
        """Save rankings to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'data/weighted_rankings_{timestamp}.csv'
            
        self.results_df.to_csv(filename, index=False)
        print(f"\nRankings saved to: {filename}")
        
        # Also save as 'latest'
        self.results_df.to_csv('data/weighted_rankings_latest.csv', index=False)

# Example usage
if __name__ == "__main__":
    # Create model with new weights
    model = WeightedPowerRankingModel()
    
    # Load the data
    model.load_data()
    
    # Generate rankings
    rankings = model.generate_rankings()
    
    # Display top 25
    model.display_top_teams(25)
    
    # Find biggest movers
    model.find_biggest_movers(5)
    
    # Show detailed breakdown for a few interesting teams
    print("\n" + "="*60)
    print("SAMPLE TEAM BREAKDOWNS")
    print("="*60)
    
    # Show #1 team
    top_team = rankings.iloc[0]['Team']
    model.show_team_breakdown(top_team)
    
    # Save the rankings
    model.save_rankings()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print("Your weighted rankings have been saved to:")
    print("- data/weighted_rankings_latest.csv")
    print("\nKey insights:")
    print(f"- Your #1 team: {rankings.iloc[0]['Team']}")
    print(f"- KenPom's #1: {rankings[rankings['KenPom_Rank'] == 1].iloc[0]['Team']}")
    print(f"- Average rank difference: {abs(rankings['Rank_Diff']).mean():.1f} spots")