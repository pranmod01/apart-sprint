import React, { useRef, useMemo, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import * as THREE from 'three';
import ForecastNodes from './ForecastNodes';
import Sinkholes from './Sinkholes';
import { useTerrainStore } from '../stores/terrainStore';

function TerrainMap() {
  const meshRef = useRef();
  const {
    capabilityData,
    loadCapabilityData,
    showSinkholes,
    showForecastNodes,
    showLabels,
    filterCategory,
    currentYear
  } = useTerrainStore();
  const [hoveredCapability, setHoveredCapability] = useState(null);

  useEffect(() => {
    loadCapabilityData();
  }, [loadCapabilityData]);

  // Generate terrain geometry based on capability data
  const { geometry, capabilityPositions } = useMemo(() => {
    if (!capabilityData) return { geometry: null, capabilityPositions: [] };

    const size = 100;
    const segments = 100;
    const geo = new THREE.PlaneGeometry(size, size, segments, segments);

    const positions = geo.attributes.position;
    const capPositions = [];

    // Normalize capability data into a grid
    const heightMap = new Map();

    // Get all capabilities and their heights
    Object.entries(capabilityData).forEach(([key, cap]) => {
      // Apply category filter
      if (filterCategory && cap.category !== filterCategory) {
        return;
      }

      if (cap.x !== undefined && cap.y !== undefined) {
        const heights = cap.heights || {};

        // Use height for current year if available, otherwise use average
        const yearHeight = heights[currentYear.toString()];
        const avgHeight = yearHeight !== undefined
          ? yearHeight
          : (Object.values(heights).length > 0
            ? Object.values(heights).reduce((a, b) => a + b, 0) / Object.values(heights).length
            : 0.3);

        // Convert x,y (0-1) to grid coordinates
        const gridX = Math.floor(cap.x * segments);
        const gridY = Math.floor(cap.y * segments);
        const gridKey = `${gridX},${gridY}`;

        heightMap.set(gridKey, {
          height: avgHeight * 30, // Scale height for visibility
          capability: cap,
          key
        });

        capPositions.push({
          x: (cap.x - 0.5) * size,
          z: (cap.y - 0.5) * size,
          y: avgHeight * 30 + 2,
          name: cap.name || key,
          color: getCategoryColor(cap.category),
          category: cap.category
        });
      }
    });

    // Apply heights to geometry with smooth interpolation
    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i);
      const z = positions.getZ(i);

      // Convert to grid coordinates (0-1 range)
      const gridX = Math.floor(((x / size) + 0.5) * segments);
      const gridY = Math.floor(((z / size) + 0.5) * segments);

      // Look for nearby capability heights
      let height = 0;
      let totalWeight = 0;

      // Sample nearby grid points for smooth interpolation
      for (let dx = -3; dx <= 3; dx++) {
        for (let dy = -3; dy <= 3; dy++) {
          const key = `${gridX + dx},${gridY + dy}`;
          const data = heightMap.get(key);

          if (data) {
            const distance = Math.sqrt(dx * dx + dy * dy);
            const weight = Math.exp(-distance / 2); // Gaussian-like falloff
            height += data.height * weight;
            totalWeight += weight;
          }
        }
      }

      if (totalWeight > 0) {
        positions.setY(i, height / totalWeight);
      } else {
        // Base terrain height with some noise
        const noise = Math.sin(x * 0.1) * Math.cos(z * 0.1) * 2;
        positions.setY(i, noise);
      }
    }

    positions.needsUpdate = true;
    geo.computeVertexNormals();

    return { geometry: geo, capabilityPositions: capPositions };
  }, [capabilityData, filterCategory, currentYear]);

  // Animate terrain gently
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = -Math.PI / 2;
    }
  });

  if (!geometry) return null;

  return (
    <group>
      {/* Main Terrain Mesh */}
      <mesh
        ref={meshRef}
        geometry={geometry}
        rotation={[-Math.PI / 2, 0, 0]}
        receiveShadow
      >
        <meshStandardMaterial
          color="#1a1a2e"
          wireframe={false}
          metalness={0.3}
          roughness={0.7}
          side={THREE.DoubleSide}
          vertexColors={false}
        />
      </mesh>

      {/* Wireframe overlay for better depth perception */}
      <mesh
        geometry={geometry}
        rotation={[-Math.PI / 2, 0, 0]}
      >
        <meshBasicMaterial
          color="#4488ff"
          wireframe={true}
          transparent={true}
          opacity={0.1}
        />
      </mesh>

      {/* Capability Labels */}
      {showLabels && capabilityPositions.map((cap, idx) => (
        <group key={idx} position={[cap.x, cap.y, cap.z]}>
          <mesh
            onPointerOver={() => setHoveredCapability(cap.name)}
            onPointerOut={() => setHoveredCapability(null)}
          >
            <sphereGeometry args={[0.8, 16, 16]} />
            <meshStandardMaterial
              color={cap.color}
              emissive={cap.color}
              emissiveIntensity={hoveredCapability === cap.name ? 0.8 : 0.3}
              metalness={0.8}
              roughness={0.2}
            />
          </mesh>

          {hoveredCapability === cap.name && (
            <Text
              position={[0, 3, 0]}
              fontSize={1.5}
              color="white"
              anchorX="center"
              anchorY="middle"
              outlineWidth={0.1}
              outlineColor="#000000"
            >
              {cap.name}
            </Text>
          )}
        </group>
      ))}

      {/* Forecast Nodes */}
      {showForecastNodes && <ForecastNodes />}

      {/* Sinkholes */}
      {showSinkholes && <Sinkholes />}

      {/* Grid helper */}
      <gridHelper args={[100, 20, '#333333', '#222222']} position={[0, -0.1, 0]} />
    </group>
  );
}

// Helper function to get color based on category
function getCategoryColor(category) {
  const colors = {
    coding: '#00ff88',
    reasoning: '#ff6b6b',
    knowledge: '#4ecdc4',
    spatial: '#ffe66d',
    language: '#a8dadc',
    physical: '#ff9f1c',
    default: '#ffffff'
  };
  return colors[category] || colors.default;
}

export default TerrainMap;
