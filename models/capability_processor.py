import pandas as pd
import numpy as np
import json
from pathlib import Path

class CapabilityProcessor:
    """Process benchmark data into capability heights over time"""
    
    def __init__(self, combined_data_path='data/processed/combined_benchmarks_cleaned.csv'):
        self.df = pd.read_csv(combined_data_path)
        self.capabilities = self.build_capability_taxonomy()
        self.model_families = self._identify_model_families()
        
    def build_capability_taxonomy(self):
        """Create semantic grouping of capabilities with spatial positions"""
        
        # Get unique capabilities from data
        unique_caps = self.df['capability'].unique()
        
        # Define capability taxonomy with x,y positions
        taxonomy = {}
        
        # Position clusters by category
        positions = {
            # Reasoning cluster (right side)
            'code_generation': (0.65, 0.50),
            'web_development': (0.70, 0.55),
            'mathematical_reasoning': (0.75, 0.45),
            'advanced_mathematics': (0.80, 0.40),
            'competition_math': (0.85, 0.45),
            'advanced_reasoning': (0.70, 0.40),
            'complex_reasoning': (0.65, 0.45),
            'abstract_reasoning': (0.75, 0.35),
            
            # Knowledge cluster (left side)
            'general_knowledge': (0.25, 0.60),
            'factual_knowledge': (0.20, 0.55),
            'scientific_reasoning': (0.30, 0.55),
            'geographic_knowledge': (0.25, 0.50),
            
            # Language cluster (center-left)
            'reading_comprehension': (0.35, 0.65),
            'language_modeling': (0.30, 0.70),
            'language_understanding': (0.40, 0.65),
            'natural_language_inference': (0.35, 0.60),
            'commonsense_reasoning': (0.45, 0.55),
            'boolean_reasoning': (0.40, 0.50),
            'physical_intuition': (0.50, 0.50),
            
            # Agent/Tool cluster (top)
            'agent_reasoning': (0.50, 0.80),
            'terminal_usage': (0.45, 0.85),
            'os_navigation': (0.55, 0.85),
            'os_interaction': (0.60, 0.80),
            'research_ability': (0.50, 0.75),
            'long_horizon_planning': (0.55, 0.75),
            
            # Specialized cluster (bottom)
            'cybersecurity': (0.70, 0.20),
            'game_playing': (0.65, 0.25),
            'game_strategy': (0.60, 0.20),
            'spatial_reasoning': (0.55, 0.25),
            'cad_design': (0.75, 0.25),
            
            # Creative cluster (left-bottom)
            'creative_writing': (0.20, 0.30),
            'writing_quality': (0.25, 0.35),
            
            # Other
            'basic_tasks': (0.40, 0.40),
            'unusual_tasks': (0.50, 0.30),
            'visual_perception': (0.30, 0.40),
            'uncategorized': (0.50, 0.50),
        }
        
        for cap in unique_caps:
            x, y = positions.get(cap, (0.5, 0.5))  # Default center if not mapped
            
            # Get benchmarks for this capability
            benchmarks = self.df[self.df['capability'] == cap]['benchmark'].unique().tolist()
            
            taxonomy[cap] = {
                'name': cap.replace('_', ' ').title(),
                'category': self._get_category(cap),
                'x': x,
                'y': y,
                'benchmarks': benchmarks,
                'description': self._get_description(cap)
            }
        
        return taxonomy
    
    def _get_category(self, cap):
        """Assign high-level category"""
        if 'code' in cap or 'web' in cap:
            return 'coding'
        elif 'math' in cap:
            return 'mathematics'
        elif 'agent' in cap or 'terminal' in cap or 'os_' in cap:
            return 'agents'
        elif 'knowledge' in cap or 'factual' in cap or 'scientific' in cap:
            return 'knowledge'
        elif 'language' in cap or 'writing' in cap or 'reading' in cap:
            return 'language'
        elif 'game' in cap or 'spatial' in cap:
            return 'games'
        else:
            return 'reasoning'
    
    def _get_description(self, cap):
        """Generate description"""
        descriptions = {
            'abstract_reasoning': 'Recognize patterns and solve problems requiring high-level conceptual thinking',
            'advanced_mathematics': 'Solve graduate-level and research mathematics problems',
            'advanced_reasoning': 'Handle complex multi-step reasoning across diverse domains',
            'agent_reasoning': 'Plan and execute multi-step tasks autonomously',
            'basic_tasks': 'Perform fundamental operations and simple problem-solving',
            'boolean_reasoning': 'Answer yes/no questions requiring logical deduction',
            'cad_design': 'Create and manipulate computer-aided design models',
            'code_generation': 'Generate functional code from natural language descriptions',
            'commonsense_reasoning': 'Apply everyday knowledge and intuitive logic',
            'competition_math': 'Solve competition-level mathematics problems (AMC, AIME, IMO)',
            'complex_reasoning': 'Navigate multi-layered logical problems requiring synthesis',
            'creative_writing': 'Generate original, engaging narrative and expressive text',
            'cybersecurity': 'Identify vulnerabilities and solve security-related challenges',
            'factual_knowledge': 'Retrieve and apply specific facts across domains',
            'game_playing': 'Learn and execute strategies in game environments',
            'game_strategy': 'Develop winning approaches in strategic games',
            'general_knowledge': 'Answer questions across diverse academic and cultural domains',
            'geographic_knowledge': 'Understand spatial relationships, locations, and geographic data',
            'language_modeling': 'Predict and generate coherent natural language sequences',
            'language_understanding': 'Comprehend meaning, context, and nuance in text',
            'long_horizon_planning': 'Plan and reason about extended sequences of actions',
            'mathematical_reasoning': 'Solve math problems with step-by-step logical reasoning',
            'natural_language_inference': 'Determine logical relationships between text passages',
            'os_interaction': 'Navigate and manipulate operating system interfaces',
            'os_navigation': 'Find and access files and programs within operating systems',
            'physical_intuition': 'Apply understanding of physical laws and object behavior',
            'reading_comprehension': 'Extract meaning and answer questions from written passages',
            'research_ability': 'Gather, synthesize, and analyze information from multiple sources',
            'scientific_reasoning': 'Apply scientific methods and domain knowledge to problems',
            'spatial_reasoning': 'Understand and manipulate objects in 2D and 3D space',
            'terminal_usage': 'Execute commands and navigate command-line interfaces',
            'unusual_tasks': 'Handle novel or atypical challenges outside standard benchmarks',
            'visual_perception': 'Process and interpret visual information and imagery',
            'web_development': 'Create and debug web applications and interfaces',
            'writing_quality': 'Produce well-structured, grammatically correct, compelling text',
        }
        return descriptions.get(cap, f"Performance on {cap.replace('_', ' ')} tasks")
    
    def normalize_score(self, score, benchmark):
        """Normalize scores to 0-1 range"""
        # Most benchmarks are already 0-100 (accuracy)
        if pd.isna(score):
            return None
        
        if score > 1.0:
            return score / 100.0
        
        return score
    
    def interpolate_missing_years(self, results, target_years=[2019, 2020, 2021, 2022, 2023, 2024, 2025]):
        """Fill gaps with linear interpolation"""

        # Iterate over model families first
        for model_family in results:
            for cap_id, data in results[model_family].items():
                heights = data['heights']
                available_years = sorted([int(y) for y in heights.keys()])

                if len(available_years) == 0:
                    continue

                # If we only have one year, extrapolate backwards with slight decline
                if len(available_years) == 1:
                    year = available_years[0]
                    height = heights[str(year)]

                    for target_year in target_years:
                        if target_year < year and str(target_year) not in heights:
                            # Assume 5% decline per year going backwards
                            years_back = year - target_year
                            past_height = height * (0.95 ** years_back)
                            heights[str(target_year)] = round(past_height, 3)
                        elif target_year > year and str(target_year) not in heights:
                            # Assume 3% growth per year going forward
                            years_forward = target_year - year
                            future_height = min(height * (1.03 ** years_forward), 1.0)
                            heights[str(target_year)] = round(future_height, 3)
                    continue

                # Linear interpolation between known points
                for i in range(len(available_years) - 1):
                    y1, y2 = available_years[i], available_years[i + 1]
                    h1, h2 = heights[str(y1)], heights[str(y2)]

                    for year in range(y1 + 1, y2):
                        if str(year) not in heights:
                            t = (year - y1) / (y2 - y1)
                            heights[str(year)] = round(h1 + t * (h2 - h1), 3)

                # Extrapolate before first year
                if available_years[0] > min(target_years):
                    first_year = available_years[0]
                    first_height = heights[str(first_year)]

                    for year in target_years:
                        if year < first_year:
                            years_back = first_year - year
                            past_height = first_height * (0.95 ** years_back)
                            heights[str(year)] = round(past_height, 3)

                # Extrapolate after last year
                if available_years[-1] < max(target_years):
                    last_year = available_years[-1]
                    last_height = heights[str(last_year)]

                    for year in target_years:
                        if year > last_year:
                            years_forward = year - last_year
                            future_height = min(last_height * (1.03 ** years_forward), 1.0)
                            heights[str(year)] = round(future_height, 3)

        return results
    
    def _identify_model_families(self):
        """Map organizations to model families"""
        
        if 'org' not in self.df.columns:
            return {}
        
        families = {}
        for org in self.df['org'].unique():
            org_lower = str(org).lower()
            
            # Major labs (top tier)
            if 'openai' in org_lower:
                families[org] = 'openai'
            elif 'anthropic' in org_lower:
                families[org] = 'anthropic'
            elif any(x in org_lower for x in ['google', 'deepmind']):
                families[org] = 'google'
            elif 'meta' in org_lower:
                families[org] = 'meta'
            
            # Chinese labs (tier 2)
            elif any(x in org_lower for x in ['alibaba', 'baichuan', 'deepseek', '01.ai', 'moonshot', 'zhipu']):
                families[org] = 'chinese_labs'
            
            # Open source leaders
            elif any(x in org_lower for x in ['mistral', 'technology innovation']):  # TII = Falcon
                families[org] = 'mistral_tii'
            
            # Big tech (tier 2)
            elif 'microsoft' in org_lower:
                families[org] = 'microsoft'
            elif 'amazon' in org_lower:
                families[org] = 'amazon'
            elif 'nvidia' in org_lower:
                families[org] = 'nvidia'
            
            # Startups
            elif any(x in org_lower for x in ['xai', 'inflection', 'reka', 'minimax', 'cohere']):
                families[org] = 'startups'
            
            # Research/Academic
            elif any(x in org_lower for x in ['eleutherai', 'hugging face', 'allen institute', 'databricks', 'mosaicml', 'salesforce']):
                families[org] = 'research_open'
            
            else:
                families[org] = 'other'
        
        return families
    
    def calculate_capability_height(self, capability, year, model_family='all', return_top_models=False):
        """Calculate height for a capability in a given year, optionally returning top models"""
        
        # Filter for capability and year
        mask = (
            (self.df['capability'] == capability) &
            (self.df['year'] == year)
        )
        
        # Apply model family filter if specified
        if model_family != 'all' and 'org' in self.df.columns:
            family_orgs = [org for org, fam in self.model_families.items() if fam == model_family]
            mask &= self.df['org'].isin(family_orgs)
        
        data = self.df[mask]
        
        if len(data) == 0:
            return (None, []) if return_top_models else None
        
        # Get best score for each benchmark
        scores = []
        top_models = []  # Store which models achieved top scores
        
        for benchmark in data['benchmark'].unique():
            bench_data = data[data['benchmark'] == benchmark]
            if 'score' in bench_data.columns:
                # Find best score
                best_score = bench_data['score'].max()
                
                if not pd.isna(best_score):
                    normalized = self.normalize_score(best_score, benchmark)
                    if normalized is not None:
                        scores.append(normalized)
                        
                        # Find which model(s) achieved this score
                        best_rows = bench_data[bench_data['score'] == best_score]
                        for _, row in best_rows.iterrows():
                            model_info = {
                                'model': row.get('model', 'Unknown'),
                                'org': row.get('org', 'Unknown'),
                                'benchmark': benchmark,
                                'score': float(best_score),
                                'normalized_score': normalized,
                                'date': row.get('date', None)
                            }
                            top_models.append(model_info)
        
        if len(scores) == 0:
            return (None, []) if return_top_models else None
        
        height = np.mean(scores)
        
        if return_top_models:
            return float(height), top_models
        return float(height)

    def calculate_all_heights(self, years=None, model_families=None):
        """Calculate heights for all capabilities across years and model families"""
        
        if years is None:
            years = sorted(self.df['year'].dropna().unique().astype(int).tolist())
        
        if model_families is None:
            model_families = [
                'all',
                'openai', 
                'anthropic', 
                'google', 
                'meta',
                'mistral_tii',
                'chinese_labs',
                'microsoft',
                'startups',
                'research_open'
            ]
        
        results = {}
        
        print(f"\nProcessing {len(model_families)} model families...")
        
        for model_family in model_families:
            print(f"  Processing {model_family}...", end=' ')
            results[model_family] = {}
            
            for cap_id, cap_data in self.capabilities.items():
                results[model_family][cap_id] = {
                    'name': cap_data['name'],
                    'category': cap_data['category'],
                    'x': cap_data['x'],
                    'y': cap_data['y'],
                    'description': cap_data['description'],
                    'benchmarks': cap_data['benchmarks'],
                    'heights': {},
                    'top_models': {}  # NEW: Store top models per year
                }
                
                for year in years:
                    height, top_models = self.calculate_capability_height(
                        cap_id, year, model_family, return_top_models=True
                    )
                    
                    if height is not None:
                        results[model_family][cap_id]['heights'][str(year)] = round(height, 3)
                        
                        # Store top 3 models for this capability/year
                        # Sort by normalized score
                        top_models_sorted = sorted(
                            top_models, 
                            key=lambda x: x['normalized_score'], 
                            reverse=True
                        )
                        
                        results[model_family][cap_id]['top_models'][str(year)] = top_models_sorted
            
            caps_with_data = sum(1 for cap in results[model_family].values() if cap['heights'])
            print(f"✓ ({caps_with_data} capabilities)")
        
        return results
    
    def save_results(self, results, output_path='data/processed/capability_heights.json'):
        """Save processed capabilities with model family breakdown"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Clean NaN values before saving
        def clean_nan(obj):
            """Recursively replace NaN with None"""
            if isinstance(obj, dict):
                return {k: clean_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan(item) for item in obj]
            elif isinstance(obj, float):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return obj
            return obj
        
        cleaned_results = clean_nan(results)
        
        with open(output_path, 'w') as f:
            json.dump(cleaned_results, f, indent=2)
        
        print(f"✓ Saved capability heights (all model families) to {output_path}")


if __name__ == '__main__':
    print("="*70)
    print("PROCESSING CAPABILITIES")
    print("="*70 + "\n")
    
    # Initialize processor
    processor = CapabilityProcessor()
    
    print(f"✓ Found {len(processor.capabilities)} capabilities")
    print(f"✓ Years available: {sorted(processor.df['year'].dropna().unique().astype(int).tolist())}")
    
    # Calculate heights
    print("\nCalculating heights for all capabilities...")
    results = processor.calculate_all_heights()
    
    # Interpolate missing years
    print("Interpolating missing years...")
    results = processor.interpolate_missing_years(results)
    
    # Save
    processor.save_results(results)
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    # Show summary for 'all' model family
    for cap_id, data in list(results['all'].items())[:5]:
        print(f"\n {data['name']}:")
        print(f"   Category: {data['category']}")
        print(f"   Position: ({data['x']}, {data['y']})")
        print(f"   Benchmarks: {', '.join(data['benchmarks'][:3])}...")
        print(f"   Heights: {data['heights']}")

    print("\n✓ Ready for ML models!")