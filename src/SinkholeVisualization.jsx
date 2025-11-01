import { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import * as THREE from 'three';

// type PointsData = { x: number, y: number, z: number };

// Component to draw the spline
function Spline({ pointsData }) {
  // Convert your raw data points into THREE.Vector3 objects
  const curvePoints = useMemo(() =>
    pointsData.map(p => new THREE.Vector3(p.x, p.y, p.z)),
    [pointsData]
  );

  // Create a CatmullRomCurve3 (smooth, interpolating curve)
  const curve = useMemo(() => new THREE.CatmullRomCurve3(curvePoints), [curvePoints]);

  // Get a denser set of points for smoothness (e.g., 50 points)
  const numPoints = 50;
  const smoothPoints = useMemo(() => curve.getPoints(numPoints), [curve]);

  // Create the BufferGeometry from the points
  const geometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints(smoothPoints);
  }, [smoothPoints]);

  return (
    <line geometry={geometry}>
      <lineBasicMaterial color={0xff0000} attach="material" />
    </line>
  );
}

// Main Canvas component
export default function SinkholeVisualization() {
  // Example sinkhole data (replace with your actual data)
  const sinkholePoints = [
    { x: -10, y: 0, z: 0 },
    { x: -5, y: -5, z: -2 },
    { x: 0, y: -8, z: -5 },
    { x: 5, y: -5, z: -8 },
    { x: 10, y: 0, z: -10 }
  ];

  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <Spline pointsData={sinkholePoints} />
      {/* Optional: Render individual points to show original data */}
      {sinkholePoints.map((point, index) => (
        <mesh key={index} position={[point.x, point.y, point.z]}>
          <sphereGeometry args={[0.3, 16, 16]} />
          <meshBasicMaterial color={0x00ff00} />
        </mesh>
      ))}
      <axesHelper args={[20]} />
    </Canvas>
  );
}