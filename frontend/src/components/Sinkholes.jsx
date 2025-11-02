import React, { useMemo, useState } from 'react';
import { Text } from '@react-three/drei';
import * as THREE from 'three';
import sinkholeData from '../../../data/outputs/terrain_sinkholes.json';

function Sinkholes() {
  const [hoveredSinkhole, setHoveredSinkhole] = useState(null);

  // Transform sinkhole data into renderable meshes
  const sinkholes = useMemo(() => {
    const { vertices, metadata, colors } = sinkholeData;

    return vertices.map((vertex, idx) => {
      const [x, y, z] = vertex;
      const meta = metadata[idx];
      const color = colors[idx];

      // Convert normalized coordinates (0-1) to world space (-50 to 50)
      const worldX = (x - 0.5) * 100;
      const worldZ = (y - 0.5) * 100;
      const worldY = z * 0.15; // Scale depth for visibility

      return {
        id: `sinkhole_${idx}`,
        position: [worldX, worldY, worldZ],
        metadata: meta,
        color: new THREE.Color(color[0], color[1], color[2]),
        severity: meta.severity,
        category: meta.category
      };
    });
  }, []);

  return (
    <group>
      {sinkholes.map((sinkhole) => (
        <group key={sinkhole.id} position={sinkhole.position}>
          {/* Main sinkhole mesh - inverted cone/pit */}
          <mesh
            onPointerOver={() => setHoveredSinkhole(sinkhole)}
            onPointerOut={() => setHoveredSinkhole(null)}
            castShadow
          >
            <cylinderGeometry args={[0.8, 2, Math.abs(sinkhole.position[1]), 16]} />
            <meshStandardMaterial
              color={sinkhole.color}
              emissive={sinkhole.color}
              emissiveIntensity={hoveredSinkhole?.id === sinkhole.id ? 0.8 : 0.4}
              metalness={0.3}
              roughness={0.7}
              transparent
              opacity={0.9}
            />
          </mesh>

          {/* Rim/edge ring for better visibility */}
          <mesh position={[0, Math.abs(sinkhole.position[1]) / 2, 0]} rotation={[Math.PI / 2, 0, 0]}>
            <ringGeometry args={[1.8, 2.2, 32]} />
            <meshBasicMaterial
              color={sinkhole.color}
              transparent
              opacity={0.6}
              side={THREE.DoubleSide}
            />
          </mesh>

          {/* Glowing particles for critical sinkholes */}
          {sinkhole.severity === 'critical' && (
            <pointLight
              position={[0, 2, 0]}
              color={sinkhole.color}
              intensity={2}
              distance={10}
            />
          )}

          {/* Tooltip on hover */}
          {hoveredSinkhole?.id === sinkhole.id && (
            <group position={[0, 5, 0]}>
              <Text
                fontSize={1}
                color="white"
                anchorX="center"
                anchorY="middle"
                outlineWidth={0.15}
                outlineColor="#000000"
                maxWidth={20}
              >
                {`${sinkhole.metadata.category.replace('_', ' ').toUpperCase()}\n${sinkhole.metadata.severity}`}
              </Text>
              <Text
                position={[0, -2, 0]}
                fontSize={0.7}
                color="#cccccc"
                anchorX="center"
                anchorY="middle"
                outlineWidth={0.1}
                outlineColor="#000000"
                maxWidth={25}
              >
                {sinkhole.metadata.task.substring(0, 100)}...
              </Text>
              <Text
                position={[0, -4, 0]}
                fontSize={0.6}
                color={sinkhole.metadata.failure_count === sinkhole.metadata.total_tested ? '#ff4444' : '#44ff44'}
                anchorX="center"
                anchorY="middle"
                outlineWidth={0.1}
                outlineColor="#000000"
              >
                {`Failed: ${sinkhole.metadata.failure_count}/${sinkhole.metadata.total_tested} models`}
              </Text>
            </group>
          )}
        </group>
      ))}
    </group>
  );
}

export default Sinkholes;
