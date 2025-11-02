# AI Capability Terrain Map - Frontend

Interactive 3D visualization of AI capabilities using React and Three.js.

## Features

- **3D Terrain Visualization**: Mountains = mastered capabilities, valleys = emerging skills
- **Sinkholes**: Red pits showing tasks AI inexplicably fails at
- **Forecast Nodes**: Glowing spheres predicting future capability breakthroughs
- **Interactive Camera**: Orbit, zoom, and pan to explore the terrain
- **Real-time Data**: Loads ML predictions from JSON files

## Tech Stack

- **React 18**: UI framework
- **Three.js**: 3D graphics
- **@react-three/fiber**: React renderer for Three.js
- **@react-three/drei**: Three.js helpers
- **Vite**: Build tool
- **Zustand**: State management

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the visualization.

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

## Data Sources

The visualization loads data from:

- `/data/intermediate/capability_heights.json` - AI capability performance data
- `/data/outputs/terrain_sinkholes.json` - Sinkhole locations and metadata
- `/predictions/forecast_nodes.json` - Future capability predictions

## Controls

- **Left Click + Drag**: Rotate camera
- **Right Click + Drag**: Pan camera
- **Scroll**: Zoom in/out
- **Hover**: Show details on capabilities, sinkholes, and forecast nodes

## Deployment

### Vercel (Recommended)

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `vercel`

### Manual Deployment

1. Build: `npm run build`
2. Upload `dist/` folder to your hosting provider
3. Ensure the data files are accessible at the correct paths

## Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── TerrainMap.jsx       # Main 3D terrain
│   │   ├── Sinkholes.jsx        # Sinkhole visualization
│   │   ├── ForecastNodes.jsx    # Forecast node spheres
│   │   ├── UI.jsx               # Overlay UI controls
│   │   └── UI.css               # UI styling
│   ├── stores/
│   │   └── terrainStore.js      # Global state management
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── index.html                   # HTML template
├── vite.config.js               # Vite configuration
└── package.json                 # Dependencies
```

## Customization

### Adjust Terrain Scale

Edit `TerrainMap.jsx`:

```javascript
const size = 100;  // Terrain size
const segments = 100;  // Mesh resolution
```

### Change Color Schemes

Edit category colors in `TerrainMap.jsx`:

```javascript
const colors = {
  coding: '#00ff88',
  reasoning: '#ff6b6b',
  // ...
};
```

## Troubleshooting

**Data not loading:**
- Ensure JSON files exist in `/data/` and `/predictions/` directories
- Check browser console for errors
- Verify file paths in components

**Performance issues:**
- Reduce `segments` in TerrainMap.jsx
- Disable shadows in App.jsx
- Lower the number of forecast nodes displayed

**Build errors:**
- Clear node_modules: `rm -rf node_modules package-lock.json`
- Reinstall: `npm install`
- Check Node.js version (requires v14+)

## License

MIT
