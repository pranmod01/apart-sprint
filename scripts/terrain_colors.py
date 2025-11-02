"""
Unified Color Scheme for AI Capability Terrain
All terrain nodes (baseline, forecasts, sinkholes) use these colors
"""

# Baseline Capability Colors (by capability name)
# RGB values in 0-1 range for rendering engines
CAPABILITY_COLORS = {
    # Language & Text (Blue spectrum)
    'code_generation': [0.2, 0.4, 0.8],
    'natural_language_understanding': [0.3, 0.5, 0.9],
    'creative_writing': [0.25, 0.45, 0.85],
    'writing_quality': [0.28, 0.48, 0.88],
    'language_modeling': [0.22, 0.42, 0.82],
    'reading_comprehension': [0.26, 0.46, 0.86],
    'natural_language_inference': [0.24, 0.44, 0.84],
    'language_understanding': [0.27, 0.47, 0.87],
    
    # Reasoning & Logic (Purple spectrum)
    'mathematical_reasoning': [0.6, 0.2, 0.7],
    'competition_math': [0.65, 0.25, 0.75],
    'advanced_mathematics': [0.7, 0.3, 0.8],
    'commonsense_reasoning': [0.55, 0.15, 0.65],
    'complex_reasoning': [0.58, 0.18, 0.68],
    'advanced_reasoning': [0.68, 0.28, 0.78],
    'abstract_reasoning': [0.62, 0.22, 0.72],
    'boolean_reasoning': [0.56, 0.16, 0.66],
    'physical_intuition': [0.54, 0.14, 0.64],
    'spatial_reasoning': [0.64, 0.24, 0.74],
    
    # Knowledge & Facts (Teal/Cyan spectrum)
    'general_knowledge': [0.2, 0.7, 0.5],
    'factual_knowledge': [0.25, 0.75, 0.55],
    'scientific_reasoning': [0.22, 0.72, 0.52],
    
    # Games & Interaction (Orange spectrum)
    'game_playing': [0.9, 0.5, 0.2],
    'game_strategy': [0.85, 0.45, 0.15],
    
    # Technical & Systems (Red spectrum)
    'cybersecurity': [0.8, 0.2, 0.2],
    'os_navigation': [0.75, 0.25, 0.25],
    'os_interaction': [0.78, 0.23, 0.23],
    'terminal_usage': [0.76, 0.24, 0.24],
    'agent_reasoning': [0.82, 0.22, 0.22],
    'cad_design': [0.77, 0.26, 0.26],
    
    # Planning & Strategy (Green spectrum)
    'long_horizon_planning': [0.4, 0.8, 0.3],
    
    # Miscellaneous (Gray spectrum)
    'basic_tasks': [0.5, 0.5, 0.5],
    'unusual_tasks': [0.6, 0.6, 0.6],
}

# Forecast Node Colors (by threshold percentage)
FORECAST_COLORS = {
    80: [0.3, 0.5, 0.9],   # Light blue
    85: [0.4, 0.4, 0.9],   # Blue-purple
    90: [0.6, 0.3, 0.8],   # Purple (main milestone)
    95: [0.7, 0.2, 0.7],   # Deep purple
    99: [0.8, 0.1, 0.6],   # Magenta
}

# Simple two-tier system (currently implemented)
def get_forecast_color(threshold):
    """Get forecast color based on threshold"""
    if threshold < 90:
        return [0.3, 0.4, 0.9]  # Blue
    else:
        return [0.6, 0.3, 0.8]  # Purple

# Sinkhole Colors (by severity level)
SINKHOLE_COLORS = {
    'critical': [0.9, 0.1, 0.1],    # Dark red
    'high': [1.0, 0.3, 0.1],         # Red-orange
    'medium': [1.0, 0.5, 0.0],       # Orange
    'low': [1.0, 0.65, 0.2],         # Amber
}

# Category groupings (for legend)
CATEGORY_GROUPS = {
    'Language & Text': ['code_generation', 'natural_language_understanding', 'creative_writing', 
                        'writing_quality', 'language_modeling', 'reading_comprehension',
                        'natural_language_inference', 'language_understanding'],
    'Reasoning & Logic': ['mathematical_reasoning', 'competition_math', 'advanced_mathematics',
                          'commonsense_reasoning', 'complex_reasoning', 'advanced_reasoning',
                          'abstract_reasoning', 'boolean_reasoning', 'physical_intuition', 'spatial_reasoning'],
    'Knowledge': ['general_knowledge', 'factual_knowledge', 'scientific_reasoning'],
    'Games': ['game_playing', 'game_strategy'],
    'Technical': ['cybersecurity', 'os_navigation', 'os_interaction', 'terminal_usage', 
                  'agent_reasoning', 'cad_design'],
    'Planning': ['long_horizon_planning'],
    'Other': ['basic_tasks', 'unusual_tasks'],
}

# Helper function to get color for any capability
def get_capability_color(capability_name, default=[0.5, 0.5, 0.5]):
    """
    Get RGB color for a capability.
    Returns default gray if capability not found.
    """
    return CAPABILITY_COLORS.get(capability_name, default)

# Helper function to get sinkhole color
def get_sinkhole_color(severity):
    """Get RGB color for a sinkhole based on severity"""
    return SINKHOLE_COLORS.get(severity, [1.0, 0.5, 0.0])  # Default to orange