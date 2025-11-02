import React, { useMemo, useState } from 'react';
import { Text } from '@react-three/drei';
import * as THREE from 'three';
import { useTerrainStore } from '../stores/terrainStore';
import forecastData from '../../../predictions/forecast_nodes.json';

function ForecastNodes() {
  const [hoveredNode, setHoveredNode] = useState(null);
  const { filterCategory } = useTerrainStore();

  // Transform forecast data into 3D nodes
  const nodes = useMemo(() => {
    return forecastData.nodes
      .filter((node) => {
        // Apply category filter
        if (filterCategory) {
          // Match capability name with category
          const capabilityLower = node.capability.toLowerCase();
          return capabilityLower.includes(filterCategory);
        }
        return true;
      })
      .map((node, idx) => {
      // Generate position based on capability and threshold
      // Spread nodes across the terrain
      const angle = (idx / forecastData.nodes.length) * Math.PI * 2;
      const radius = 30 + (node.threshold / 100) * 20;

      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const y = 10 + (node.threshold / 100) * 20; // Height based on threshold

      // Color based on node color from data
      const colorMap = {
        blue: '#4488ff',
        purple: '#aa44ff',
        red: '#ff4444',
        green: '#44ff88'
      };

      return {
        ...node,
        id: `forecast_${idx}`,
        position: [x, y, z],
        color: new THREE.Color(colorMap[node.color] || '#ffffff')
      };
    });
  }, [filterCategory]);

  return (
    <group>
      {nodes.map((node) => (
        <group key={node.id} position={node.position}>
          {/* Main forecast node sphere */}
          <mesh
            onPointerOver={() => setHoveredNode(node)}
            onPointerOut={() => setHoveredNode(null)}
          >
            <sphereGeometry args={[1.2, 32, 32]} />
            <meshStandardMaterial
              color={node.color}
              emissive={node.color}
              emissiveIntensity={hoveredNode?.id === node.id ? 1.0 : 0.5}
              transparent
              opacity={0.7}
              metalness={0.8}
              roughness={0.2}
            />
          </mesh>

          {/* Outer ring for translucent style */}
          {node.style === 'translucent' && (
            <mesh rotation={[Math.PI / 2, 0, 0]}>
              <ringGeometry args={[1.5, 2.0, 32]} />
              <meshBasicMaterial
                color={node.color}
                transparent
                opacity={0.3}
                side={THREE.DoubleSide}
              />
            </mesh>
          )}

          {/* Pulsing glow effect */}
          <pointLight
            color={node.color}
            intensity={hoveredNode?.id === node.id ? 3 : 1}
            distance={15}
          />

          {/* Tooltip on hover */}
          {hoveredNode?.id === node.id && (
            <group position={[0, 4, 0]}>
              <Text
                fontSize={1.2}
                color="white"
                anchorX="center"
                anchorY="middle"
                outlineWidth={0.15}
                outlineColor="#000000"
              >
                {node.capability.replace(/_/g, ' ').toUpperCase()}
              </Text>
              <Text
                position={[0, -2, 0]}
                fontSize={0.8}
                color="#ffff44"
                anchorX="center"
                anchorY="middle"
                outlineWidth={0.1}
                outlineColor="#000000"
              >
                {`Threshold: ${node.threshold}%`}
              </Text>
              <Text
                position={[0, -3.5, 0]}
                fontSize={0.7}
                color="#44ff88"
                anchorX="center"
                anchorY="middle"
                outlineWidth={0.1}
                outlineColor="#000000"
              >
                {`Predicted: ${node.predicted_date}`}
              </Text>
              <Text
                position={[0, -5, 0]}
                fontSize={0.6}
                color="#aaaaaa"
                anchorX="center"
                anchorY="middle"
                outlineWidth={0.1}
                outlineColor="#000000"
              >
                {node.days_until > 0
                  ? `${node.days_until} days until breakthrough`
                  : `${Math.abs(node.days_until)} days ago`}
              </Text>
            </group>
          )}

          {/* Warning indicator for imminent breakthroughs */}
          {node.days_until > 0 && node.days_until < 365 && (
            <mesh position={[0, 3, 0]}>
              <coneGeometry args={[0.5, 1, 4]} />
              <meshBasicMaterial color="#ffff00" />
            </mesh>
          )}
        </group>
      ))}
    </group>
  );
}

export default ForecastNodes;
