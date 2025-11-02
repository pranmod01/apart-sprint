"""
Batch Forecasting Script
Processes multiple capabilities and generates predictions for integration
"""

import json
import pandas as pd
from capability_forecaster import CapabilityForecaster
from datetime import datetime
from typing import List, Dict
import os


class BatchForecaster:
    """Generate forecasts for multiple capabilities at once."""
    
    def __init__(self, output_dir: str = "predictions"):
        self.output_dir = output_dir
        self.forecaster = CapabilityForecaster(saturation_point=100.0)
        self.results = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'model': 'logistic_growth',
                'confidence_level': 0.95
            },
            'capabilities': {}
        }
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def process_capability(self, 
                          capability_name: str,
                          dates: List[str],
                          scores: List[float],
                          thresholds: List[float] = [85, 90, 95]) -> Dict:
        """
        Process a single capability: fit model and generate predictions.
        
        Args:
            capability_name: Name of the capability
            dates: List of observation dates
            scores: List of performance scores
            thresholds: Target thresholds to predict
            
        Returns:
            Dictionary with all predictions and metadata
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
                    print(f"  {threshold}%: {pred['predicted_date']} "
                          f"(±{((pd.to_datetime(pred['confidence_interval']['upper']) - pd.to_datetime(pred['confidence_interval']['lower'])).days // 2)} days)")
                
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
    
    def process_batch(self, capabilities_data: Dict[str, Dict]) -> None:
        """
        Process multiple capabilities from a data dictionary.
        
        Args:
            capabilities_data: Dictionary mapping capability names to their data
                Format: {
                    'capability_name': {
                        'dates': ['2022-01-01', ...],
                        'scores': [45.2, ...]
                    }
                }
        """
        print(f"\n{'='*60}")
        print(f"BATCH FORECASTING - Processing {len(capabilities_data)} capabilities")
        print(f"{'='*60}")
        
        for capability_name, data in capabilities_data.items():
            result = self.process_capability(
                capability_name,
                data['dates'],
                data['scores'],
                thresholds=[85, 90, 95]
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


# Example data structure for your hackathon
EXAMPLE_CAPABILITIES = {
    'code_generation': {
        'dates': ["2022-01-01", "2022-06-01", "2023-01-01", "2023-06-01", "2024-01-01", "2024-06-01"],
        'scores': [45, 52, 61, 68, 75, 82]
    },
    'mathematical_reasoning': {
        'dates': ["2022-01-01", "2022-06-01", "2023-01-01", "2023-06-01", "2024-01-01", "2024-06-01"],
        'scores': [35, 41, 48, 56, 64, 71]
    },
    'natural_language_understanding': {
        'dates': ["2022-01-01", "2022-06-01", "2023-01-01", "2023-06-01", "2024-01-01", "2024-06-01"],
        'scores': [65, 70, 74, 78, 82, 86]
    },
    'visual_reasoning': {
        'dates': ["2022-01-01", "2022-06-01", "2023-01-01", "2023-06-01", "2024-01-01", "2024-06-01"],
        'scores': [30, 35, 42, 48, 56, 63]
    }
}


if __name__ == "__main__":
    # Run batch forecasting
    batch = BatchForecaster(output_dir="predictions")
    batch.process_batch(EXAMPLE_CAPABILITIES)
    
    print("\n" + "="*60)
    print("Ready for integration! Files in ./predictions/")
    print("="*60)