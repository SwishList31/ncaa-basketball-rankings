"""
Diagnose the column issue with our data merge
"""

import pandas as pd

def diagnose_columns():
    """Check what columns we actually have"""
    
    print("DIAGNOSING COLUMN ISSUES")
    print("="*60)
    
    # Load the data files
    print("\n1. Loading rankings data...")
    rankings = pd.read_csv('data/kenpom_rankings_latest.csv')
    print(f"   Shape: {rankings.shape}")
    print(f"   Columns: {list(rankings.columns)}")
    
    print("\n2. Loading personnel data...")
    personnel = pd.read_csv('data/kenpom_height_experience_latest.csv')
    print(f"   Shape: {personnel.shape}")
    print(f"   Columns: {list(personnel.columns)}")
    
    print("\n3. Checking for common columns...")
    common_cols = set(rankings.columns) & set(personnel.columns)
    print(f"   Common columns: {common_cols}")
    
    print("\n4. Attempting merge...")
    try:
        merged = pd.merge(rankings, personnel, on='Team', how='inner', suffixes=('', '_pers'))
        print(f"   Merge successful! Shape: {merged.shape}")
        print(f"   Merged columns: {list(merged.columns)}")
        
        # Check specifically for Conference
        conf_cols = [col for col in merged.columns if 'onf' in col or 'ONF' in col]
        print(f"\n   Conference-related columns: {conf_cols}")
        
        # Show first few rows
        print("\n5. First 3 rows of merged data:")
        print(merged[['Team'] + conf_cols].head(3))
        
    except Exception as e:
        print(f"   Merge failed: {e}")
    
    print("\n6. Sample data from each file:")
    print("\n   Rankings sample:")
    print(rankings[['Team', 'Conference', 'AdjEM']].head(3))
    
    print("\n   Personnel sample:")
    print(personnel[['Team', 'Conference', 'Experience']].head(3))

if __name__ == "__main__":
    diagnose_columns()