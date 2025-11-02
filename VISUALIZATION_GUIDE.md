# AI Capability Terrain Map - Visualization Guide

## Overview

This is a 3D early warning system that maps AI capabilities as literal terrain. The visualization helps researchers, policymakers, and developers monitor AI progress in real-time and anticipate breakthrough capabilities.

## Visual Elements

### 1. Terrain Surface

The main terrain surface represents AI capability landscape:

- **Mountain Peaks** (High elevation): Mastered capabilities with high performance scores
- **Hills** (Medium elevation): Emerging capabilities showing improvement
- **Valleys** (Low elevation): Weak or nascent capabilities
- **Base Terrain** (Near zero): Areas with minimal capability data

**Color Scheme:**
- Capabilities are color-coded by category (coding, reasoning, spatial, etc.)
- Wireframe overlay provides depth perception

### 2. Sinkholes (Red Pits)

Sinkholes are inverted cones that represent **tasks AI should handle but inexplicably fails at**.

**Visual Properties:**
- **Depth**: Represents severity
  - -20 units: Low severity (yellow-orange)
  - -45 units: Medium severity (orange)
  - -90 units: Critical severity (deep red)
- **Color**: RGB values indicate severity level
- **Rim Ring**: Glowing edge for visibility
- **Particle Effects**: Critical sinkholes emit light particles

**Hover to See:**
- Task description
- Category (e.g., spatial_reasoning, self_reference)
- Severity level
- Failure rate (e.g., "Failed: 2/2 models")

**Example Sinkholes:**
- Letter counting tasks
- Multi-constraint generation
- Self-referential logic puzzles
- Basic spatial reasoning

### 3. Forecast Nodes (Glowing Spheres)

Forecast nodes are translucent spheres predicting **future capability breakthroughs**.

**Visual Properties:**
- **Height**: Higher = harder threshold (85%, 90%, 95% performance)
- **Color**:
  - Blue: 85% threshold (more achievable)
  - Purple: 90-95% threshold (harder)
- **Glow Intensity**: Increases on hover
- **Position**: Distributed around terrain based on capability type

**Hover to See:**
- Capability name
- Performance threshold
- Predicted achievement date
- Days until breakthrough
- Confidence interval bounds

**Warning Indicators:**
- Yellow cone above node = Breakthrough imminent (< 365 days)

**Example Nodes:**
- "Code Generation - 90% by 2068"
- "Physical Intuition - 95% by 2030"
- "Advanced Mathematics - 85% by 2027"

### 4. Capability Markers (Colored Spheres)

Small glowing spheres on the terrain surface mark specific AI capabilities.

