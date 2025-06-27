"""
NCAA Basketball Hybrid Power Ranking Model
Combines Kenpom efficiency metrics with actual game results
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class HybridPowerRankingModel:
    def __init__(self, base_weight=0.7, results_weight=0.3):
        """
        Initialize the hybrid model
        base_weight: Weight for Kenpom efficiency metrics (default 70%)
        results_weight: Weight for actual game results (default 30%)
        """
        self.base_weight = base_weight
        self.results_weight = results_weight
        
        # Validate weights sum to 1.0
        total = base_weight + results_weight
        if abs(total - 1.0) > 0.001:
            print(f"Warning: Weights sum to {total}, normalizing to 1.0")
            self.base_weight = base_weight / total
            self.results_weight = results_weight / total
            
        print(f"Hybrid Model Weights:")
        print(f"- Kenpom Base Metrics: {self.base_weight:.0%}")
        print(f"- Game Results: {self.results_weight:.0%}")
    
    def load_data(self, data_dir='data'):
        """Load all necessary data"""
        print("\nLoading data...")
        
        # Load Kenpom data
        self.rankings = pd.read_csv(f'{data_dir}/kenpom_rankings_latest.csv')
        self.four_factors = pd.read_csv(f'{data_dir}/kenpom_four_factors_latest.csv')
        
        # Load game data
        try:
            self.upset_games = pd.read_csv(f'{data_dir}/kenpom_upset_games_latest.csv')
            self.exciting_games = pd.read_csv(f'{data_dir}/kenpom_exciting_games_latest.csv')
            print(f"Loaded {len(self.upset_games)} upset games")
            print(f"Loaded {len(self.exciting_games)} exciting games")
        except:
            self.upset_games = None
            self.exciting_games = None
            print("Warning: Could not load game data")
            
        print(f"Loaded data for {len(self.rankings)} teams")
    
    def calculate_base_score(self, team_row):
        """Calculate base score from Kenpom efficiency metrics"""
        # Normalize AdjEM to 0-100 scale
        all_adj_em = self.rankings['AdjEM']
        max_em = all_adj_em.max()
        min_em = all_adj_em.min()
        
        base_score = 100 * (team_row['AdjEM'] - min_em) / (max_em - min_em)
        return base_score
    
    def analyze_game_results(self, team_name):
        """
        Analyze actual game results for a team
        Returns a results score (0-100) based on:
        - Upset wins (beating higher-ranked teams)
        - Avoiding upset losses
        - Margin of victory in big games
        """
        results_score = 50  # Default neutral score
        
        # Check upset games
        if self.upset_games is not None:
            # Find games where this team was involved
            team_upset_wins = 0
            team_upset_losses = 0
            
            for idx, game in self.upset_games.iterrows():
                # Parse game data (this depends on the actual format)
                # For now, we'll use a simplified approach
                game_text = str(game.to_dict())
                
                if team_name in game_text:
                    # Simple heuristic: if team appears early, they likely won
                    if game_text.index(team_name) < len(game_text) / 2:
                        team_upset_wins += 1
                    else:
                        team_upset_losses += 1
            
            # Adjust score based on upsets
            results_score += (team_upset_wins * 10)  # Bonus for upset wins
            results_score -= (team_upset_losses * 15)  # Penalty for upset losses
        
        # Check exciting/close games performance
        if self.exciting_games is not None:
            close_game_wins = 0
            close_game_total = 0
            
            for idx, game in self.exciting_games.iterrows():
                game_text = str(game.to_dict())
                if team_name in game_text:
                    close_game_total += 1
                    # Similar simple heuristic
                    if game_text.index(team_name) < len(game_text) / 2:
                        close_game_wins += 1
            
            # Clutch performance bonus
            if close_game_total > 0:
                clutch_rate = close_game_wins / close_game_total
                results_score += (clutch_rate - 0.5) * 20  # +/-10 points based on clutch
        
        # Cap score between 0 and 100
        results_score = max(0, min(100, results_score))
        
        return results_score
    
    def calculate_momentum_bonus(self, team_name):
        """
        Calculate momentum based on recent performance
        This is a simplified version - ideally would look at last 5-10 games
        """
        # For now, use ranking position as proxy
        team_row = self.rankings[self.rankings['Team'] == team_name]
        if len(team_row) == 0:
            return 0
        
        rank = team_row.iloc[0]['AdjEM_Rank']
        
        # Top 25 teams get momentum bonus
        if rank <= 25:
            return 10
        elif rank <= 50:
            return 5
        else:
            return 0
    
    def calculate_hybrid_score(self, team_row):
        """Calculate the final hybrid score for a team"""
        team_name = team_row['Team']
        
        # 1. Base Kenpom efficiency score
        base_score = self.calculate_base_score(team_row)
        
        # 2. Game results score
        results_score = self.analyze_game_results(team_name)
        
        # 3. Momentum bonus (small additional factor)
        momentum_bonus = self.calculate_momentum_bonus(team_name)
        
        # Combine scores
        hybrid_score = (self.base_weight * base_score + 
                       self.results_weight * results_score)
        
        # Add momentum bonus (capped at 5% of total)
        hybrid_score += min(5, momentum_bonus * 0.5)
        
        return {
            'hybrid_score': hybrid_score,
            'base_score': base_score,
            'results_score': results_score,
            'momentum_bonus': momentum_bonus
        }
    
    def generate_rankings(self):
        """Generate the hybrid power rankings"""
        print("\nCalculating hybrid scores...")
        
        results = []
        for idx, row in self.rankings.iterrows():
            scores = self.calculate_hybrid_score(row)
            
            result = {
                'Team': row['Team'],
                'Conference': row['Conference'],
                'Hybrid_Score': scores['hybrid_score'],
                'Base_Score': scores['base_score'],
                'Results_Score': scores['results_score'],
                'Momentum_Bonus': scores['momentum_bonus'],
                'KenPom_Rank': row['AdjEM_Rank'],
                'AdjEM': row['AdjEM'],
                'AdjOE': row['AdjOE'],
                'AdjDE': row['AdjDE']
            }
            results.append(result)
        
        # Create DataFrame and sort
        self.results_df = pd.DataFrame(results)
        self.results_df = self.results_df.sort_values('Hybrid_Score', ascending=False)
        self.results_df['Hybrid_Rank'] = range(1, len(self.results_df) + 1)
        
        # Calculate rank difference from KenPom
        self.results_df['Rank_Diff'] = self.results_df['KenPom_Rank'] - self.results_df['Hybrid_Rank']
        
        return self.results_df
    
    def display_top_teams(self, n=25):
        """Display the top N teams"""
        print(f"\n{'='*110}")
        print(f"TOP {n} TEAMS - HYBRID POWER RANKINGS")
        print(f"{'='*110}")
        print(f"Model: {self.base_weight:.0%} Kenpom + {self.results_weight:.0%} Game Results")
        print(f"{'-'*110}")
        print(f"{'Rank':<6}{'Team':<20}{'Conf':<8}{'Score':<8}{'Base':<8}{'Results':<10}{'KP Rank':<10}{'Diff':<8}{'AdjEM':<8}")
        print(f"{'-'*110}")
        
        top_teams = self.results_df.head(n)
        for idx, row in top_teams.iterrows():
            rank_diff = row['Rank_Diff']
            diff_symbol = '↑' if rank_diff > 0 else '↓' if rank_diff < 0 else '='
            
            print(f"{row['Hybrid_Rank']:<6}{row['Team']:<20}{row['Conference']:<8}"
                  f"{row['Hybrid_Score']:<8.1f}{row['Base_Score']:<8.1f}"
                  f"{row['Results_Score']:<10.1f}{row['KenPom_Rank']:<10}"
                  f"{diff_symbol}{abs(rank_diff):<7}{row['AdjEM']:<8.2f}")
    
    def show_interesting_movers(self):
        """Show teams that moved significantly due to game results"""
        print(f"\n{'='*80}")
        print("TEAMS MOST AFFECTED BY GAME RESULTS")
        print(f"{'='*80}")
        
        # Calculate impact of results on ranking
        self.results_df['Results_Impact'] = self.results_df['Results_Score'] - 50
        
        # Biggest beneficiaries
        print("\nBiggest Winners from Game Results:")
        winners = self.results_df.nlargest(5, 'Results_Impact')
        for idx, row in winners.iterrows():
            print(f"{row['Team']:20} Results Score: {row['Results_Score']:.1f} "
                  f"(+{row['Results_Impact']:.1f} boost)")
        
        # Biggest losers
        print("\nBiggest Losers from Game Results:")
        losers = self.results_df.nsmallest(5, 'Results_Impact')
        for idx, row in losers.iterrows():
            print(f"{row['Team']:20} Results Score: {row['Results_Score']:.1f} "
                  f"({row['Results_Impact']:.1f} penalty)")
    
    def compare_models(self, team_name):
        """Compare how a team ranks in different models"""
        team_data = self.results_df[self.results_df['Team'] == team_name]
        
        if len(team_data) == 0:
            print(f"Team '{team_name}' not found")
            return
            
        row = team_data.iloc[0]
        
        print(f"\n{'='*60}")
        print(f"MODEL COMPARISON: {team_name}")
        print(f"{'='*60}")
        print(f"Hybrid Rank: #{row['Hybrid_Rank']} (Score: {row['Hybrid_Score']:.1f})")
        print(f"KenPom Rank: #{row['KenPom_Rank']} (AdjEM: {row['AdjEM']:.2f})")
        print(f"Difference: {row['Rank_Diff']:+d} spots")
        print(f"\nScore Breakdown:")
        print(f"- Base Efficiency Score: {row['Base_Score']:.1f}/100")
        print(f"- Game Results Score: {row['Results_Score']:.1f}/100")
        print(f"- Momentum Bonus: +{row['Momentum_Bonus']:.1f}")
    
    def save_rankings(self, filename=None):
        """Save rankings to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'data/hybrid_rankings_{timestamp}.csv'
            
        self.results_df.to_csv(filename, index=False)
        print(f"\nRankings saved to: {filename}")
        
        # Also save as 'latest'
        self.results_df.to_csv('data/hybrid_rankings_latest.csv', index=False)

