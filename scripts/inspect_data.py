"""
Data Inspection Script
Checks your combined_benchmarks_cleaned.csv before forecasting
"""

import pandas as pd

def inspect_data(filepath="data/intermediate/combined_benchmarks_cleaned.csv"):
    """Inspect the data file and check for issues."""
    
    print("\n" + "="*70)
    print("DATA INSPECTION")
    print("="*70 + "\n")
    
    # Load data
    print(f"Loading: {filepath}")
    df = pd.read_csv(filepath)
    
    print(f"✓ Loaded {len(df):,} rows\n")
    
    # Check required columns
    print("=" * 70)
    print("COLUMNS CHECK")
    print("=" * 70)
    
    required = ['date', 'score', 'capability']
    for col in required:
        if col in df.columns:
            print(f"✓ {col}: Found")
        else:
            print(f"✗ {col}: MISSING (required!)")
    
    print(f"\nAll columns: {df.columns.tolist()}\n")
    
    # Score range check
    print("=" * 70)
    print("SCORE ANALYSIS")
    print("=" * 70)
    
    if 'score' in df.columns:
        score_min = df['score'].min()
        score_max = df['score'].max()
        score_mean = df['score'].mean()
        
        print(f"Score range: {score_min:.6f} to {score_max:.6f}")
        print(f"Score mean:  {score_mean:.6f}")
        
        if score_max <= 1.0:
            print("\n✓ Scores are on 0-1 scale")
            print("  → Will auto-convert to 0-100 (multiply by 100)")
            print(f"  → After conversion: {score_min*100:.2f} to {score_max*100:.2f}")
        elif score_max <= 100:
            print("\n✓ Scores are on 0-100 scale")
        else:
            print(f"\n⚠️  WARNING: Max score is {score_max:.2f} (>100)")
            print("  → May need custom normalization")
        
        # Check for null scores
        null_count = df['score'].isnull().sum()
        if null_count > 0:
            print(f"\n⚠️  {null_count} null scores found")
    
    # Date analysis
    print("\n" + "=" * 70)
    print("DATE ANALYSIS")
    print("=" * 70)
    
    if 'date' in df.columns:
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        
        # Try to parse dates
        try:
            df['date_parsed'] = pd.to_datetime(df['date'])
            print("✓ Dates are in valid format")
        except:
            print("✗ ERROR: Dates cannot be parsed")
            print("  Dates must be in format: YYYY-MM-DD")
    
    # Capability analysis
    print("\n" + "=" * 70)
    print("CAPABILITY ANALYSIS")
    print("=" * 70)
    
    if 'capability' in df.columns:
        cap_counts = df.groupby('capability').size().sort_values(ascending=False)
        
        print(f"Total capabilities: {len(cap_counts)}")
        print(f"\nData points per capability:")
        print("-" * 70)
        
        for cap, count in cap_counts.items():
            status = "✓" if count >= 4 else "⚠️ "
            print(f"{status} {cap:<40} {count:>3} points")
        
        # Summary
        enough_data = (cap_counts >= 4).sum()
        print(f"\n{'='*70}")
        print(f"Capabilities with ≥4 points: {enough_data}/{len(cap_counts)}")
        print(f"Capabilities with <4 points: {len(cap_counts) - enough_data}/{len(cap_counts)}")
        
        if enough_data == 0:
            print("\n❌ ERROR: No capabilities have enough data points!")
            print("   Need at least 4 time points per capability to forecast")
        else:
            print(f"\n✓ {enough_data} capabilities ready for forecasting")
    
    issues = []
    
    # Check for issues
    if 'score' not in df.columns:
        issues.append("Missing 'score' column")
    if 'date' not in df.columns:
        issues.append("Missing 'date' column")
    if 'capability' not in df.columns:
        issues.append("Missing 'capability' column")
    
    if 'capability' in df.columns:
        cap_counts = df.groupby('capability').size()
        enough_data = (cap_counts >= 4).sum()
        if enough_data == 0:
            issues.append("No capabilities with ≥4 data points")
    
    if len(issues) == 0:
        print("\n✅ Data looks good! Ready to run batch_forecaster.py")
    else:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nFix these issues before running the forecaster.")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    inspect_data()