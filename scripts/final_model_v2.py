"""
Final Predictive Model V2 - With Proper Experience Handling
Duke and other elite young teams should rank appropriately
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class FinalPredictiveModelV2:
    def __init__(self):
        """Initialize with balanced weights"""
        self.weights = {
            'defensive_rating': 0.30,      
            'offensive_rating': 0.30,      
            'recent_performance': 0.20,    
            'experience': 0.15,            
            'pace_control': 0.05           
        }
        
        print("Final Predictive Power Ranking Model V2")
        print("="*60)
        print("Philosophy: Elite talent can overcome youth")
        print("\nWeights:")
        for factor, weight in self.weights.items():
            print(f"  {factor}: {weight:.0%}")
    
    def load_all_data(self, data_dir='data'):
        """Load all necessary data"""
        print("\nLoading data...")
        
        # Core rankings
        self.rankings = pd.read_csv(f'{data_dir}/kenpom_rankings_latest.csv')
        
        # Personnel data for experience
        self.personnel = pd.read_csv(f'{data_dir}/kenpom_height_experience_latest.csv')
        
        # Tempo data for pace control
        self.tempo = pd.read_csv(f'{data_dir}/kenpom_tempo_stats_latest.csv')
        
        # Merge all data
        self.data = pd.merge(self.rankings, self.personnel, on='Team', how='inner', suffixes=('', '_pers'))
        self.data = pd.merge(self.data, self.tempo, on='Team', how='inner', suffixes=('', '_tempo'))
        
        # Drop duplicate Conference columns
        conf_cols = [col for col in self.data.columns if 'Conference' in col and col != 'Conference']
        self.data = self.data.drop(columns=conf_cols)
        
        print(f"Loaded data for {len(self.data)} teams")
        
    def calculate_defensive_rating(self, team_row):
        """Defense is 30%"""
        all_def = self.data['AdjDE']
        def_percentile = (all_def > team_row['AdjDE']).sum() / len(all_def) * 100
        
        if team_row['AdjDE.Rank'] <= 10:
            def_percentile = min(100, def_percentile + 5)
        elif team_row['AdjDE.Rank'] <= 25:
            def_percentile = min(100, def_percentile + 2)
            
        return def_percentile
    
    def calculate_offensive_rating(self, team_row):
        """Offense is 30%"""
        all_off = self.data['AdjOE']
        off_percentile = (team_row['AdjOE'] > all_off).sum() / len(all_off) * 100
        
        if team_row['AdjOE.Rank'] <= 10:
            off_percentile = min(100, off_percentile + 4)
        elif team_row['AdjOE.Rank'] <= 25:
            off_percentile = min(100, off_percentile + 2)
            
        return off_percentile
    
    def calculate_recent_performance(self, team_name):
        """Recent form - 20%"""
        team_row = self.data[self.data['Team'] == team_name].iloc[0]
        rank = team_row['AdjEM_Rank']
        
        if rank <= 5:
            return 98
        elif rank <= 10:
            return 93
        elif rank <= 25:
            return 85
        elif rank <= 50:
            return 75
        elif rank <= 75:
            return 65
        elif rank <= 100:
            return 55
        elif rank <= 150:
            return 45
        else:
            return 35
    
    def calculate_experience(self, team_row):
        """Experience - 15% - FIXED FOR ELITE TEAMS"""
        exp_value = team_row['Experience']
        team_rank = team_row['AdjEM_Rank']
        
        # For ELITE teams (top 10), experience barely matters
        if team_rank <= 10:
            # Elite teams get 80-100 range regardless of experience
            if exp_value >= 2.5:
                return 100  # Veteran elite team
            elif exp_value >= 2.0:
                return 90   # Normal elite team
            else:
                return 80   # Young elite team - minimal penalty
                
        # For VERY GOOD teams (11-25), slight impact
        elif team_rank <= 25:
            if exp_value >= 2.5:
                return 95
            elif exp_value >= 2.0:
                return 80
            else:
                return 70   # Some penalty but not severe
                
        # For GOOD teams (26-50), moderate impact
        elif team_rank <= 50:
            if exp_value >= 2.5:
                return 90
            elif exp_value >= 2.0:
                return 70
            elif exp_value >= 1.5:
                return 55
            else:
                return 40
                
        # For AVERAGE teams (51-100), significant impact
        elif team_rank <= 100:
            if exp_value >= 3.0:
                return 90
            elif exp_value >= 2.5:
                return 75
            elif exp_value >= 2.0:
                return 60
            elif exp_value >= 1.5:
                return 45
            else:
                return 30
                
        # For BAD teams (101+), experience is crucial
        else:
            if exp_value >= 3.0:
                return 85
            elif exp_value >= 2.5:
                return 70
            elif exp_value >= 2.0:
                return 50
            elif exp_value >= 1.5:
                return 30
            else:
                return 10   # Young bad teams are terrible
    
    def calculate_pace_control(self, team_row):
        """Pace Control - 5%"""
        if 'Tempo-Adj.Rank' in team_row:
            tempo_rank = team_row['Tempo-Adj.Rank']
        else:
            return 50
        
        if tempo_rank <= 30 or tempo_rank >= 335:
            pace_score = 90
        elif tempo_rank <= 60 or tempo_rank >= 305:
            pace_score = 75
        elif tempo_rank <= 100 or tempo_rank >= 265:
            pace_score = 60
        else:
            pace_score = 45
        
        if team_row['AdjEM_Rank'] <= 25:
            pace_score = min(100, pace_score + 10)
            
        return pace_score
    
    def calculate_total_score(self, team_row):
        """Calculate final predictive score"""
        team_name = team_row['Team']
        
        scores = {
            'defensive_rating': self.calculate_defensive_rating(team_row),
            'offensive_rating': self.calculate_offensive_rating(team_row),
            'recent_performance': self.calculate_recent_performance(team_name),
            'experience': self.calculate_experience(team_row),
            'pace_control': self.calculate_pace_control(team_row)
        }
        
        # Calculate weighted total
        total = sum(scores[factor] * self.weights[factor] for factor in scores)
        
        return total, scores
    
    def generate_rankings(self):
        """Generate final rankings"""
        print("\nCalculating final predictive scores...")
        
        results = []
        for idx, row in self.data.iterrows():
            total_score, component_scores = self.calculate_total_score(row)
            
            result = {
                'Team': row['Team'],
                'Conference': row['Conference'],
                'Final_Score': total_score,
                'Experience': row['Experience'],
                'Experience_Score': component_scores['experience'],
                'KenPom_Rank': row['AdjEM_Rank'],
                'AdjEM': row['AdjEM'],
                'AdjOE': row['AdjOE'],
                'AdjDE': row['AdjDE'],
                'AdjOE_Rank': row['AdjOE.Rank'],
                'AdjDE_Rank': row['AdjDE.Rank']
            }
            
            # Add component scores
            for factor, score in component_scores.items():
                result[f'{factor}_score'] = score
            
            results.append(result)
        
        # Create and sort dataframe
        self.results_df = pd.DataFrame(results)
        self.results_df = self.results_df.sort_values('Final_Score', ascending=False)
        self.results_df['Final_Rank'] = range(1, len(self.results_df) + 1)
        self.results_df['Rank_Change'] = self.results_df['KenPom_Rank'] - self.results_df['Final_Rank']
        
        return self.results_df
    
    def display_rankings(self, n=30):
        """Display top teams"""
        print(f"\n{'='*120}")
        print("FINAL PREDICTIVE POWER RANKINGS V2")
        print(f"{'='*120}")
        print(f"{'Rank':<6}{'Team':<20}{'Conf':<8}{'Score':<8}{'Def':<8}{'Off':<8}{'Exp':<6}{'ExpSc':<8}{'KP':<6}{'Change':<10}")
        print(f"{'-'*120}")
        
        for idx, row in self.results_df.head(n).iterrows():
            change = row['Rank_Change']
            if change > 0:
                symbol = f"↑{change}"
            elif change < 0:
                symbol = f"↓{abs(change)}"
            else:
                symbol = "="
            
            print(f"{row['Final_Rank']:<6}{row['Team']:<20}{row['Conference']:<8}"
                  f"{row['Final_Score']:<8.1f}"
                  f"#{row['AdjDE_Rank']:<7.0f}#{row['AdjOE_Rank']:<7.0f}"
                  f"{row['Experience']:<6.2f}{row['Experience_Score']:<8.0f}"
                  f"{row['KenPom_Rank']:<6.0f}{symbol:<10}")

# Run the model
if __name__ == "__main__":
    model = FinalPredictiveModelV2()
    model.load_all_data()
    
    # Generate rankings
    rankings = model.generate_rankings()
    
    # Display results
    model.display_rankings(30)
    
    # Check specific teams
    print(f"\n{'='*80}")
    print("YOUNG ELITE TEAMS CHECK")
    print(f"{'='*80}")
    
    young_elites = ['Duke', 'Michigan St.', 'Maryland', 'Purdue']
    for team in young_elites:
        team_data = rankings[rankings['Team'] == team].iloc[0]
        print(f"{team:<20} Exp: {team_data['Experience']:.2f} yrs, "
              f"Exp Score: {team_data['Experience_Score']:.0f}, "
              f"Rank: #{team_data['Final_Rank']}")
    
    # Save
    rankings.to_csv('data/final_predictive_rankings_v2.csv', index=False)
    print("\nRankings saved to data/final_predictive_rankings_v2.csv")