"""
Final Predictive Model - Clean Version
Removed flawed star power metric, redistributed weights
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class FinalPredictiveModel:
    def __init__(self):
        """Initialize with refined weights"""
        self.weights = {
            'defensive_rating': 0.30,      
            'offensive_rating': 0.30,      # Increased to 30%
            'recent_performance': 0.20,    
            'experience': 0.15,            # Back to 15%
            'pace_control': 0.05           
        }
        
        print("Final Predictive Power Ranking Model")
        print("="*60)
        print("Philosophy: Balanced excellence wins games")
        print("Key insight: Elite teams can overcome youth with talent")
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
        """Defense is 30% - most important factor"""
        all_def = self.data['AdjDE']
        
        # Lower defensive rating is better, so invert
        def_percentile = (all_def > team_row['AdjDE']).sum() / len(all_def) * 100
        
        # Bonus for elite defenses (top 10)
        if team_row['AdjDE.Rank'] <= 10:
            def_percentile = min(100, def_percentile + 5)
        elif team_row['AdjDE.Rank'] <= 25:
            def_percentile = min(100, def_percentile + 2)
            
        return def_percentile
    
    def calculate_offensive_rating(self, team_row):
        """Offense is 25% - slightly less than defense"""
        all_off = self.data['AdjOE']
        
        # Higher offensive rating is better
        off_percentile = (team_row['AdjOE'] > all_off).sum() / len(all_off) * 100
        
        # Bonus for elite offenses
        if team_row['AdjOE.Rank'] <= 10:
            off_percentile = min(100, off_percentile + 4)
        elif team_row['AdjOE.Rank'] <= 25:
            off_percentile = min(100, off_percentile + 2)
            
        return off_percentile
    
    def calculate_recent_performance(self, team_name):
        """Recent form - 20% - based on current ranking"""
        team_row = self.data[self.data['Team'] == team_name].iloc[0]
        rank = team_row['AdjEM_Rank']
        
        # Top teams are likely in good form
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
        """Experience - 20% - proven to matter (0.637 correlation)"""
        exp_value = team_row['Experience']
        all_exp = self.data['Experience']
        
        # Convert to percentile
        exp_percentile = (team_row['Experience'] > all_exp).sum() / len(all_exp) * 100
        
        # Bonuses for veteran teams
        if exp_value >= 3.0:  # Very experienced
            exp_percentile = min(100, exp_percentile + 10)
        elif exp_value >= 2.5:
            exp_percentile = min(100, exp_percentile + 5)
        
        # Penalty for very young teams
        if exp_value < 1.5:
            exp_percentile = max(0, exp_percentile - 10)
        elif exp_value < 2.0:
            exp_percentile = max(0, exp_percentile - 5)
            
        return exp_percentile
    
    def calculate_pace_control(self, team_row):
        """Pace Control - 5% - can play fast or slow"""
        # Get tempo rank with proper column name
        if 'Tempo-Adj.Rank' in team_row:
            tempo_rank = team_row['Tempo-Adj.Rank']
        else:
            return 50  # Default if not found
        
        # Teams at extremes can control pace
        if tempo_rank <= 30 or tempo_rank >= 335:
            pace_score = 90  # Very fast or very slow - they dictate pace
        elif tempo_rank <= 60 or tempo_rank >= 305:
            pace_score = 75
        elif tempo_rank <= 100 or tempo_rank >= 265:
            pace_score = 60
        else:
            pace_score = 45  # Middle pace - less control
        
        # Elite teams get a bonus regardless
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
        print(f"\n{'='*110}")
        print("FINAL PREDICTIVE POWER RANKINGS")
        print(f"{'='*110}")
        print(f"{'Rank':<6}{'Team':<20}{'Conf':<8}{'Score':<8}{'Def':<8}{'Off':<8}{'Exp':<6}{'Form':<6}{'KP':<6}{'Change':<10}")
        print(f"{'-'*110}")
        
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
                  f"{row['Experience']:<6.2f}{row['recent_performance_score']:<6.0f}"
                  f"{row['KenPom_Rank']:<6.0f}{symbol:<10}")
    
    def show_factor_impact(self):
        """Show how each factor impacts the rankings"""
        print(f"\n{'='*80}")
        print("FACTOR IMPACT ANALYSIS")
        print(f"{'='*80}")
        
        # Show correlation of each factor with final ranking
        factors = ['defensive_rating_score', 'offensive_rating_score', 
                  'recent_performance_score', 'experience_score', 'pace_control_score']
        
        print("\nTop 5 teams by each factor:")
        for factor in factors:
            print(f"\n{factor.upper().replace('_', ' ').replace(' SCORE', '')}:")
            top_5 = self.results_df.nlargest(5, factor)[['Team', factor, 'Final_Rank']]
            for idx, row in top_5.iterrows():
                print(f"  {row['Team']:<20} Score: {row[factor]:<6.1f} (Rank #{row['Final_Rank']})")
    
    def show_biggest_movers(self):
        """Show teams that moved the most"""
        print(f"\n{'='*80}")
        print("BIGGEST MOVERS vs KENPOM")
        print(f"{'='*80}")
        
        # Biggest risers
        print("\nBiggest Risers:")
        risers = self.results_df.nlargest(10, 'Rank_Change')
        for idx, row in risers.iterrows():
            print(f"{row['Team']:<20} ↑{row['Rank_Change']} (#{row['KenPom_Rank']} → #{row['Final_Rank']})")
        
        # Biggest fallers
        print("\nBiggest Fallers:")
        fallers = self.results_df.nsmallest(10, 'Rank_Change')
        for idx, row in fallers.iterrows():
            print(f"{row['Team']:<20} ↓{abs(row['Rank_Change'])} (#{row['KenPom_Rank']} → #{row['Final_Rank']})")

# Run the model
if __name__ == "__main__":
    model = FinalPredictiveModel()
    model.load_all_data()
    
    # Generate rankings
    rankings = model.generate_rankings()
    
    # Display results
    model.display_rankings(30)
    model.show_factor_impact()
    model.show_biggest_movers()
    
    # Save final rankings
    rankings.to_csv('data/final_predictive_rankings.csv', index=False)
    print("\n\nFinal rankings saved to data/final_predictive_rankings.csv")
    
    # Summary
    print(f"\n{'='*80}")
    print("MODEL SUMMARY")
    print(f"{'='*80}")
    print("This model predicts who would win on a neutral court by considering:")
    print("- Defensive ability (30%) - Elite defense travels")
    print("- Offensive ability (30%) - You need to score to win")  
    print("- Recent performance (20%) - Current form matters")
    print("- Experience (15%) - Veterans perform under pressure")
    print("- Pace control (5%) - Dictating tempo provides an edge")