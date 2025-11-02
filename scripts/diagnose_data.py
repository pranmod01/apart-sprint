"""
Detailed Data Diagnostics
Finds exactly what's wrong with each capability
"""

import pandas as pd
import numpy as np

def diagnose_capability(df, capability_name):
    """Diagnose a single capability's data."""
    
    cap_df = df[df['capability'] == capability_name].copy()
    cap_df = cap_df.sort_values('date')
    
    print(f"\n{'='*70}")
    print(f"CAPABILITY: {capability_name}")
    print(f"{'='*70}")
    
    print(f"\nData points: {len(cap_df)}")
    print(f"Date range: {cap_df['date'].min()} to {cap_df['date'].max()}")
    
    # Score analysis
    scores = cap_df['score'].values
    print(f"\nScore statistics:")
    print(f"  Min:    {scores.min():.6f}")
    print(f"  Max:    {scores.max():.6f}")
    print(f"  Mean:   {scores.mean():.6f}")
    print(f"  Median: {np.median(scores):.6f}")
    
    # Detect scale
    if scores.max() <= 1.0:
        print(f"  → Scale: 0-1 (will convert to 0-100)")
        print(f"  → After conversion: {scores.min()*100:.2f} to {scores.max()*100:.2f}")
    elif scores.max() <= 100:
        print(f"  → Scale: 0-100")
    else:
        print(f"  → Scale: UNKNOWN (max > 100)")
    
    # Check trend
    if len(scores) >= 2:
        trend = "increasing" if scores[-1] > scores[0] else "decreasing" if scores[-1] < scores[0] else "flat"
        change = scores[-1] - scores[0]
        print(f"\nTrend: {trend} (change: {change:+.6f})")
    
    # Show all data points
    print(f"\nAll data points:")
    print(f"{'Date':<15} {'Score':<12} {'Model':<30}")
    print("-" * 70)
    for _, row in cap_df.iterrows():
        model_name = row.get('model', 'N/A')
        if pd.notna(model_name):
            model_name = str(model_name)[:30]
        else:
            model_name = 'N/A'
        print(f"{row['date']:<15} {row['score']:<12.6f} {model_name:<30}")
    
    # Check for issues
    issues = []
    if len(scores) < 4:
        issues.append(f"Only {len(scores)} points (need ≥4)")
    if scores.max() == scores.min():
        issues.append("All scores identical (flat line)")
    if scores.max() <= 0.01:
        issues.append("Scores very low (<1%)")
    if any(pd.isna(scores)):
        issues.append("Contains null values")
    
    if issues:
        print(f"\n⚠️  ISSUES:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"\n✓ No obvious issues")
    
    return cap_df


def full_diagnosis(filepath="data/intermediate/combined_benchmarks_cleaned.csv"):
    """Run full diagnosis on all capabilities."""
    
    print("\n" + "="*70)
    print("FULL DATA DIAGNOSIS")
    print("="*70)
    
    df = pd.read_csv(filepath)
    
    print(f"\nTotal rows: {len(df):,}")
    print(f"Total capabilities: {df['capability'].nunique()}")
    
    # Get capability counts
    cap_counts = df.groupby('capability').size().sort_values(ascending=False)
    
    print("\n" + "="*70)
    print("QUICK OVERVIEW")
    print("="*70)
    
    for cap in cap_counts.index[:10]:  # Top 10 by data points
        cap_df = df[df['capability'] == cap]
        scores = cap_df['score'].values
        
        scale = "0-1" if scores.max() <= 1.0 else "0-100" if scores.max() <= 100 else ">100"
        trend = "↑" if scores[-1] > scores[0] else "↓" if scores[-1] < scores[0] else "→"
        
        print(f"{cap:<35} {len(cap_df):>3} pts | "
              f"Scale: {scale:<5} | Range: {scores.min():.3f}-{scores.max():.3f} {trend}")
    
    # Find problematic capabilities
    print("\n" + "="*70)
    print("POTENTIAL ISSUES")
    print("="*70)
    
    problems = []
    
    for cap in df['capability'].unique():
        cap_df = df[df['capability'] == cap]
        scores = cap_df['score'].values
        
        # Check for various issues
        if len(scores) < 4:
            problems.append((cap, f"Only {len(scores)} points"))
        elif scores.max() <= 0.01:
            problems.append((cap, f"Very low scores (max: {scores.max():.6f})"))
        elif scores.max() == scores.min():
            problems.append((cap, "Flat line (no variation)"))
        elif scores.max() > 1.0 and scores.max() < 10:
            problems.append((cap, f"Unusual scale? (max: {scores.max():.2f})"))
    
    if problems:
        for cap, issue in problems[:15]:  # Show first 15
            print(f"  {cap:<35} → {issue}")
    else:
        print("  No major issues found!")
    
    # Interactive drill-down
    print("\n" + "="*70)
    print("DETAILED CAPABILITY ANALYSIS")
    print("="*70)
    
    # Focus on the ones you mentioned
    focus_caps = [
        'writing_quality',
        'code_generation', 
        'scientific_reasoning',
        'commonsense_reasoning',
        'creative_writing'
    ]
    
    for cap in focus_caps:
        if cap in df['capability'].values:
            diagnose_capability(df, cap)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    # Count by scale
    scale_counts = {'0-1': 0, '0-100': 0, 'other': 0}
    for cap in df['capability'].unique():
        scores = df[df['capability'] == cap]['score'].values
        if scores.max() <= 1.0:
            scale_counts['0-1'] += 1
        elif scores.max() <= 100:
            scale_counts['0-100'] += 1
        else:
            scale_counts['other'] += 1
    
    print(f"\nCapabilities by scale:")
    print(f"  0-1 scale:   {scale_counts['0-1']}")
    print(f"  0-100 scale: {scale_counts['0-100']}")
    print(f"  Other:       {scale_counts['other']}")
    
    if scale_counts['0-1'] > 0 and scale_counts['0-100'] > 0:
        print(f"\n⚠️  MIXED SCALES DETECTED!")
        print(f"  Some capabilities use 0-1, others use 0-100")
        print(f"  Auto-normalization should handle this.")


if __name__ == "__main__":
    full_diagnosis()