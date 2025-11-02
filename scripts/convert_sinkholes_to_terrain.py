"""
Convert Sinkhole Evaluation Markdown to Terrain Map Format
Extracts model failures/vulnerabilities and maps them to terrain sinkholes

Each sinkhole includes:
- Position (x, y, negative z for depth)
- Failure metadata (which models failed, why)
- Severity scoring
"""

import json
import re
import numpy as np
from typing import Dict, List, Tuple, Optional


class SinkholeToTerrainConverter:
    """
    Convert sinkhole evaluation data to terrain format
    """
    
    def __init__(self):
        # Category to position mapping (aligns with capabilities)
        self.category_positions = {
            'constrained_generation': (0.2, 0.3),  # language area
            'spatial_reasoning': (0.55, 0.25),     # games area
            'string_manipulation': (0.2, 0.3),      # language area
            'retroactive_reasoning': (0.65, 0.45),  # complex reasoning
            'self_reference': (0.7, 0.4),           # advanced reasoning
            'logic_puzzle': (0.45, 0.55),           # commonsense reasoning
            'physical_reasoning': (0.5, 0.5),       # physical intuition
            'temporal': (0.4, 0.5),                 # basic tasks
            'arithmetic': (0.75, 0.45),             # mathematical reasoning
            'counting': (0.4, 0.4)                  # basic tasks
        }
        
        # Severity colors (RGB 0-1 range)
        self.severity_colors = {
            'critical': [0.8, 0.1, 0.1],    # dark red
            'high': [0.9, 0.2, 0.1],         # red-orange
            'medium': [1.0, 0.4, 0.0],       # orange
            'low': [1.0, 0.6, 0.2]           # light orange
        }
        
    def parse_markdown(self, md_content: str) -> List[Dict]:
        """
        Parse markdown file and extract sinkhole data
        Returns list of sinkhole records
        """
        sinkholes = []
        
        # Split by sinkhole sections (## sinkhole_XXX)
        sections = re.split(r'##\s+sinkhole_\d+', md_content)
        
        for section in sections[1:]:  # Skip header
            sinkhole = self._parse_sinkhole_section(section)
            if sinkhole:
                sinkholes.append(sinkhole)
        
        return sinkholes
    
    def _parse_sinkhole_section(self, section: str) -> Optional[Dict]:
        """Parse a single sinkhole section"""
        
        # Extract task
        task_match = re.search(r'\*\*Task:\*\*\s+(.+?)(?=\n\n|\*\*)', section, re.DOTALL)
        if not task_match:
            return None
        task = task_match.group(1).strip()
        
        # Extract category
        category_match = re.search(r'\*\*Category:\*\*\s+(\w+)', section)
        category = category_match.group(1) if category_match else 'unknown'
        
        # Extract expected answer
        expected_match = re.search(r'\*\*Expected Answer:\*\*\s+(.+?)(?=\n\n|###)', section, re.DOTALL)
        expected = expected_match.group(1).strip() if expected_match else ''
        
        # Extract model evaluations
        models = {}
        
        # Find CLAUDE section
        claude_section = re.search(r'###\s+CLAUDE\s+```(.+?)```\s+\*\*Correct\?\*\*\s+\[([ X])\]\s+Yes\s+\[([ X])\]\s+No\s+\*\*Evaluation:\*\*\s+(.+?)(?=###|---|\Z)', 
                                   section, re.DOTALL)
        if claude_section:
            models['Claude'] = {
                'response': claude_section.group(1).strip(),
                'correct': 'X' in claude_section.group(2),
                'evaluation': claude_section.group(4).strip()
            }
        
        # Find GROK section
        grok_section = re.search(r'###\s+GROK\s+```(.+?)```\s+\*\*Correct\?\*\*\s+\[([ X])\]\s+Yes\s+\[([ X])\]\s+No\s+\*\*Evaluation:\*\*\s+(.+?)(?=###|---|\Z)', 
                                 section, re.DOTALL)
        if grok_section:
            models['Grok'] = {
                'response': grok_section.group(1).strip(),
                'correct': 'X' in grok_section.group(2),
                'evaluation': grok_section.group(4).strip()
            }
        
        return {
            'task': task,
            'category': category,
            'expected_answer': expected,
            'models': models
        }
    
    def _calculate_severity(self, sinkhole_data: Dict) -> str:
        """
        Calculate severity based on how many models failed
        """
        models = sinkhole_data['models']
        failed_count = sum(1 for m in models.values() if not m['correct'])
        
        if failed_count == len(models):
            return 'critical'  # All models failed
        elif failed_count >= len(models) * 0.75:
            return 'high'
        elif failed_count >= len(models) * 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_depth(self, severity: str, models_data: Dict) -> float:
        """
        Calculate sinkhole depth (negative z value)
        Deeper = more severe
        """
        base_depths = {
            'critical': -80.0,
            'high': -60.0,
            'medium': -40.0,
            'low': -20.0
        }
        
        depth = base_depths.get(severity, -30.0)
        
        # Add jitter for failed models
        failed_count = sum(1 for m in models_data.values() if not m['correct'])
        depth -= failed_count * 5  # Each failure adds depth
        
        return depth
    
    def _get_position(self, category: str, index: int) -> Tuple[float, float]:
        """
        Get x, y position based on category
        Add small jitter to avoid overlaps
        """
        base_pos = self.category_positions.get(category, (0.5, 0.5))
        
        # Add small random offset to avoid exact overlaps
        jitter = 0.03
        x = base_pos[0] + (np.random.random() - 0.5) * jitter
        y = base_pos[1] + (np.random.random() - 0.5) * jitter
        
        # Clamp to valid range
        x = max(0.1, min(0.9, x))
        y = max(0.1, min(0.9, y))
        
        return (x, y)
    
    def convert_to_terrain_format(self, sinkholes: List[Dict]) -> Dict:
        """
        Convert sinkholes to rendering-ready format
        
        Returns structure matching capabilities format:
        {
            'vertices': [[x, y, z], ...],
            'metadata': [{...}, ...],
            'colors': [[r, g, b], ...],
            'indices': [0, 1, 2, ...]
        }
        """
        vertices = []
        metadata = []
        colors = []
        
        for idx, sinkhole in enumerate(sinkholes):
            # Get position
            x, y = self._get_position(sinkhole['category'], idx)
            
            # Calculate severity and depth
            severity = self._calculate_severity(sinkhole)
            z = self._calculate_depth(severity, sinkhole['models'])
            
            # Create vertex
            vertex = [round(float(x), 4), round(float(y), 4), round(float(z), 4)]
            vertices.append(vertex)
            
            # Get color based on severity
            color = self.severity_colors[severity]
            colors.append(color)
            
            # Create metadata
            failed_models = [name for name, data in sinkhole['models'].items() 
                           if not data['correct']]
            passed_models = [name for name, data in sinkhole['models'].items() 
                           if data['correct']]
            
            meta = {
                'type': 'sinkhole',
                'task': sinkhole['task'],
                'category': sinkhole['category'],
                'expected_answer': sinkhole['expected_answer'],
                'severity': severity,
                'depth': z,
                'failed_models': failed_models,
                'passed_models': passed_models,
                'failure_count': len(failed_models),
                'total_tested': len(sinkhole['models']),
                'evaluations': {
                    name: {
                        'correct': data['correct'],
                        'reason': data['evaluation']
                    }
                    for name, data in sinkhole['models'].items()
                }
            }
            metadata.append(meta)
        
        # Create indices
        indices = list(range(len(vertices)))
        
        # Calculate bounds
        vertices_array = np.array(vertices)
        bounds = {
            'min_x': float(vertices_array[:, 0].min()),
            'max_x': float(vertices_array[:, 0].max()),
            'min_y': float(vertices_array[:, 1].min()),
            'max_y': float(vertices_array[:, 1].max()),
            'min_z': float(vertices_array[:, 2].min()),
            'max_z': float(vertices_array[:, 2].max())
        }
        
        # Calculate statistics
        severity_counts = {}
        for m in metadata:
            sev = m['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        category_counts = {}
        for m in metadata:
            cat = m['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return {
            'vertices': vertices,
            'metadata': metadata,
            'colors': colors,
            'indices': indices,
            'bounds': bounds,
            'stats': {
                'total_sinkholes': len(vertices),
                'severity_breakdown': severity_counts,
                'category_breakdown': category_counts,
                'total_failures': sum(m['failure_count'] for m in metadata),
                'models_tested': list(set(
                    model for m in metadata 
                    for model in list(m['failed_models']) + list(m['passed_models'])
                ))
            },
            'config': {
                'coordinate_system': 'cartesian',
                'z_axis': 'failure_depth',
                'severity_colors': self.severity_colors,
                'interpretation': 'Negative z = vulnerability depth, deeper = more severe'
            }
        }
    
    def export_to_json(self, sinkholes: List[Dict], output_path: str):
        """Export sinkholes to JSON file"""
        terrain_data = self.convert_to_terrain_format(sinkholes)
        
        with open(output_path, 'w') as f:
            json.dump(terrain_data, f, indent=2)
        
        print(f"✓ Exported sinkholes to {output_path}")
        print(f"  - Total sinkholes: {terrain_data['stats']['total_sinkholes']}")
        print(f"  - Severity breakdown: {terrain_data['stats']['severity_breakdown']}")
        print(f"  - Categories: {list(terrain_data['stats']['category_breakdown'].keys())}")
        print(f"  - Total failures: {terrain_data['stats']['total_failures']}")
        
        return terrain_data


def main():
    """Main conversion function"""
    # Read markdown file
    with open('data/sinkhole_data/sinkhole_evaluation.md', 'r') as f:
        md_content = f.read()

    # Create converter
    converter = SinkholeToTerrainConverter()

    # Parse sinkholes
    print("Parsing sinkhole evaluations...")
    sinkholes = converter.parse_markdown(md_content)
    print(f"Found {len(sinkholes)} sinkholes")

    # Convert to terrain format
    print("\nConverting to rendering format...")
    terrain_data = converter.export_to_json(
        sinkholes,
        'data/outputs/terrain_sinkholes.json'
    )

    return terrain_data


if __name__ == '__main__':
    terrain_data = main()