**Visual Properties:**
- **Color**: Category-specific
  - Green (#00ff88): Coding
  - Red (#ff6b6b): Reasoning
  - Cyan (#4ecdc4): Knowledge
  - Yellow (#ffe66d): Spatial
  - Blue (#a8dadc): Language
  - Orange (#ff9f1c): Physical
- **Emissive Glow**: Increases on hover
- **Position**: Based on normalized (x, y) coordinates from capability data

**Hover to See:**
- Full capability name
- Category
- Current performance metrics

### 5. UI Overlay

The interface provides controls and information:

**Top Center:**
- Title and subtitle

**Left Panel (Legend):**
- Visual guide to elements
- Color codes and meanings

**Left Bottom (Controls):**
- Toggle sinkholes on/off
- Toggle forecast nodes on/off
- Toggle capability labels on/off

**Right Top (Stats):**
- Number of active sinkholes
- Number of forecast nodes
- Capabilities tracked

**Right Bottom (Instructions):**
- Camera controls guide

## Data Understanding

### Color Coding System

**Sinkholes (by Severity):**
```javascript
Critical: [0.8, 0.1, 0.1]  // Dark red
Medium:   [1.0, 0.4, 0.0]  // Orange
Low:      [1.0, 0.6, 0.2]  // Light orange
```

**Forecast Nodes (by Threshold):**
```javascript
85% threshold: Blue (#4488ff)
90% threshold: Purple (#aa44ff)
95% threshold: Purple (#aa44ff)
```

**Capabilities (by Category):**
```javascript
Coding:    #00ff88 (Green)
Reasoning: #ff6b6b (Red)
Knowledge: #4ecdc4 (Cyan)
Spatial:   #ffe66d (Yellow)
Language:  #a8dadc (Blue)
Physical:  #ff9f1c (Orange)
```

### Size and Scale

- **Terrain Grid**: 100x100 units
- **Terrain Segments**: 100x100 mesh resolution
- **Capability Height Scaling**: Performance scores (0-1) × 30 units
- **Sinkhole Radius**: 0.8-2.0 units (base to rim)
- **Forecast Node Radius**: 1.2 units
- **Forecast Node Ring**: 1.5-2.0 units

### Coordinate System

- **X-axis**: West (-50) to East (+50)
- **Y-axis**: Down (negative sinkholes) to Up (positive peaks)
- **Z-axis**: South (-50) to North (+50)

Capability data uses normalized coordinates (0-1) which are mapped to world space:
```javascript
worldX = (x - 0.5) * 100  // 0-1 → -50 to +50
worldZ = (y - 0.5) * 100  // 0-1 → -50 to +50
worldY = height * 30      // 0-1 → 0 to 30
```

## Interaction Guide

### Camera Controls

1. **Orbit**: Left-click and drag to rotate around the terrain
2. **Pan**: Right-click and drag to move the camera
3. **Zoom**: Scroll wheel to zoom in/out
4. **Limits**:
   - Min distance: 20 units
   - Max distance: 200 units
   - Max polar angle: ~65° (prevents going below terrain)

### Hover Interactions

Hovering over any element shows a tooltip with detailed information:

- **Sinkholes**: Task details, severity, failure stats
- **Forecast Nodes**: Capability, threshold, prediction date, confidence
- **Capability Markers**: Name and category

Hovered elements also increase in brightness/emissive intensity.

### Toggle Controls

Use the left-bottom control panel to show/hide:
- Sinkholes
- Forecast Nodes
- Capability Labels

## Interpreting the Visualization

### Identifying Critical Areas

1. **Deep Red Sinkholes**: These are critical failures that affect multiple models. Hover to see which specific tasks AI struggles with.

2. **Near-term Forecast Nodes**: Look for nodes with yellow warning cones (< 365 days). These represent imminent capability breakthroughs.

3. **Capability Clusters**: Groups of same-colored spheres indicate related capabilities. Height differences show performance variation within a category.

### Tracking Progress

- **Height Changes**: Compare capability marker heights over time to track improvement
- **Sinkhole Resolution**: If a sinkhole disappears in updates, that failure mode has been solved
- **Forecast Node Achievement**: When a forecast date passes, check if the capability actually reached the threshold

### Early Warning Signals

The system provides three types of early warnings:

1. **Anomaly Detection**: Sudden height changes in terrain indicate capability jumps
2. **Multi-Model Convergence**: Multiple forecast nodes in the same area suggest breakthrough potential
3. **Leading Indicators**: Near-term forecast nodes (< 6 months) require attention

## Performance Optimization

For smoother visualization:

1. **Reduce Mesh Resolution**: Lower `segments` in TerrainMap.jsx
2. **Disable Shadows**: Comment out `castShadow` in components
3. **Limit Visible Elements**: Use toggle controls to hide unused layers
4. **Lower Draw Distance**: Reduce max camera distance

## Technical Details

### Data Pipeline

```
ML Models → JSON Output → Frontend Loader → Three.js Rendering
```

1. Python scripts generate predictions
2. Data exported to JSON in `/data/outputs/` and `/predictions/`
3. Frontend components fetch and parse JSON
4. Three.js creates 3D geometry from parsed data
5. React manages state and interactivity

### Rendering Pipeline

```
App.jsx → Canvas → TerrainMap → Geometry + Materials + Lights
                 ├─ Sinkholes → Cylinders + Rings + Lights
                 ├─ ForecastNodes → Spheres + Rings + Lights
                 └─ UI Overlay → React DOM
```

## Future Enhancements

Potential additions to the visualization:

- [ ] Timeline slider to view historical terrain evolution
- [ ] Anomaly alerts (flashing indicators)
- [ ] Benchmark source filtering (Epoch AI vs Papers With Code)
- [ ] Model comparison mode
- [ ] Export terrain as image/video
- [ ] VR mode for immersive exploration
- [ ] Real-time data updates via WebSocket

## Troubleshooting

**Visualization appears empty:**
- Check browser console for JSON loading errors
- Verify data files exist in correct paths
- Ensure capability_heights.json has valid data

**Poor performance/lag:**
- Reduce terrain segments (line 23 in TerrainMap.jsx)
- Disable shadows in App.jsx
- Hide unused layers via toggle controls
- Use a modern GPU

**Elements not interactive:**
- Ensure raycasting is working (check console)
- Verify onPointerOver/Out handlers are attached
- Check if camera controls are blocking events

**Colors look wrong:**
- Verify JSON data has correct RGB values
- Check THREE.Color conversion in components
- Ensure lighting is properly configured

## Contact & Support

For issues with the visualization:
1. Check console for errors
2. Verify data file integrity
3. Review component props and state
4. Open an issue on GitHub (if applicable)

---

**Remember**: This is an early warning system. The goal is not just to visualize current state, but to predict and prepare for future AI capability breakthroughs. Use it to stay ahead of rapid AI progress.
