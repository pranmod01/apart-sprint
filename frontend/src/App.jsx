import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Stars } from '@react-three/drei';
import TerrainMap from './components/TerrainMap';
import UI from './components/UI';
import './App.css';

function App() {
  return (
    <div className="app">
      <Canvas shadows>
        <Suspense fallback={null}>
          {/* Camera Setup */}
          <PerspectiveCamera makeDefault position={[0, 50, 100]} fov={60} />

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

          {/* Camera Controls */}
          <OrbitControls
            enableDamping
            dampingFactor={0.05}
            minDistance={20}
            maxDistance={200}
            maxPolarAngle={Math.PI / 2.2}
          />
        </Suspense>
      </Canvas>

      {/* UI Overlay */}
      <UI />
    </div>
  );
}

export default App;
