import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Stars } from '@react-three/drei';
import TerrainMap from './components/TerrainMap';
import UI from './components/UI';
import { useTerrainStore } from './stores/terrainStore';
import './App.css';

function CameraController() {
  const { cameraMode } = useTerrainStore();

  // Camera positions for different modes
  const cameraPosition = cameraMode === 'landscape'
    ? [120, 20, 0]  // Side view - landscape
    : [0, 50, 100]; // Top-down view

  const orbitTarget = cameraMode === 'landscape'
    ? [0, 10, 0]  // Look slightly up in landscape
    : [0, 0, 0];  // Look at center in top-down

  return (
    <>
      <PerspectiveCamera makeDefault position={cameraPosition} fov={60} />
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        minDistance={20}
        maxDistance={200}
        maxPolarAngle={cameraMode === 'landscape' ? Math.PI / 1.5 : Math.PI / 2.2}
        target={orbitTarget}
      />
    </>
  );
}

function App() {
  return (
    <div className="app">
      <Canvas shadows>
        <Suspense fallback={null}>
          {/* Camera Setup */}
          <CameraController />

          {/* Lighting */}
          <ambientLight intensity={0.4} />
          <directionalLight
            position={[50, 50, 25]}
            intensity={1}
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
          />
          <pointLight position={[-50, 50, -25]} intensity={0.5} color="#4488ff" />

          {/* Background */}
          <Stars
            radius={300}
            depth={50}
            count={5000}
            factor={4}
            saturation={0}
            fade
            speed={1}
          />

          {/* Main Terrain Component */}
          <TerrainMap />
        </Suspense>
      </Canvas>

      {/* UI Overlay */}
      <UI />
    </div>
  );
}

export default App;
