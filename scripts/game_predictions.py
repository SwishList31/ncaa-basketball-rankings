"""
Game Predictions using Defense-Focused Model
Test specific matchups and see how defense impacts predictions
"""

import pandas as pd
import numpy as np
from datetime import datetime

class GamePredictor:
    def __init__(self):
        """Initialize with our defense-focused rankings"""
        self.rankings = None
        self.kenpom = None
        
    def load_rankings(self, data_dir='data'):
        """Load both our rankings and original KenPom data"""
        print("Loading rankings data...")
        self.rankings = pd.read_csv(f'{data_dir}/defense_focused_rankings_latest.csv')
        self.kenpom = pd.read_csv(f'{data_dir}/kenpom_rankings_latest.csv')
        print(f"Loaded {len(self.rankings)} teams")
        
    def get_team_data(self, team_name):
        """Get all relevant data for a team"""
        # Our rankings
        our_data = self.rankings[self.rankings['Team'] == team_name]
        if len(our_data) == 0:
            print(f"Team {team_name} not found!")
            return None
            
        # KenPom data
        kp_data = self.kenpom[self.kenpom['Team'] == team_name].iloc[0]
        our_data = our_data.iloc[0]
        
        return {
            'team': team_name,
            'our_rank': our_data['Defense_Rank'],
            'our_score': our_data['Defense_Focused_Score'],
            'kp_rank': kp_data['AdjEM_Rank'],
            'adj_o': kp_data['AdjOE'],
            'adj_d': kp_data['AdjDE'],
            'adj_em': kp_data['AdjEM'],
            'def_rank': our_data['AdjDE_Rank'],
            'off_rank': our_data['AdjOE_Rank']
        }
    
    def predict_game(self, team1_name, team2_name, location='neutral', verbose=True):
        """
        Predict a game outcome
        location: 'neutral', 'home' (team1 at home), 'away' (team2 at home)
        """
        # Get team data
        team1 = self.get_team_data(team1_name)
        team2 = self.get_team_data(team2_name)
        
        if not team1 or not team2:
            return None
            
        # Calculate base prediction from our scores
        score_diff = team1['our_score'] - team2['our_score']
        
        # Convert to predicted margin (calibrated from testing)
        # Our score differences are smaller, so multiply by factor
        predicted_margin = score_diff * 0.35
        
        # Home court advantage
        if location == 'home':
            predicted_margin += 3.5
        elif location == 'away':
            predicted_margin -= 3.5
            
        # Calculate predicted scores using tempo and efficiency
        # Estimate possessions (around 70 average)
        possessions = 70
        
        # Team 1 scores against Team 2's defense
        team1_expected_pts = (team1['adj_o'] / 100) * possessions * (100 / team2['adj_d'])
        # Team 2 scores against Team 1's defense  
        team2_expected_pts = (team2['adj_o'] / 100) * possessions * (100 / team1['adj_d'])
        
        # Adjust based on our model's prediction
        adjustment = predicted_margin / 2
        team1_expected_pts += adjustment
        team2_expected_pts -= adjustment
        
        # Win probability using logistic function
        win_prob = 1 / (1 + np.exp(-predicted_margin / 8))
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"GAME PREDICTION: {team1_name} vs {team2_name}")
            print(f"{'='*70}")
            print(f"Location: {location.title()}")
            print(f"\n{team1_name:20} | Our Rank: #{team1['our_rank']:<3} | KP: #{team1['kp_rank']:<3} | Def: #{team1['def_rank']:<3} | Off: #{team1['off_rank']:<3}")
            print(f"{team2_name:20} | Our Rank: #{team2['our_rank']:<3} | KP: #{team2['kp_rank']:<3} | Def: #{team2['def_rank']:<3} | Off: #{team2['off_rank']:<3}")
            print(f"\n{'-'*70}")
            print(f"PREDICTION:")
            print(f"{'-'*70}")
            
            if predicted_margin > 0:
                print(f"Winner: {team1_name} by {abs(predicted_margin):.1f}")
            else:
                print(f"Winner: {team2_name} by {abs(predicted_margin):.1f}")
                
            print(f"\nProjected Score: {team1_name} {team1_expected_pts:.0f}, {team2_name} {team2_expected_pts:.0f}")
            print(f"\nWin Probability:")
            print(f"  {team1_name}: {win_prob:.1%}")
            print(f"  {team2_name}: {(1-win_prob):.1%}")
            
            # Analysis
            print(f"\n{'-'*70}")
            print("KEY FACTORS:")
            print(f"{'-'*70}")
            
            # Defensive matchup
            if team1['def_rank'] < team2['off_rank']:
                print(f"• {team1_name}'s defense (#{team1['def_rank']}) should slow {team2_name}'s offense (#{team2['off_rank']})")
            if team2['def_rank'] < team1['off_rank']:
                print(f"• {team2_name}'s defense (#{team2['def_rank']}) should slow {team1_name}'s offense (#{team1['off_rank']})")
                
            # Style matchup
            if team1['def_rank'] < 30 and team2['def_rank'] < 30:
                print(f"• Defensive battle expected - both teams in top 30 defenses")
            elif team1['off_rank'] < 30 and team2['off_rank'] < 30:
                print(f"• High-scoring game possible - both teams in top 30 offenses")
                
        return {
            'team1': team1_name,
            'team2': team2_name,
            'predicted_margin': predicted_margin,
            'team1_score': team1_expected_pts,
            'team2_score': team2_expected_pts,
            'team1_win_prob': win_prob,
            'location': location
        }
    
    def compare_predictions(self, team1_name, team2_name):
        """Compare our prediction vs pure KenPom"""
        print(f"\n{'='*70}")
        print(f"MODEL COMPARISON: {team1_name} vs {team2_name}")
        print(f"{'='*70}")
        
        # Get team data
        team1 = self.get_team_data(team1_name)
        team2 = self.get_team_data(team2_name)
        
        # Our model prediction
        our_diff = team1['our_score'] - team2['our_score']
        our_margin = our_diff * 0.35
        
        # KenPom prediction (just use AdjEM difference)
        kp_margin = team1['adj_em'] - team2['adj_em']
        
        print(f"\nDEFENSE-FOCUSED MODEL:")
        print(f"  {team1_name} by {our_margin:.1f}" if our_margin > 0 
              else f"  {team2_name} by {abs(our_margin):.1f}")
        
        print(f"\nKENPOM MODEL:")
        print(f"  {team1_name} by {kp_margin:.1f}" if kp_margin > 0 
              else f"  {team2_name} by {abs(kp_margin):.1f}")
        
        print(f"\nDIFFERENCE: {abs(our_margin - kp_margin):.1f} points")
        
        if (our_margin > 0) != (kp_margin > 0):
            print("\n*** MODELS DISAGREE ON WINNER! ***")
            
    def test_interesting_matchups(self):
        """Test various interesting matchups"""
        print("\n" + "="*70)
        print("TESTING INTERESTING MATCHUPS")
        print("="*70)
        
        matchups = [
            # Elite defensive teams
            ("Houston", "Alabama", "neutral"),  # #1 defense vs #4 offense
            ("Michigan St.", "Purdue", "neutral"),  # #4 defense vs #7 offense
            
            # Offense vs Defense
            ("Duke", "Houston", "neutral"),  # #1 offense vs #1 defense
            ("Tennessee", "Auburn", "neutral"),  # #3 defense vs #3 offense
            
            # Teams that moved in our rankings
            ("UCLA", "Arizona", "home"),  # UCLA jumped up, Arizona fell
            ("Texas Tech", "Iowa St.", "neutral"),  # Tech fell, Iowa St. steady
            
            # Classic matchups
            ("Duke", "North Carolina", "away"),  # At UNC
            ("Kansas", "Kentucky", "neutral"),  # Classic blueblood battle
        ]
        
        results = []
        for team1, team2, location in matchups:
            result = self.predict_game(team1, team2, location, verbose=True)
            if result:
                results.append(result)
                
        return results

