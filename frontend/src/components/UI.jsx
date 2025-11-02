import React from 'react';
import { useTerrainStore } from '../stores/terrainStore';
import './UI.css';

function UI() {
  const {
    showSinkholes,
    showForecastNodes,
    showLabels,
    filterCategory,
    filterModel,
    currentYear,
    availableYears,
    availableCategories,
    availableModels,
    toggleSinkholes,
    toggleForecastNodes,
    toggleLabels,
    setFilterCategory,
    setFilterModel,
    setCurrentYear
  } = useTerrainStore();

  return (
    <div className="ui-overlay">
      {/* Title */}
      <div className="ui-header">
        <h1>AI Capability Terrain Map</h1>
        <p className="subtitle">3D Early Warning System for AI Progress</p>
      </div>

      {/* Legend */}
      <div className="ui-legend">
        <h3>Legend</h3>
        <div className="legend-item">
          <div className="legend-icon" style={{ background: 'linear-gradient(45deg, #4488ff, #aa44ff)' }}></div>
          <span>Forecast Nodes - Predicted Breakthroughs</span>
        </div>
        <div className="legend-item">
          <div className="legend-icon sinkhole-icon" style={{ background: 'linear-gradient(135deg, #ff4444, #ff8844)' }}></div>
          <span>Sinkholes - Tasks AI Can't Handle</span>
        </div>
        <div className="legend-item">
          <div className="legend-icon" style={{ background: '#00ff88' }}></div>
          <span>Peaks - Mastered Capabilities</span>
        </div>
      </div>

      {/* Timeline Slider */}
      <div className="ui-timeline">
        <h3>Timeline: {currentYear}</h3>
        <input
          type="range"
          min={availableYears[0]}
          max={availableYears[availableYears.length - 1]}
          value={currentYear}
          onChange={(e) => setCurrentYear(parseInt(e.target.value))}
          className="timeline-slider"
        />
        <div className="timeline-labels">
          <span>{availableYears[0]}</span>
          <span>{availableYears[availableYears.length - 1]}</span>
        </div>
      </div>

      {/* Filters */}
      <div className="ui-filters">
        <h3>Filters</h3>

        <div className="filter-group">
          <label>Category:</label>
          <select
            value={filterCategory || 'all'}
            onChange={(e) => setFilterCategory(e.target.value === 'all' ? null : e.target.value)}
            className="filter-select"
          >
            <option value="all">All Categories</option>
            {availableCategories.map(cat => (
              <option key={cat} value={cat}>
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Model:</label>
          <select
            value={filterModel || 'All'}
            onChange={(e) => setFilterModel(e.target.value === 'All' ? null : e.target.value)}
            className="filter-select"
          >
            {availableModels.map(model => (
              <option key={model} value={model}>{model}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Display Controls */}
      <div className="ui-controls">
        <h3>Display Options</h3>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={showSinkholes}
            onChange={toggleSinkholes}
          />
          <span>Show Sinkholes</span>
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={showForecastNodes}
            onChange={toggleForecastNodes}
          />
          <span>Show Forecast Nodes</span>
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={showLabels}
            onChange={toggleLabels}
          />
          <span>Show Labels</span>
        </label>
      </div>

      {/* Stats */}
      <div className="ui-stats">
        <h3>System Status</h3>
        <div className="stat-item">
          <span className="stat-label">Active Sinkholes:</span>
          <span className="stat-value">43</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Forecast Nodes:</span>
          <span className="stat-value">74</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Capabilities Tracked:</span>
          <span className="stat-value">20+</span>
        </div>
      </div>

      {/* Instructions */}
      <div className="ui-instructions">
        <p><strong>Controls:</strong></p>
        <p>🖱️ Left Click + Drag: Rotate</p>
        <p>🖱️ Right Click + Drag: Pan</p>
        <p>🖱️ Scroll: Zoom</p>
        <p>🎯 Hover: Show Details</p>
      </div>
    </div>
  );
}

export default UI;
