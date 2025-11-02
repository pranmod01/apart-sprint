"""
Batch Forecasting Script - Loads YOUR actual data
Processes capabilities from combined_benchmarks_cleaned.csv
"""

import json
import pandas as pd
from capability_forecaster import CapabilityForecaster
from datetime import datetime
from typing import List, Dict
import os


class BatchForecaster:
    """Generate forecasts for multiple capabilities at once."""
    
    def __init__(self, data_path: str, output_dir: str = "predictions"):
        """
        Args:
            data_path: Path to combined_benchmarks_cleaned.csv
            output_dir: Where to save predictions
        """
        self.data_path = data_path
        self.output_dir = output_dir
        self.forecaster = CapabilityForecaster(saturation_point=100.0)
        self.results = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'model': 'logistic_growth',
                'confidence_level': 0.95,
                'data_source': data_path
            },
            'capabilities': {}
        }
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def load_data(self) -> pd.DataFrame:
        """Load your combined benchmarks data."""
        print(f"\n{'='*60}")
        print(f"Loading data from: {self.data_path}")
        print(f"{'='*60}")
        
        df = pd.read_csv(self.data_path)
        
        print(f"\n✓ Loaded {len(df)} rows")
        print(f"✓ Columns: {df.columns.tolist()}")
        print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
        
        # Score range check
        if 'score' in df.columns:
            score_min = df['score'].min()
            score_max = df['score'].max()
            print(f"✓ Score range: {score_min:.4f} to {score_max:.4f}")
            
            if score_max <= 1.0:
                print(f"  ℹ️  Scores appear to be on 0-1 scale (will auto-convert to 0-100)")
            elif score_max <= 100:
                print(f"  ℹ️  Scores appear to be on 0-100 scale")
            else:
                print(f"  ⚠️  Warning: Max score > 100, may need custom handling")
        
        if 'capability' in df.columns:
            print(f"✓ Capabilities found: {df['capability'].nunique()}")
            print(f"  {sorted(df['capability'].unique())}")
        
        return df
    
    def prepare_capability_data(self, df: pd.DataFrame, 
                                min_points: int = 4) -> Dict[str, Dict]:
        """
        Convert dataframe to capability time series.
        
        Args:
            df: DataFrame with columns: date, score, capability
            min_points: Minimum data points required per capability
            
        Returns:
            Dictionary mapping capability names to {dates, scores}
        """
        print(f"\n{'='*60}")
        print("PREPARING CAPABILITY TIME SERIES")
        print(f"{'='*60}\n")
        
        capabilities_data = {}
        
        # Group by capability
        for capability in df['capability'].unique():
            cap_df = df[df['capability'] == capability].copy()
            
            # Sort by date
            cap_df = cap_df.sort_values('date')
            
            # If multiple scores per date, take the BEST (max) score
            # This represents the state-of-the-art on that date
            cap_df = cap_df.groupby('date', as_index=False).agg({
                'score': 'max',  # Best performance on that date
                'capability': 'first'
            })
            
            # Re-sort after aggregation
            cap_df = cap_df.sort_values('date')
            
            # Check minimum points
            if len(cap_df) < min_points:
                print(f"⚠️  Skipping {capability}: only {len(cap_df)} points (need {min_points})")
                continue
            
            # Extract dates and scores
            dates = cap_df['date'].tolist()
            scores = cap_df['score'].tolist()
            
            # Auto-detect scale and normalize to 0-100
            max_score = max(scores)
            min_score = min(scores)
            
            # Check if we have MIXED scales (some 0-1, some 0-100)
            has_small = any(s <= 1.0 for s in scores)
            has_large = any(s > 1.0 for s in scores)
            
            if has_small and has_large:
                # MIXED SCALES: Convert small values (<=1.0) to 0-100
                print(f"  ⚠️  MIXED SCALES detected! Converting values <=1.0 to percentage")
                scores = [s * 100 if s <= 1.0 else s for s in scores]
                max_score = max(scores)
                min_score = min(scores)
            elif max_score <= 1.0:
                # All scores are 0-1 scale, convert to 0-100
                scores = [s * 100 for s in scores]
                print(f"  ℹ️  Normalized from 0-1 scale: {min_score:.3f}-{max_score:.3f} → {min_score*100:.1f}-{max_score*100:.1f}")
                max_score = max(scores)
                min_score = min(scores)
            elif max_score <= 10.0 and min_score >= 1.0:
                # Looks like 1-10 scale (e.g., rating), convert to 0-100
                scores = [s * 10 for s in scores]
                print(f"  ℹ️  Detected 1-10 rating scale: {min_score:.2f}-{max_score:.2f} → {min_score*10:.1f}-{max_score*10:.1f}")
                max_score = max(scores)
                min_score = min(scores)
            elif max_score > 100:
                print(f"⚠️  Warning: max score = {max_score:.2f} (>100), may need custom normalization")
            
            # Show the data we'll use
            print(f"  → {len(dates)} time points: {dates[0]} to {dates[-1]}")
            print(f"  → Score range: {min(scores):.1f} to {max(scores):.1f}")
            print(f"  → Trend: {scores[0]:.1f} → {scores[-1]:.1f} ({scores[-1]-scores[0]:+.1f})")
            
            capabilities_data[capability] = {
                'dates': dates,
                'scores': scores
            }
            
            print(f"✓ {capability}: {len(dates)} points from {dates[0]} to {dates[-1]}")
        
        print(f"\n✓ Prepared {len(capabilities_data)} capabilities for forecasting")
        
        return capabilities_data
    
    def process_capability(self, 
                          capability_name: str,
                          dates: List[str],
                          scores: List[float],
                          thresholds: List[float] = [85, 90, 95]) -> Dict:
        """
        Process a single capability: fit model and generate predictions.
        """
        print(f"\n{'='*60}")
        print(f"Processing: {capability_name}")
        print(f"{'='*60}")
        
        # Fit the model
        fit_result = self.forecaster.fit_capability(dates, scores, capability_name)
        
        if not fit_result['success']:
            print(f"❌ Failed to fit: {fit_result.get('error', 'Unknown error')}")
            return {
                'success': False,
                'error': fit_result.get('error'),
                'capability': capability_name
            }
        
        print(f"✓ Fitted successfully (R² = {fit_result['r_squared']:.4f})")
        
        # Generate predictions for each threshold
        predictions = []
        for threshold in thresholds:
            pred = self.forecaster.predict_threshold_date(capability_name, threshold)
            
            if pred['success']:
                if pred.get('already_achieved'):
                    print(f"  {threshold}%: Already achieved on {pred['date_achieved']}")
                else:
                    ci_range = (pd.to_datetime(pred['confidence_interval']['upper']) - 
                               pd.to_datetime(pred['confidence_interval']['lower'])).days // 2
                    print(f"  {threshold}%: {pred['predicted_date']} (±{ci_range} days)")
                
                predictions.append(pred)
        
        # Generate forecast curve for visualization
        forecast_curve = self.forecaster.generate_forecast_curve(
            capability_name, 
            days_ahead=730
        )
        
        # Generate forecast nodes for 3D terrain
        forecast_nodes = self.forecaster.export_forecast_nodes(
            capability_name,
            thresholds
        )
        
        return {
            'success': True,
            'capability': capability_name,
            'fit_quality': {
                'r_squared': fit_result['r_squared'],
                'n_observations': fit_result['n_observations'],
                'date_range': fit_result['date_range']
            },
            'model_parameters': {
                'L': fit_result['L'],
                'k': fit_result['k'],
                't0': fit_result['t0']
            },
            'threshold_predictions': predictions,
            'forecast_curve': forecast_curve,
            'forecast_nodes': forecast_nodes
        }
    
    def process_all(self, min_points: int = 4, thresholds: List[float] = [85, 90, 95]) -> None:
        """
        Main processing pipeline: load data, prepare, forecast all capabilities.
        
        Args:
            min_points: Minimum data points required per capability
            thresholds: Threshold percentages to predict
        """
        # Load data
        df = self.load_data()
        
        # Prepare capability time series
        capabilities_data = self.prepare_capability_data(df, min_points)
        
        if len(capabilities_data) == 0:
            print("\n❌ No capabilities with sufficient data points!")
            return
        
        # Process each capability
        print(f"\n{'='*60}")
        print(f"FORECASTING {len(capabilities_data)} CAPABILITIES")
        print(f"{'='*60}")
        
        for capability_name, data in capabilities_data.items():
            result = self.process_capability(
                capability_name,
                data['dates'],
                data['scores'],
                thresholds=thresholds
            )
            
            self.results['capabilities'][capability_name] = result
        
        # Save results
        self.save_results()
        
        # Print summary
        self.print_summary()
    
    def save_results(self) -> None:
        """Save all results to JSON files."""
        
        # Full results
        full_path = os.path.join(self.output_dir, 'forecast_results.json')
        with open(full_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Saved full results to: {full_path}")
        
        # Forecast nodes only (for 3D terrain integration)
        all_nodes = []
        for cap_name, cap_data in self.results['capabilities'].items():
            if cap_data['success']:
                all_nodes.extend(cap_data['forecast_nodes'])
        
        nodes_path = os.path.join(self.output_dir, 'forecast_nodes.json')
        with open(nodes_path, 'w') as f:
            json.dump({
                'metadata': self.results['metadata'],
                'nodes': all_nodes
            }, f, indent=2)
        print(f"✓ Saved forecast nodes to: {nodes_path}")
        
        # Summary CSV
        summary_rows = []
        for cap_name, cap_data in self.results['capabilities'].items():
            if cap_data['success']:
                for pred in cap_data['threshold_predictions']:
                    if pred['success'] and not pred.get('already_achieved'):
                        summary_rows.append({
                            'capability': cap_name,
                            'threshold': pred['threshold'],
                            'predicted_date': pred['predicted_date'],
                            'ci_lower': pred['confidence_interval']['lower'],
                            'ci_upper': pred['confidence_interval']['upper'],
                            'days_until': pred['days_until_threshold'],
                            'current_performance': pred['current_predicted_performance']
                        })
        
        if summary_rows:
            df = pd.DataFrame(summary_rows)
            csv_path = os.path.join(self.output_dir, 'forecast_summary.csv')
            df.to_csv(csv_path, index=False)
            print(f"✓ Saved summary CSV to: {csv_path}")
    
    def print_summary(self) -> None:
        """Print a summary of all forecasts."""
        print(f"\n{'='*60}")
        print("FORECAST SUMMARY")
        print(f"{'='*60}")
        
        successful = sum(1 for c in self.results['capabilities'].values() if c['success'])
        failed = len(self.results['capabilities']) - successful
        
        print(f"\nCapabilities processed: {len(self.results['capabilities'])}")
        print(f"  ✓ Successful: {successful}")
        print(f"  ✗ Failed: {failed}")
        
        if successful > 0:
            print(f"\nKey Predictions (90% threshold):")
            print(f"{'Capability':<30} {'Date':<15} {'Days Until':<12} {'Current %'}")
            print("-" * 70)
            
            for cap_name, cap_data in self.results['capabilities'].items():
                if not cap_data['success']:
                    continue
                
                # Find 90% prediction
                pred_90 = next(
                    (p for p in cap_data['threshold_predictions'] 
                     if p.get('threshold') == 90 and p['success']),
                    None
                )
                
                if pred_90 and not pred_90.get('already_achieved'):
                    days = pred_90.get('days_until_threshold', 'N/A')
                    current = pred_90.get('current_predicted_performance', 0)
                    print(f"{cap_name:<30} {pred_90['predicted_date']:<15} "
                          f"{str(days):>11} {current:>10.1f}%")


if __name__ == "__main__":
    # Path to your combined benchmarks file
    DATA_PATH = "data/intermediate/combined_benchmarks_cleaned.csv"
    
    print("\n" + "="*60)
    print("AI CAPABILITY FORECASTING")
    print("="*60)
    
    # Create forecaster
    batch = BatchForecaster(
        data_path=DATA_PATH,
        output_dir="predictions"
    )
    
    # Process all capabilities
    # min_points=4 means we need at least 4 time points to forecast
    # thresholds=[85, 90, 95] means predict when each hits these levels
    batch.process_all(
        min_points=4,
        thresholds=[85, 90, 95]
    )
    
    print("✅ COMPLETE! Files ready in ./predictions/")