# Example usage
if __name__ == "__main__":
    # Create hybrid model (70% Kenpom, 30% Results)
    model = HybridPowerRankingModel(base_weight=0.7, results_weight=0.3)
    
    # Load data
    model.load_data()
    
    # Generate rankings
    rankings = model.generate_rankings()
    
    # Display top 25
    model.display_top_teams(25)
    
    # Show interesting movers
    model.show_interesting_movers()
    
    # Compare some interesting teams
    print("\n" + "="*80)
    print("DETAILED TEAM COMPARISONS")
    print("="*80)
    
    # Look at a few specific teams
    teams_to_check = ['Duke', 'Gonzaga', 'St. John\'s']
    for team in teams_to_check:
        model.compare_models(team)
    
    # Save rankings
    model.save_rankings()
    
    print("\n" + "="*80)
    print("EXPERIMENT WITH DIFFERENT WEIGHTINGS")
    print("="*80)
    
    # Try a more results-heavy model
    print("\nTrying 50/50 split between Kenpom and Results...")
    results_heavy = HybridPowerRankingModel(base_weight=0.5, results_weight=0.5)
    results_heavy.load_data()
    results_heavy.generate_rankings()
    print("\nTop 10 with 50/50 weighting:")
    results_heavy.display_top_teams(10)