# Run predictions
if __name__ == "__main__":
    predictor = GamePredictor()
    predictor.load_rankings()
    
    # Test specific matchups
    print("\n" + "="*70)
    print("SHOWCASE PREDICTIONS")
    print("="*70)
    
    # Defense vs Offense showdown
    predictor.predict_game("Houston", "Alabama", "neutral")
    predictor.compare_predictions("Houston", "Alabama")
    
    # What our model values
    predictor.predict_game("Michigan St.", "Purdue", "neutral")
    predictor.compare_predictions("Michigan St.", "Purdue")
    
    # Test all interesting matchups
    results = predictor.test_interesting_matchups()
    
    # Summary of predictions
    print("\n" + "="*70)
    print("PREDICTION SUMMARY")
    print("="*70)
    print(f"{'Matchup':<30} {'Predicted Winner':<20} {'Margin':<10} {'Win %':<10}")
    print("-"*70)
    
    for r in results:
        winner = r['team1'] if r['predicted_margin'] > 0 else r['team2']
        margin = abs(r['predicted_margin'])
        win_pct = r['team1_win_prob'] if r['predicted_margin'] > 0 else (1 - r['team1_win_prob'])
        matchup = f"{r['team1']} vs {r['team2']}"
        print(f"{matchup:<30} {winner:<20} {margin:<10.1f} {win_pct:<10.1%}")