"""
NCAA Basketball Predictive Power Ranking Model
Goal: Predict who would win on a neutral court tomorrow
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class PredictivePowerRankingModel:
    def __init__(self, weights=None):
        """
        Initialize predictive model with factors that actually predict game outcomes
        """
        if weights is None:
            self.weights = {
                'adjusted_efficiency': 0.45,    # Core efficiency (offense - defense)
                'recent_performance': 0.20,     # Last 5-10 games weighted more
                'consistency': 0.10,            # Teams that don't have high variance
                'pace_flexibility': 0.10,       # Can play fast or slow
                'experience': 0.05,             # Veteran teams perform better in big games
                'altitude_travel': 0.05,        # Home court and travel factors
                'injury_adjustment': 0.05       # Account for missing players
            }
        else:
            self.weights = weights
            
        # Normalize weights
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.001:
            for key in self.weights:
                self.weights[key] = self.weights[key] / total
                
        print("Predictive Power Ranking Model")
        print("="*50)
        print("Weights:")
        for factor, weight in self.weights.items():
            print(f"  {factor}: {weight:.1%}")
    
    def load_data(self, data_dir='data'):
        """Load all necessary data"""
        print("\nLoading data...")
        
        # Core data
        self.rankings = pd.read_csv(f'{data_dir}/kenpom_rankings_latest.csv')
        self.four_factors = pd.read_csv(f'{data_dir}/kenpom_four_factors_latest.csv')
        self.tempo_stats = pd.read_csv(f'{data_dir}/kenpom_tempo_stats_latest.csv')
        
        # Game data for recent performance
        try:
            self.games = pd.read_csv(f'{data_dir}/kenpom_exciting_games_latest.csv')
            self.upsets = pd.read_csv(f'{data_dir}/kenpom_upset_games_latest.csv')
        except:
            self.games = None
            self.upsets = None
            
        print(f"Loaded data for {len(self.rankings)} teams")
    
    def calculate_adjusted_efficiency(self, team_row):
        """
        Core efficiency metric with adjustments
        """
        # Base efficiency margin
        base_em = team_row['AdjOE'] - team_row['AdjDE']
        
        # Normalize to 0-100
        all_ems = self.rankings['AdjOE'] - self.rankings['AdjDE']
        em_normalized = 100 * (base_em - all_ems.min()) / (all_ems.max() - all_ems.min())
        
        # Adjust for extremes (teams with elite offense OR defense get small bonus)
        offense_percentile = 100 * (1 - team_row['AdjOE.Rank'] / len(self.rankings))
        defense_percentile = 100 * (1 - team_row['AdjDE.Rank'] / len(self.rankings))
        
        if offense_percentile > 95 or defense_percentile > 95:
            em_normalized += 2  # Small bonus for elite units
            
        return min(100, em_normalized)
    
    def calculate_recent_performance(self, team_name):
        """
        Weight recent games more heavily than early season
        For now, use ranking trajectory as proxy
        """
        team_row = self.rankings[self.rankings['Team'] == team_name].iloc[0]
        
        # Use current ranking as base
        current_rank = team_row['AdjEM_Rank']
        
        # Teams in top 50 are likely playing well recently
        if current_rank <= 10:
            recency_score = 90
        elif current_rank <= 25:
            recency_score = 80
        elif current_rank <= 50:
            recency_score = 70
        elif current_rank <= 100:
            recency_score = 60
        else:
            recency_score = 50
            
        # TODO: In real implementation, analyze last 5-10 games
        # Look at margin of victory, opponent strength, home/away
        
        return recency_score
    
    def calculate_consistency(self, team_name):
        """
        Consistent teams are more predictable and reliable
        High variance teams might have higher ceiling but lower floor
        """
        # Get team's four factors data
        team_ff = self.four_factors[self.four_factors['Team'] == team_name]
        
        if len(team_ff) == 0:
            return 50
            
        team_ff = team_ff.iloc[0]
        
        # Look at offensive and defensive ranks
        off_rank = team_ff['AdjOE.Rank']
        def_rank = team_ff['AdjDE.Rank']
        
        # Consistent teams have balanced offense/defense
        rank_diff = abs(off_rank - def_rank)
        
        if rank_diff < 20:
            consistency = 85  # Very balanced
        elif rank_diff < 50:
            consistency = 70  # Somewhat balanced
        elif rank_diff < 100:
            consistency = 55  # Unbalanced
        else:
            consistency = 40  # Very unbalanced
            
        return consistency
    
    def calculate_pace_flexibility(self, team_name):
        """
        Teams that can win at any pace are more dangerous
        """
        # Get tempo stats
        team_tempo = self.tempo_stats[self.tempo_stats['Team'] == team_name]
        
        if len(team_tempo) == 0:
            return 50
            
        team_tempo = team_tempo.iloc[0]
        tempo_rank = team_tempo['Tempo-Adj.Rank']
        
        # Teams in the middle can adjust better
        # Very fast or very slow teams might struggle to adapt
        if 100 <= tempo_rank <= 200:
            flexibility = 80  # Can play multiple styles
        elif 50 <= tempo_rank <= 250:
            flexibility = 65
        else:
            flexibility = 50  # Locked into one style
            
        # Elite teams get bonus regardless of pace
        team_row = self.rankings[self.rankings['Team'] == team_name].iloc[0]
        if team_row['AdjEM_Rank'] <= 25:
            flexibility = min(100, flexibility + 15)
            
        return flexibility
    
    def calculate_experience(self, team_name):
        """
        Veteran teams typically perform better under pressure
        For now, use conference and ranking as proxy
        """
        team_row = self.rankings[self.rankings['Team'] == team_name].iloc[0]
        conf = team_row['Conference']
        
        # Power conference teams typically have more experienced players
        power_conferences = ['SEC', 'B12', 'B10', 'ACC', 'BE']
        
        if conf in power_conferences:
            base_experience = 70
        else:
            base_experience = 50
            
        # Top programs recruit experienced transfers
        if team_row['AdjEM_Rank'] <= 50:
            base_experience += 10
            
        return min(100, base_experience)
    
    def calculate_altitude_travel(self, team_name):
        """
        Account for home court advantages and travel difficulties
        Teams at altitude, remote locations, or with great crowds get bonus
        """
        # Known tough home courts
        altitude_teams = ['Air Force', 'Colorado', 'Colorado St.', 'Denver', 
                         'New Mexico', 'Utah St.', 'Wyoming', 'Nevada']
        
        tough_venues = ['Duke', 'Kansas', 'Gonzaga', 'Michigan St.', 'Purdue',
                       'Arizona', 'Kentucky', 'North Carolina']
        
        if team_name in altitude_teams:
            return 85  # Significant home advantage
        elif team_name in tough_venues:
            return 75  # Great home court
        else:
            return 60  # Normal home advantage
    
    def calculate_injury_adjustment(self, team_name):
        """
        Placeholder for injury adjustments
        In reality, would track player availability
        """
        # For now, assume all teams healthy
        return 75
    
    def calculate_predictive_score(self, team_row):
        """Calculate comprehensive predictive score"""
        team_name = team_row['Team']
        
        # Calculate all components
        scores = {
            'adjusted_efficiency': self.calculate_adjusted_efficiency(team_row),
            'recent_performance': self.calculate_recent_performance(team_name),
            'consistency': self.calculate_consistency(team_name),
            'pace_flexibility': self.calculate_pace_flexibility(team_name),
            'experience': self.calculate_experience(team_name),
            'altitude_travel': self.calculate_altitude_travel(team_name),
            'injury_adjustment': self.calculate_injury_adjustment(team_name)
        }
        
        # Calculate weighted score
        total_score = sum(scores[factor] * self.weights[factor] 
                         for factor in scores)
        
        return total_score, scores
    
    def generate_rankings(self):
        """Generate predictive power rankings"""
        print("\nCalculating predictive scores...")
        
        results = []
        for idx, row in self.rankings.iterrows():
            total_score, component_scores = self.calculate_predictive_score(row)
            
            result = {
                'Team': row['Team'],
                'Conference': row['Conference'],
                'Predictive_Score': total_score,
                'KenPom_Rank': row['AdjEM_Rank'],
                'AdjEM': row['AdjEM'],
                'AdjOE': row['AdjOE'],
                'AdjDE': row['AdjDE']
            }
            
            # Add component scores
            for factor, score in component_scores.items():
                result[f'{factor}_score'] = score
                
            results.append(result)
        
        # Create DataFrame and rank
        self.results_df = pd.DataFrame(results)
        self.results_df = self.results_df.sort_values('Predictive_Score', ascending=False)
        self.results_df['Predictive_Rank'] = range(1, len(self.results_df) + 1)
        
        # Compare to KenPom
        self.results_df['Rank_Diff'] = self.results_df['KenPom_Rank'] - self.results_df['Predictive_Rank']
        
        return self.results_df
    
    def display_rankings(self, n=25):
        """Display top N teams"""
        print(f"\n{'='*120}")
        print("PREDICTIVE POWER RANKINGS - Who Would Win Tomorrow?")
        print(f"{'='*120}")
        print(f"{'Rank':<6}{'Team':<20}{'Conf':<8}{'Score':<8}{'AdjEM':<8}{'Offense':<10}{'Defense':<10}{'KP Rank':<10}{'Diff':<8}")
        print(f"{'-'*120}")
        
        top_teams = self.results_df.head(n)
        for idx, row in top_teams.iterrows():
            rank_diff = row['Rank_Diff']
            diff_symbol = '↑' if rank_diff > 0 else '↓' if rank_diff < 0 else '='
            
            # Get efficiency ranks
            off_rank = self.rankings[self.rankings['Team'] == row['Team']].iloc[0]['AdjOE.Rank']
            def_rank = self.rankings[self.rankings['Team'] == row['Team']].iloc[0]['AdjDE.Rank']
            
            print(f"{row['Predictive_Rank']:<6}{row['Team']:<20}{row['Conference']:<8}"
                  f"{row['Predictive_Score']:<8.1f}{row['AdjEM']:<8.2f}"
                  f"#{off_rank:<9.0f}#{def_rank:<9.0f}"
                  f"{row['KenPom_Rank']:<10.0f}{diff_symbol}{abs(rank_diff):<7.0f}")
    
    def show_prediction_factors(self, team_name):
        """Show what drives a team's predictive rating"""
        team_data = self.results_df[self.results_df['Team'] == team_name]
        
        if len(team_data) == 0:
            print(f"Team '{team_name}' not found")
            return
            
        row = team_data.iloc[0]
        
        print(f"\n{'='*60}")
        print(f"PREDICTIVE BREAKDOWN: {team_name}")
        print(f"{'='*60}")
        print(f"Predictive Rank: #{row['Predictive_Rank']} (Score: {row['Predictive_Score']:.1f})")
        print(f"KenPom Rank: #{row['KenPom_Rank']}")
        print(f"\nFactor Scores:")
        print(f"{'-'*60}")
        
        for factor in self.weights.keys():
            score = row[f'{factor}_score']
            weight = self.weights[factor]
            contribution = score * weight
            print(f"{factor.replace('_', ' ').title():<25}{score:<10.1f}{weight:<10.1%}{contribution:<10.1f}")
    
    def predict_matchup(self, team1, team2, neutral=True):
        """Predict a specific matchup"""
        t1_data = self.results_df[self.results_df['Team'] == team1]
        t2_data = self.results_df[self.results_df['Team'] == team2]
        
        if len(t1_data) == 0 or len(t2_data) == 0:
            print("One or both teams not found")
            return
            
        t1 = t1_data.iloc[0]
        t2 = t2_data.iloc[0]
        
        # Base prediction on score difference
        score_diff = t1['Predictive_Score'] - t2['Predictive_Score']
        
        # Convert to point spread (roughly 1 score point = 0.4 real points)
        predicted_spread = score_diff * 0.4
        
        # Home court adjustment
        if not neutral:
            home_bonus = 3.5  # Standard home court advantage
            predicted_spread += home_bonus
        
        print(f"\n{'='*60}")
        print(f"MATCHUP PREDICTION: {team1} vs {team2}")
        print(f"{'='*60}")
        print(f"Location: {'Neutral Court' if neutral else f'{team1} Home Court'}")
        print(f"\n{team1}: #{t1['Predictive_Rank']} (Score: {t1['Predictive_Score']:.1f})")
        print(f"{team2}: #{t2['Predictive_Rank']} (Score: {t2['Predictive_Score']:.1f})")
        print(f"\nPredicted Result: {team1} by {abs(predicted_spread):.1f}" if predicted_spread > 0 
              else f"\nPredicted Result: {team2} by {abs(predicted_spread):.1f}")
        
        # Win probability (simple logistic approach)
        win_prob = 1 / (1 + np.exp(-predicted_spread/10))
        print(f"\n{team1} Win Probability: {win_prob:.1%}")
        print(f"{team2} Win Probability: {1-win_prob:.1%}")

# Example usage
if __name__ == "__main__":
    # Create model
    model = PredictivePowerRankingModel()
    
    # Load data
    model.load_data()
    
    # Generate rankings
    rankings = model.generate_rankings()
    
    # Display top 25
    model.display_rankings(25)
    
    # Show some interesting breakdowns
    print("\n" + "="*60)
    print("DETAILED BREAKDOWNS")
    print("="*60)
    
    # Top team
    top_team = rankings.iloc[0]['Team']
    model.show_prediction_factors(top_team)
    
    # Interesting teams
    model.show_prediction_factors('Gonzaga')
    model.show_prediction_factors('Arkansas')
    
    # Predict some matchups
    print("\n" + "="*60)
    print("SAMPLE PREDICTIONS")
    print("="*60)
    
    model.predict_matchup('Duke', 'North Carolina', neutral=True)
    model.predict_matchup('Kansas', 'Houston', neutral=False)
    model.predict_matchup('Arkansas', 'Kentucky', neutral=True)
    
    # Save rankings
    model.results_df.to_csv('data/predictive_rankings_latest.csv', index=False)
    print("\n\nRankings saved to data/predictive_rankings_latest.csv")