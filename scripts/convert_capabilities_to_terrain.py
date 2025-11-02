"""
Convert Capabilities Heights JSON to Rendering-Ready Terrain Map Format
Optimized for 3D graphics engines (Three.js, WebGL, Unity, etc.)

Output format:
- vertices: flat array of [x, y, z] coordinates
- metadata: parallel array with hover data
- indices: for mesh rendering
- colors: per-vertex colors based on capability (from unified color scheme)
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
from terrain_colors import CAPABILITY_COLORS, get_capability_color, CATEGORY_GROUPS


class RenderingTerrainConverter:
    """
    Convert capabilities to rendering-optimized format
    Uses unified color scheme from terrain_colors.py
    """
    
    def __init__(self, capabilities_data):
        self.capabilities = capabilities_data
        self.org_filter = 'all'
        
        # Use unified color scheme (imported from terrain_colors.py)
        # No longer defining colors here - single source of truth!
        
    def set_org_filter(self, org_name):
        """Set which organization's data to use"""
        valid_orgs = ['all', 'openai', 'anthropic', 'google', 'meta', 
                     'mistral_tii', 'chinese_labs', 'microsoft', 'startups', 'research_open']
        if org_name in valid_orgs:
            self.org_filter = org_name
        else:
            print(f"Warning: {org_name} not found, using 'all'")
            self.org_filter = 'all'
    
    def _calculate_velocity(self, heights_dict):
        """Calculate improvement velocity"""
        if len(heights_dict) < 2:
            return {
                'velocity': 0.0,
                'trend': 'stable',
                'acceleration': 0.0
            }
        
        years = sorted([int(y) for y in heights_dict.keys()])
        scores = [heights_dict[str(y)] for y in years]
        
        velocities = []
        for i in range(1, len(scores)):
            year_diff = years[i] - years[i-1]
            score_diff = scores[i] - scores[i-1]
            velocity = (score_diff / scores[i-1]) * 100 / year_diff if scores[i-1] > 0 else 0
            velocities.append(velocity)
        
        avg_velocity = np.mean(velocities) if velocities else 0
        
        acceleration = 0.0
        trend = 'stable'
        if len(velocities) >= 2:
            acceleration = velocities[-1] - velocities[-2]
            if acceleration > 0.5:
                trend = 'accelerating'
            elif acceleration < -0.5:
                trend = 'decelerating'
        
        return {
            'velocity': round(float(avg_velocity), 2),
            'trend': trend,
            'acceleration': round(float(acceleration), 2),
            'recent_velocity': round(float(velocities[-1]), 2) if velocities else 0
        }
    
    def _get_capability_color(self, capability_name, velocity=0):
        """
        Get RGB color for capability with optional velocity adjustment
        Uses unified color scheme from terrain_colors.py
        
        Returns [r, g, b] in 0-1 range
        """
        # Get base color from unified scheme
        base_color = get_capability_color(capability_name)
        
        # Optionally adjust brightness based on velocity
        # High velocity = brighter, low velocity = darker
        if velocity != 0:
            velocity_factor = min(1.0, max(0.5, 1.0 + velocity / 50.0))
            color = [c * velocity_factor for c in base_color]
            return [min(1.0, max(0.0, c)) for c in color]
        
        return base_color
    
    def _create_vertex_data(self, capability_name, capability_data, year, model_info):
        """
        Create vertex and metadata for a single point
        Returns (vertex, metadata, color)
        """
        # Get position
        x = capability_data.get('x', 0.5)
        y = capability_data.get('y', 0.5)
        
        # Height is the score
        height = capability_data['heights'].get(str(year), 0)
        z = height * 100 if height < 1 else height
        
        # Vertex position [x, y, z]
        vertex = [round(float(x), 4), round(float(y), 4), round(float(z), 4)]
        
        # Calculate velocity
        velocity_data = self._calculate_velocity(capability_data.get('heights', {}))
        
        # Get color using unified scheme
        color = self._get_capability_color(capability_name, velocity_data['velocity'])
        
        # Metadata for hover
        metadata = {
            'type': 'baseline',  # Mark as baseline node
            'capability': capability_name,
            'capability_display': capability_data.get('name', capability_name),
            'model': model_info.get('model', 'Unknown'),
            'organization': model_info.get('org', 'Unknown'),
            'release_date': model_info.get('date', f'{year}-01-01'),
            'benchmark': model_info.get('benchmark', 'Unknown'),
            'score': round(float(model_info.get('score', 0)), 4),
            'normalized_score': round(float(model_info.get('normalized_score', model_info.get('score', 0))), 4),
            'category': capability_data.get('category', 'unknown'),
            'description': capability_data.get('description', ''),
            'velocity': velocity_data['velocity'],
            'velocity_trend': velocity_data['trend'],
            'year': year
        }
        
        return vertex, metadata, color
    
    def convert_to_rendering_format(self):
        """
        Convert to rendering-optimized format
        
        Returns:
        {
            'vertices': [[x, y, z], [x, y, z], ...],  # Flat array of positions
            'metadata': [{...}, {...}, ...],           # Parallel array with hover data
            'colors': [[r, g, b], [r, g, b], ...],    # Per-vertex colors (from unified scheme)
            'indices': [0, 1, 2, 3, 4, 5, ...],       # For indexed rendering
            'bounds': {min_x, max_x, min_y, max_y, min_z, max_z},
            'config': {...}
        }
        """
        if self.org_filter not in self.capabilities:
            raise ValueError(f"Organization filter '{self.org_filter}' not found in data")
        
        org_data = self.capabilities[self.org_filter]
        
        vertices = []
        metadata = []
        colors = []
        
        # Process each capability
        for capability_name, capability_data in org_data.items():
            top_models = capability_data.get('top_models', {})
            
            for year_str, models_list in top_models.items():
                try:
                    year = int(year_str)
                    for model_info in models_list:
                        vertex, meta, color = self._create_vertex_data(
                            capability_name,
                            capability_data,
                            year,
                            model_info
                        )
                        vertices.append(vertex)
                        metadata.append(meta)
                        colors.append(color)
                except (ValueError, TypeError):
                    continue
        
        # Create indices (simple sequential for point cloud)
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
        
        # Get unique capabilities for legend (using unified color scheme)
        capabilities_list = list(set(m['capability'] for m in metadata))
        capability_legend = {
            cap: {
                'color': get_capability_color(cap),
                'count': sum(1 for m in metadata if m['capability'] == cap),
                'category_group': next((group for group, caps in CATEGORY_GROUPS.items() if cap in caps), 'Other')
            }
            for cap in capabilities_list
        }
        
        return {
            'vertices': vertices,
            'metadata': metadata,
            'colors': colors,
            'indices': indices,
            'bounds': bounds,
            'stats': {
                'total_points': len(vertices),
                'capabilities': len(set(m['capability'] for m in metadata)),
                'models': len(set(m['model'] for m in metadata)),
                'organizations': len(set(m['organization'] for m in metadata)),
                'date_range': {
                    'earliest': min((m['release_date'] for m in metadata if m['release_date'] != 'Unknown'), default='Unknown'),
                    'latest': max((m['release_date'] for m in metadata if m['release_date'] != 'Unknown'), default='Unknown')
                }
            },
            'config': {
                'coordinate_system': 'cartesian',
                'z_axis': 'performance_score',
                'scale': {
                    'x': 1.0,
                    'y': 1.0,
                    'z': 100.0
                },
                'capabilities': capability_legend,
                'velocity_thresholds': {
                    'high': 10.0,
                    'medium': 5.0,
                    'low': 0.0
                },
                'color_scheme': 'unified',
                'color_source': 'terrain_colors.py'
            },
            'generated_at': datetime.now().isoformat(),
            'organization_filter': self.org_filter
        }
    
    def export_to_json(self, output_path):
        """Export to JSON file"""
        terrain_data = self.convert_to_rendering_format()
        
        with open(output_path, 'w') as f:
            json.dump(terrain_data, f, indent=2)
        
        print(f"✓ Exported rendering-ready terrain to {output_path}")
        print(f"  - Total vertices: {terrain_data['stats']['total_points']}")
        print(f"  - Capabilities: {terrain_data['stats']['capabilities']}")
        print(f"  - Models: {terrain_data['stats']['models']}")
        print(f"  - Organizations: {terrain_data['stats']['organizations']}")
        print(f"  - Bounds: x[{terrain_data['bounds']['min_x']:.2f}, {terrain_data['bounds']['max_x']:.2f}] "
              f"y[{terrain_data['bounds']['min_y']:.2f}, {terrain_data['bounds']['max_y']:.2f}] "
              f"z[{terrain_data['bounds']['min_z']:.2f}, {terrain_data['bounds']['max_z']:.2f}]")
        
        return terrain_data
    
    def export_to_binary(self, output_path):
        """
        Export to binary format for even faster loading
        Creates .bin file with:
        - Header (metadata size)
        - Metadata JSON
        - Vertex data (float32)
        - Color data (float32)
        - Index data (uint32)
        """
        terrain_data = self.convert_to_rendering_format()
        
        # Convert to binary
        vertices_bin = np.array(terrain_data['vertices'], dtype=np.float32).tobytes()
        colors_bin = np.array(terrain_data['colors'], dtype=np.float32).tobytes()
        indices_bin = np.array(terrain_data['indices'], dtype=np.uint32).tobytes()
        
        # Create metadata without the large arrays
        metadata_json = {
            'metadata': terrain_data['metadata'],
            'stats': terrain_data['stats'],
            'config': terrain_data['config'],
            'bounds': terrain_data['bounds'],
            'organization_filter': terrain_data['organization_filter'],
            'generated_at': terrain_data['generated_at'],
            'binary_layout': {
                'vertices_offset': 0,
                'vertices_count': len(terrain_data['vertices']),
                'colors_offset': 0,
                'colors_count': len(terrain_data['colors']),
                'indices_offset': 0,
                'indices_count': len(terrain_data['indices'])
            }
        }
        
        metadata_str = json.dumps(metadata_json).encode('utf-8')
        metadata_size = len(metadata_str)
        
        # Write binary file
        with open(output_path, 'wb') as f:
            # Write metadata size (4 bytes)
            f.write(metadata_size.to_bytes(4, byteorder='little'))
            # Write metadata JSON
            f.write(metadata_str)
            # Write vertex data
            f.write(vertices_bin)
            # Write color data
            f.write(colors_bin)
            # Write index data
            f.write(indices_bin)
        
        print(f"✓ Exported binary terrain to {output_path}")
        print(f"  - File size: {len(metadata_str) + len(vertices_bin) + len(colors_bin) + len(indices_bin) + 4} bytes")


def main():
    """Main conversion function"""
    # Load capabilities data
    with open('data/intermediate/capability_heights.json', 'r') as f:
        capabilities_data = json.load(f)

    # Create converter
    converter = RenderingTerrainConverter(capabilities_data)

    # Convert for 'all' organizations view
    print("Converting capabilities to rendering-ready format...")
    print(f"Organization filter: {converter.org_filter}")
    print(f"Using unified color scheme from terrain_colors.py\n")

    # Export JSON format
    terrain_data = converter.export_to_json('data/outputs/terrain_rendering_all.json')

    # Export binary format for faster loading
    print()
    converter.export_to_binary('data/outputs/terrain_rendering_all.bin')
    
    return terrain_data


if __name__ == '__main__':
    terrain_data = main()