import pandas as pd
from pathlib import Path
import json
import os
from datetime import datetime

print("✓ All imports complete, defining functions...")

def get_available_benchmarks(data_dir='data/raw/epoch_benchmark_data'):
    """Scan directory and find all available CSV files"""
    
    path = Path(data_dir)
    if not path.exists():
        print(f"❌ Directory not found: {data_dir}")
        return []
    
    csv_files = list(path.glob('*.csv'))
    
    # Extract benchmark names (remove _external and .csv)
    benchmarks = []
    for f in csv_files:
        name = f.stem  # filename without extension
        # Remove _external suffix if present
        if name.endswith('_external'):
            name = name[:-9]  # Remove last 9 chars (_external)
        benchmarks.append((name, str(f)))
    
    return benchmarks

# Capability mapping
CAPABILITY_MAP = {
    # Coding
    'live_bench': 'code_generation',
    'aider_polyglot': 'code_generation',
    'swe_bench_verified': 'code_generation',
    'webdev_arena': 'web_development',
    
    # Math & Reasoning
    'gsm8k': 'mathematical_reasoning',
    'math_level_5': 'mathematical_reasoning',
    'gpqa_diamond': 'advanced_reasoning',
    'frontiermath': 'advanced_mathematics',
    'frontiermath_tier_4': 'advanced_mathematics',
    'otis_mock_aime_2024_2025': 'competition_math',
    
    # General reasoning
    'mmlu': 'general_knowledge',
    'arc_ai2': 'commonsense_reasoning',
    'arc_agi': 'abstract_reasoning',
    'hella_swag': 'commonsense_reasoning',
    'wino_grande': 'commonsense_reasoning',
    'bbh': 'complex_reasoning',
    
    # Q&A / Language
    'trivia_qa': 'factual_knowledge',
    'open_book_qa': 'reading_comprehension',
    'bool_q': 'boolean_reasoning',
    'common_sense_qa_2': 'commonsense_reasoning',
    'piqa': 'physical_intuition',
    'lambada': 'language_modeling',
    'adversarial_nli': 'natural_language_inference',
    'superglue': 'language_understanding',
    
    # Specialized
    'science_qa': 'scientific_reasoning',
    'geobench': 'geographic_knowledge',
    'cybench': 'cybersecurity',
    'balrog': 'game_playing',
    'gso': 'spatial_reasoning',
    'cad_eval': 'cad_design',
    'factorio_learning_environment': 'game_strategy',
    
    # Agent/Tool
    'terminalbench': 'terminal_usage',
    'os_world': 'os_navigation',
    'os_universe': 'os_interaction',
    'the_agent_company': 'agent_reasoning',
    'deepresearchbench': 'research_ability',
    
    # Other
    'simplebench': 'basic_tasks',
    'fictionlivebench': 'creative_writing',
    'lech_mazur_writing': 'writing_quality',
    'metr_time_horizons': 'long_horizon_planning',
    'vpct': 'visual_perception',
    'weirdml': 'unusual_tasks',
}

def load_benchmark(filepath, benchmark_name):
    """Load a benchmark CSV from full filepath"""
    try:
        df = pd.read_csv(filepath)
        cols_preview = df.columns.tolist()[:8]
        print(f"✓ {benchmark_name}: {len(df)} rows | Columns: {cols_preview}...")
        return df
    except Exception as e:
        print(f"✗ Error loading {benchmark_name}: {e}")
        return None

def standardize_dataframe(df, benchmark_name):
    """Standardize column names"""
    
    result = df.copy()

    # Flexible column matching (case insensitive)
    def find_column(possible_names):
        for name in possible_names:
            for col in df.columns:
                if col.lower() == name.lower():
                    return col
        return None

    # Find model column
    model_col = 'Model version'
    result['model'] = result[model_col]
    
    # Find date column
    date_col = 'Release date'
    result['date'] = result[date_col]
    result['date'] = pd.to_datetime(result['date'])

    # Create year column
    result['year'] = result['date'].dt.year

    # Find organization column
    org_col = 'Organization'
    result['org'] = result[org_col]

    # Find country column
    country_col = 'Country'
    result['country'] = result[country_col]

    # Find Training compute (FLOPs) column
    compute_col = 'Training compute (FLOPs)'
    matching_cols = [x for x in df.columns if 'training compute' in x.lower()]
    if matching_cols:
        compute_col = matching_cols[0]
        result['training_compute_flops'] = result[compute_col]
    
    # Find score column
    score_col = find_column(['average_score', 'score', 'stderr', 'performance', 'result', 'Best score (across scorers)', 'Accuracy', 'Production Score', 'Percent correct', 'Average progress', '120k token score', 'Mean score', 'Overall pass (%)', 'Global average', 'EM', 'Score (AVG@5)', 'Weighted Score', 'Average', 'ACW Avg Score', 'Score OPT@1', 'Unguided % Solved', '% Score', 'Challenge score', 'Accuracy mean', 'Overall accuracy'])
    if score_col:
        result['score'] = pd.to_numeric(result[score_col], errors='coerce')
    
    result['benchmark'] = benchmark_name
    
    # Keep only standard columns
    standard_cols = ['model', 'benchmark', 'date', 'org', 'country', 'training_compute_flops', 'score']
    available = [col for col in standard_cols if col in result.columns]
    
    return result[available]

def aggregate_all_benchmarks(data_dir='data/raw/epoch_benchmark_data'):
    """Load all available benchmarks"""
    
    print("="*70)
    print("SCANNING FOR BENCHMARKS")
    print("="*70 + "\n")
    
    # Get all CSV files
    available = get_available_benchmarks(data_dir)
    print(f"Found {len(available)} CSV files\n")
    
    all_data = []
    loaded = []
    skipped = []
    
    for benchmark_name, filepath in available:
        # Skip non-benchmark files
        if benchmark_name in ['README', 'epoch_capabilities_index']:
            continue
        
        df = load_benchmark(filepath, benchmark_name)
        
        if df is not None:
            # Standardize
            df_std = standardize_dataframe(df, benchmark_name)
            
            # Add capability if we have a mapping
            capability = CAPABILITY_MAP.get(benchmark_name, 'uncategorized')
            df_std['capability'] = capability
            
            all_data.append(df_std)
            loaded.append(benchmark_name)
        else:
            skipped.append(benchmark_name)

    
    if len(all_data) == 0:
        print("\n❌ No data loaded!")
        return None
    
    # Combine all
    combined = pd.concat(all_data, ignore_index=True)
    return combined

if __name__ == '__main__':
    # Load all data
    df = aggregate_all_benchmarks()
    
    if df is not None:
        
        # Save combined dataset
        output_path = 'data/intermediate/combined_benchmarks.csv'
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"\n✓ Saved: {output_path}")

        # Save summary
        summary = {
            'total_records': len(df),
            'benchmarks': sorted(df['benchmark'].unique().tolist()),
            'capabilities': sorted(df['capability'].unique().tolist()),
        }

        with open('data/intermediate/data_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Saved: data/intermediate/data_summary.json")

        # Show what capabilities we have
        print(f"\n{'='*70}")
        print("CAPABILITIES COVERAGE")
        print(f"{'='*70}")
        cap_counts = df['capability'].value_counts()
        for cap, count in cap_counts.items():
            benchmarks = df[df['capability'] == cap]['benchmark'].unique()
            print(f"  {cap}: {count} records ({len(benchmarks)} benchmarks)")