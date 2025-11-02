"""
AI Capability Forecasting Model
Predicts when capabilities will reach target thresholds (e.g., 90%) using logistic growth
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import t
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

warnings.filterwarnings('ignore')


class CapabilityForecaster:
    """
    Forecasts AI capability progression using logistic growth curves.
    Predicts "when will capability X reach 90% performance?"
    """
    
    def __init__(self, saturation_point: float = 100.0):
        """
        Args:
            saturation_point: Maximum theoretical performance (default 100%)
        """
        self.saturation_point = saturation_point
        self.fitted_params = {}
        self.confidence_intervals = {}
        
    @staticmethod
    def logistic_growth(t: np.ndarray, L: float, k: float, t0: float) -> np.ndarray:
        """
        Logistic growth function: L / (1 + exp(-k * (t - t0)))
        
        Args:
            t: Time points
            L: Saturation level (maximum value)
            k: Growth rate
            t0: Midpoint (inflection point)
        
        Returns:
            Predicted values
        """
        return L / (1 + np.exp(-k * (t - t0)))
    
    def fit_capability(self, 
                       dates: List[str], 
                       scores: List[float],
                       capability_name: str) -> Dict:
        """
        Fit logistic growth curve to historical capability data.
        
        Args:
            dates: List of date strings (ISO format: "YYYY-MM-DD")
            scores: List of performance scores (0-100)
            capability_name: Name of the capability being forecasted
            
        Returns:
            Dictionary with fitted parameters and metadata
        """
        # Convert dates to numeric (days since first observation)
        date_objects = pd.to_datetime(dates)
        t_numeric = (date_objects - date_objects.min()).days.values
        scores_array = np.array(scores)
        
        # Store original date range for reference
        min_date = date_objects.min()
        max_date = date_objects.max()
        
        try:
            # Initial parameter guesses
            L_init = self.saturation_point
            k_init = 0.01  # Growth rate
            t0_init = t_numeric.mean()  # Midpoint
            
            # Fit the curve
            popt, pcov = curve_fit(
                lambda t, k, t0: self.logistic_growth(t, L_init, k, t0),
                t_numeric,
                scores_array,
                p0=[k_init, t0_init],
                maxfev=10000,
                bounds=([0.0001, -1000], [1, t_numeric.max() * 5])
            )
            
            k_fitted, t0_fitted = popt
            L_fitted = L_init
            
            # Calculate confidence intervals (95%)
            perr = np.sqrt(np.diag(pcov))
            
            # Store results
            self.fitted_params[capability_name] = {
                'L': L_fitted,
                'k': k_fitted,
                't0': t0_fitted,
                'min_date': min_date,
                'reference_date': min_date,  # All t values are relative to this
                't_numeric': t_numeric,
                'scores': scores_array
            }
            
            self.confidence_intervals[capability_name] = {
                'k_std': perr[0],
                't0_std': perr[1]
            }
            
            # Calculate R² for goodness of fit
            predictions = self.logistic_growth(t_numeric, L_fitted, k_fitted, t0_fitted)
            ss_res = np.sum((scores_array - predictions) ** 2)
            ss_tot = np.sum((scores_array - scores_array.mean()) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            return {
                'success': True,
                'L': float(L_fitted),
                'k': float(k_fitted),
                't0': float(t0_fitted),
                'r_squared': float(r_squared),
                'n_observations': len(scores),
                'date_range': f"{min_date.date()} to {max_date.date()}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'capability': capability_name
            }
    
    def predict_threshold_date(self, 
                               capability_name: str, 
                               threshold: float = 90.0,
                               confidence_level: float = 0.95) -> Dict:
        """
        Predict when a capability will reach a specific threshold.
        
        Args:
            capability_name: Name of the capability
            threshold: Target performance level (e.g., 90 for 90%)
            confidence_level: Confidence level for interval (default 0.95)
            
        Returns:
            Dictionary with prediction date and confidence interval
        """
        if capability_name not in self.fitted_params:
            return {
                'success': False,
                'error': f"Capability '{capability_name}' not fitted yet"
            }
        
        params = self.fitted_params[capability_name]
        ci = self.confidence_intervals[capability_name]
        
        L = params['L']
        k = params['k']
        t0 = params['t0']
        reference_date = params['reference_date']
        
        # Check if threshold is achievable
        if threshold > L:
            return {
                'success': False,
                'error': f"Threshold {threshold}% exceeds saturation level {L}%",
                'capability': capability_name
            }
        
        # Check if we've already passed the threshold
        current_scores = params['scores']
        if len(current_scores) > 0 and current_scores.max() >= threshold:
            # Find when we first crossed threshold
            t_numeric = params['t_numeric']
            crossing_idx = np.where(current_scores >= threshold)[0][0]
            crossing_date = reference_date + timedelta(days=int(t_numeric[crossing_idx]))
            
            return {
                'success': True,
                'already_achieved': True,
                'date_achieved': crossing_date.strftime('%Y-%m-%d'),
                'capability': capability_name,
                'threshold': threshold,
                'message': f"Already achieved on {crossing_date.date()}"
            }
        
        # Solve for t when y = threshold
        # threshold = L / (1 + exp(-k * (t - t0)))
        # 1 + exp(-k * (t - t0)) = L / threshold
        # exp(-k * (t - t0)) = L / threshold - 1
        # -k * (t - t0) = ln(L / threshold - 1)
        # t = t0 - ln(L / threshold - 1) / k
        
        try:
            t_predicted = t0 - np.log(L / threshold - 1) / k
            predicted_date = reference_date + timedelta(days=float(t_predicted))
            
            # Calculate confidence interval using parameter uncertainties
            # Use Monte Carlo sampling for uncertainty propagation
            n_samples = 10000
            k_samples = np.random.normal(k, ci['k_std'], n_samples)
            t0_samples = np.random.normal(t0, ci['t0_std'], n_samples)
            
            # Filter out invalid samples (k must be positive)
            valid_mask = k_samples > 0
            k_samples = k_samples[valid_mask]
            t0_samples = t0_samples[valid_mask]
            
            # Calculate t for each sample
            t_samples = t0_samples - np.log(L / threshold - 1) / k_samples
            
            # Calculate percentiles for confidence interval
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            
            t_lower = np.percentile(t_samples, lower_percentile)
            t_upper = np.percentile(t_samples, upper_percentile)
            
            date_lower = reference_date + timedelta(days=float(t_lower))
            date_upper = reference_date + timedelta(days=float(t_upper))
            
            # Calculate current predicted performance
            t_current = (datetime.now() - reference_date).days
            current_predicted = float(self.logistic_growth(
                np.array([t_current]), L, k, t0
            )[0])
            
            return {
                'success': True,
                'already_achieved': False,
                'capability': capability_name,
                'threshold': threshold,
                'predicted_date': predicted_date.strftime('%Y-%m-%d'),
                'confidence_interval': {
                    'lower': date_lower.strftime('%Y-%m-%d'),
                    'upper': date_upper.strftime('%Y-%m-%d'),
                    'level': confidence_level
                },
                'days_until_threshold': int(t_predicted - t_current),
                'current_predicted_performance': round(current_predicted, 2),
                'growth_rate_k': round(k, 4),
                'saturation_level': L
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Prediction failed: {str(e)}",
                'capability': capability_name
            }
    
    def generate_forecast_curve(self, 
                                capability_name: str,
                                days_ahead: int = 730) -> Dict:
        """
        Generate predicted values for visualization.
        
        Args:
            capability_name: Name of the capability
            days_ahead: Number of days to forecast into the future
            
        Returns:
            Dictionary with dates and predicted values
        """
        if capability_name not in self.fitted_params:
            return {'success': False, 'error': 'Capability not fitted'}
        
        params = self.fitted_params[capability_name]
        L = params['L']
        k = params['k']
        t0 = params['t0']
        reference_date = params['reference_date']
        
        # Generate time points (historical + future)
        t_historic = params['t_numeric']
        t_max = t_historic.max()
        t_future = np.arange(t_max, t_max + days_ahead, 7)  # Weekly intervals
        t_all = np.concatenate([t_historic, t_future])
        
        # Generate predictions
        predictions = self.logistic_growth(t_all, L, k, t0)
        
        # Convert to dates
        dates = [reference_date + timedelta(days=int(t)) for t in t_all]
        
        return {
            'success': True,
            'capability': capability_name,
            'dates': [d.strftime('%Y-%m-%d') for d in dates],
            'predictions': predictions.tolist(),
            'historical_cutoff_index': len(t_historic)
        }
    
    def export_forecast_nodes(self, 
                              capability_name: str,
                              thresholds: List[float] = [80, 85, 90, 95]) -> List[Dict]:
        """
        Export forecast nodes for 3D terrain visualization.
        
        Args:
            capability_name: Name of the capability
            thresholds: List of threshold percentages to forecast
            
        Returns:
            List of forecast node dictionaries
        """
        nodes = []
        
        for threshold in thresholds:
            result = self.predict_threshold_date(capability_name, threshold)
            
            if result['success'] and not result.get('already_achieved', False):
                nodes.append({
                    'capability': capability_name,
                    'threshold': threshold,
                    'predicted_date': result['predicted_date'],
                    'confidence_interval': result['confidence_interval'],
                    'days_until': result['days_until_threshold'],
                    'type': 'forecast_node',
                    'style': 'translucent',
                    'color': 'blue' if threshold < 90 else 'purple'
                })
        
        return nodes


# Example usage and testing
if __name__ == "__main__":
    # Example: Code generation capability
    forecaster = CapabilityForecaster(saturation_point=100.0)
    
    # Historical data (example)
    dates = [
        "2022-01-01", "2022-06-01", "2023-01-01", 
        "2023-06-01", "2024-01-01", "2024-06-01"
    ]
    scores = [45, 52, 61, 68, 75, 82]
    
    # Fit the model
    print("Fitting logistic growth curve...")
    fit_result = forecaster.fit_capability(dates, scores, "code_generation")
    print(json.dumps(fit_result, indent=2))
    
    # Predict when it will reach 90%
    print("\n" + "="*50)
    print("Predicting when capability reaches 90%...")
    prediction = forecaster.predict_threshold_date("code_generation", threshold=90.0)
    print(json.dumps(prediction, indent=2))
    
    # Generate forecast nodes for visualization
    print("\n" + "="*50)
    print("Generating forecast nodes for terrain...")
    nodes = forecaster.export_forecast_nodes("code_generation", [85, 90, 95])
    print(json.dumps(nodes, indent=2))
    
    # Generate full forecast curve
    print("\n" + "="*50)
    print("Generating forecast curve (2 years ahead)...")
    curve = forecaster.generate_forecast_curve("code_generation", days_ahead=730)
    if curve['success']:
        print(f"Generated {len(curve['dates'])} points")
        print(f"Last prediction: {curve['predictions'][-1]:.2f}% on {curve['dates'][-1]}")