"""
Defense-Focused Predictive Model
Key changes: Defense weighted more heavily, removed injury placeholder
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class DefenseFocusedPredictiveModel:
    def __init__(self):
        """
        Initialize with defense-focused weights
        """
        self.weights = {
            'defensive_rating': 0.30,       # NEW: Pure defensive efficiency
            'offensive_rating': 0.20,       # NEW: Pure offensive efficiency  
            'recent_performance': 0.20,     # Recent form still matters
            'consistency': 0.15,            # Reliable teams win in March
            'experience': 0.10,             # Veterans handle pressure
            'pace_control': 0.05            # Can they dictate tempo?
        }
        
        print("Defense-Focused Predictive Power Ranking Model")
        print("="*50)
        print("Philosophy: Defense wins championships!")
        print("\nWeights:")
        for factor, weight in self.weights.items():
            print(f"  {factor}: {weight:.0%}")
    
    def load_data(self, data_dir='data'):
        """Load all necessary data"""
        print("\nLoading data...")
        
        self.rankings = pd.read_csv(f'{data_dir}/kenpom_rankings_latest.csv')
        self.four_factors = pd.read_csv(f'{data_dir}/kenpom_four_factors_latest.csv')
        self.tempo_stats = pd.read_csv(f'{data_dir}/kenpom_tempo_stats_latest.csv')
        
        print(f"Loaded data for {len(self.rankings)} teams")
    
    def calculate_defensive_rating(self, team_row):
        """
        Pure defensive efficiency score
        Lower AdjDE is better, so we invert
        """
        # Get all defensive ratings for normalization
        all_def = self.rankings['AdjDE']
        
        # Invert: best defense (lowest number) gets highest score
        # Using percentile ranking
        def_percentile = (all_def > team_row['AdjDE']).sum() / len(all_def) * 100
        
        # Give bonus to truly elite defenses (top 10)
        if team_row['AdjDE.Rank'] <= 10:
            def_percentile = min(100, def_percentile + 5)
        
        return def_percentile
    
    def calculate_offensive_rating(self, team_row):
        """
        Pure offensive efficiency score
        """
        # Get all offensive ratings
        all_off = self.rankings['AdjOE']
        
        # Higher is better for offense
        off_percentile = (team_row['AdjOE'] > all_off).sum() / len(all_off) * 100
        
        # Elite offense bonus
        if team_row['AdjOE.Rank'] <= 10:
            off_percentile = min(100, off_percentile + 3)
        
        return off_percentile
    
    def calculate_recent_performance(self, team_name):
        """
        Teams playing well recently
        """
        team_row = self.rankings[self.rankings['Team'] == team_name].iloc[0]
        rank = team_row['AdjEM_Rank']
        
        # Top teams are likely hot
        if rank <= 10:
            return 95
        elif rank <= 25:
            return 85
        elif rank <= 50:
            return 75
        elif rank <= 75:
            return 65
        elif rank <= 100:
            return 55
        else:
            return 45
    
    def calculate_consistency(self, team_name):
        """
        Consistent teams = balanced offense/defense
        """
        team_row = self.rankings[self.rankings['Team'] == team_name].iloc[0]
        
        # Get ranks
        off_rank = team_row['AdjOE.Rank']
        def_rank = team_row['AdjDE.Rank']
        
        # Calculate balance
        rank_diff = abs(off_rank - def_rank)
        
        # Convert to score
        if rank_diff <= 10:
            return 95  # Extremely balanced
        elif rank_diff <= 25:
            return 85
        elif rank_diff <= 50:
            return 70
        elif rank_diff <= 100:
            return 55
        else:
            return 40  # Very unbalanced
    
    def calculate_experience(self, team_name):
        """
        Veteran teams and proven programs
        """
        team_row = self.rankings[self.rankings['Team'] == team_name].iloc[0]
        
        # Blue bloods and consistent top programs
        elite_programs = ['Duke', 'Kansas', 'Kentucky', 'North Carolina', 'UCLA',
                         'Michigan St.', 'Gonzaga', 'Villanova', 'Louisville']
        
        # Power conferences typically have older players
        power_conf = ['SEC', 'B12', 'B10', 'ACC', 'BE']
        
        if team_name in elite_programs:
            base_score = 90
        elif team_row['Conference'] in power_conf:
            base_score = 75
        else:
            base_score = 60
        
        # Top ranked teams likely have good players
        if team_row['AdjEM_Rank'] <= 25:
            base_score = min(100, base_score + 10)
        
        return base_score
    
    def calculate_pace_control(self, team_name):
        """
        Teams that can control tempo
        Great defenses often slow games down
        """
        team_tempo = self.tempo_stats[self.tempo_stats['Team'] == team_name]
        if len(team_tempo) == 0:
            return 50
        
        tempo_rank = team_tempo.iloc[0]['Tempo-Adj.Rank']
        
        # Very fast or very slow can control pace
        if tempo_rank <= 50 or tempo_rank >= 300:
            pace_score = 80
        elif tempo_rank <= 100 or tempo_rank >= 250:
            pace_score = 70
        else:
            pace_score = 60
        
        # Elite defensive teams get pace bonus
        team_row = self.rankings[self.rankings['Team'] == team_name].iloc[0]
        if team_row['AdjDE.Rank'] <= 25:
            pace_score = min(100, pace_score + 10)
        
        return pace_score
    
    def calculate_total_score(self, team_row):
        """Calculate total predictive score"""
        team_name = team_row['Team']
        
        scores = {
            'defensive_rating': self.calculate_defensive_rating(team_row),
            'offensive_rating': self.calculate_offensive_rating(team_row),
            'recent_performance': self.calculate_recent_performance(team_name),
            'consistency': self.calculate_consistency(team_name),
            'experience': self.calculate_experience(team_name),
            'pace_control': self.calculate_pace_control(team_name)
        }
        
        # Calculate weighted total
        total = sum(scores[factor] * self.weights[factor] for factor in scores)
        
        return total, scores
    
    def generate_rankings(self):
        """Generate the rankings"""
        print("\nCalculating defense-focused predictive scores...")
        
        results = []
        for idx, row in self.rankings.iterrows():
            total_score, component_scores = self.calculate_total_score(row)
            
            result = {
                'Team': row['Team'],
                'Conference': row['Conference'],
                'Defense_Focused_Score': total_score,
                'KenPom_Rank': row['AdjEM_Rank'],
                'AdjOE_Rank': row['AdjOE.Rank'],
                'AdjDE_Rank': row['AdjDE.Rank'],
                'AdjEM': row['AdjEM']
            }
            
            # Add components
            for factor, score in component_scores.items():
                result[f'{factor}_score'] = score
            
            results.append(result)
        
        # Create and sort dataframe
        self.results_df = pd.DataFrame(results)
        self.results_df = self.results_df.sort_values('Defense_Focused_Score', ascending=False)
        self.results_df['Defense_Rank'] = range(1, len(self.results_df) + 1)
        self.results_df['Rank_Diff'] = self.results_df['KenPom_Rank'] - self.results_df['Defense_Rank']
        
        return self.results_df
    
    def display_rankings(self, n=25):
        """Display top teams"""
        print(f"\n{'='*100}")
        print("DEFENSE-FOCUSED PREDICTIVE RANKINGS")
        print(f"{'='*100}")
        print(f"{'Rank':<6}{'Team':<20}{'Conf':<8}{'Score':<8}{'Def':<8}{'Off':<8}{'KP':<6}{'Diff':<8}")
        print(f"{'-'*100}")
        
        for idx, row in self.results_df.head(n).iterrows():
            diff = row['Rank_Diff']
            symbol = '↑' if diff > 0 else '↓' if diff < 0 else '='
            
            print(f"{row['Defense_Rank']:<6}{row['Team']:<20}{row['Conference']:<8}"
                  f"{row['Defense_Focused_Score']:<8.1f}"
                  f"#{row['AdjDE_Rank']:<7.0f}#{row['AdjOE_Rank']:<7.0f}"
                  f"{row['KenPom_Rank']:<6.0f}{symbol}{abs(diff):<7.0f}")
    
    def show_defense_elite(self):
        """Show how defensive teams are rewarded"""
        print(f"\n{'='*80}")
        print("TOP 10 DEFENSES AND THEIR RANKINGS")
        print(f"{'='*80}")
        
        # Get top 10 defenses
        top_d = self.rankings.nsmallest(10, 'AdjDE')
        
        for idx, team in top_d.iterrows():
            team_name = team['Team']
            our_rank = self.results_df[self.results_df['Team'] == team_name].iloc[0]['Defense_Rank']
            kp_rank = team['AdjEM_Rank']
            
            print(f"{team_name:<20} Defense: #{team['AdjDE.Rank']:<3.0f} "
                  f"Our Rank: #{our_rank:<3.0f} KenPom: #{kp_rank:<3.0f} "
                  f"{'↑' if kp_rank > our_rank else '↓'}{abs(kp_rank - our_rank)}")

# Run the model
if __name__ == "__main__":
    model = DefenseFocusedPredictiveModel()
    model.load_data()
    
    # Generate rankings
    rankings = model.generate_rankings()
    
    # Show top 25
    model.display_rankings(25)
    
    # Show how defense is valued
    model.show_defense_elite()
    
    # Compare methodologies
    print(f"\n{'='*80}")
    print("METHODOLOGY COMPARISON")
    print(f"{'='*80}")
    print("\nOriginal Model:")
    print("- 45% Adjusted Efficiency (Offense - Defense)")
    print("- Treated offense and defense equally")
    print("\nDefense-Focused Model:")
    print("- 30% Pure Defense")
    print("- 20% Pure Offense")
    print("- Defense weighted 50% more than offense")
    print("\nResult: Elite defensive teams should rise significantly")
    
    # Save
    rankings.to_csv('data/defense_focused_rankings_latest.csv', index=False)
    print("\nRankings saved!")