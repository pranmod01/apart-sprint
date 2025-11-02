import { Html, Line } from "@react-three/drei";
import { useEffect, useMemo, useRef, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, TransformControls } from "@react-three/drei";
import * as THREE from "three";
import { GUI } from "dat.gui";
import categories from "../../config/categories.json";
import capabilityHeights from "../../data/intermediate/capability_heights.json";

const ARC_SEGMENTS = 200;
const YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025];

function useCurveLine(points, curveType, color) {
  return useMemo(() => {
    if (!points || points.length < 2) return null;
    const curve = new THREE.CatmullRomCurve3(points);
    curve.curveType = curveType;
    const pts = curve.getPoints(ARC_SEGMENTS);
    const geom = new THREE.BufferGeometry().setFromPoints(pts);
    return { geom, color };
  }, [points, curveType, color]);
}

function SplineLines({ points, show }) {
  const pts = useMemo(() => points.map((p) => new THREE.Vector3(p.x, p.y, p.z)), [points]);
  const uniform = useCurveLine(pts, "catmullrom", 0xff0000);
  const centripetal = useCurveLine(pts, "centripetal", 0x00ff00);
  const chordal = useCurveLine(pts, "chordal", 0x0000ff);

  return (
    <>
      {show.uniform && uniform && (
        <line geometry={uniform.geom}>
          <lineBasicMaterial attach="material" color={uniform.color} transparent opacity={0.6} />
        </line>
      )}
      {show.centripetal && centripetal && (
        <line geometry={centripetal.geom}>
          <lineBasicMaterial attach="material" color={centripetal.color} transparent opacity={0.6} />
        </line>
      )}
      {show.chordal && chordal && (
        <line geometry={chordal.geom}>
          <lineBasicMaterial attach="material" color={chordal.color} transparent opacity={0.6} />
        </line>
      )}
    </>
  );
}

function Scene() {
  const initial = [
    new THREE.Vector3(289.7684, 452.5148, 56.10019),
    new THREE.Vector3(-53.563, 171.4971, -14.49547),
    new THREE.Vector3(-91.40119, 176.4307, -6.95827),
    new THREE.Vector3(-383.7853, 491.1365, 47.8693),
  ].map((v) => ({ x: v.x * 0.8, y: v.y * 0.6 - 200, z: v.z * 0.6 })); // scaled down for canvas

  const [points, setPoints] = useState(initial);
  const meshRefs = useRef({});
  const [selected, setSelected] = useState(null);
  const transformRef = useRef();
  const guiRef = useRef();
  const [show, setShow] = useState({ uniform: true, centripetal: false, chordal: false });

  // capability toggle state (initialized from config)
  const [capabilitiesState, setCapabilitiesState] = useState(() => {
    const map = {};
    if (categories?.capability_categories) {
      Object.keys(categories.capability_categories).forEach((k) => (map[k] = true)); // default ON
    }
    return map;
  });
  const capabilitiesGuiRef = useRef({});
  useEffect(() => {
    capabilitiesGuiRef.current = { ...capabilitiesState };
  }, []); // sync once on mount

  // selected year for narrowing down
  const [year, setYear] = useState(2025);
  const [animateYears, setAnimateYears] = useState(false);
  const animRef = useRef<number | null>(null);

  // keep meshes updated into state when transform is used
  useEffect(() => {
    const onChange = () => {
      if (selected == null) return;
      const m = meshRefs.current[selected];
      if (!m) return;
      setPoints((prev) => {
        const copy = prev.slice();
        copy[selected] = { x: m.position.x, y: m.position.y, z: m.position.z };
        return copy;
      });
    };
    const ctrl = transformRef.current;
    if (ctrl) ctrl.addEventListener?.("objectChange", onChange);
    return () => ctrl?.removeEventListener?.("objectChange", onChange);
  }, [selected]);

  // GUI
  useEffect(() => {
    const gui = new GUI({ width: 300 });
    guiRef.current = gui;

    // AI Capabilities folder - dynamically generated from config
    if (categories?.capability_categories && Object.keys(categories.capability_categories).length) {
      const { capability_categories } = categories;
      const capabilitiesFolder = gui.addFolder("AI Capabilities");

      // prepare GUI object
      capabilitiesGuiRef.current = { ...capabilitiesGuiRef.current };
      Object.keys(capability_categories).forEach((key) => {
        if (!(key in capabilitiesGuiRef.current)) capabilitiesGuiRef.current[key] = true;
      });

      for (const [key, cap] of Object.entries(capability_categories)) {
        const ctrl = capabilitiesFolder.add(capabilitiesGuiRef.current, key).name(cap.display_name || key);
        ctrl.onChange((value) => setCapabilitiesState((prev) => ({ ...prev, [key]: value })));
      }
      capabilitiesFolder.open();
    }


    const yearFolder = gui.addFolder("Year / Playback");
    yearFolder.add({ year }, "year", 2019, 2025, 1).name("Selected Year").onChange((v) => setYear(Math.round(v)));
    yearFolder.add({ animateYears }, "animateYears").name("Animate Years").onChange((v) => setAnimateYears(Boolean(v)));
    yearFolder.open();

    return () => {
      gui.destroy();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [points]);

  // animation loop for year playback
  useEffect(() => {
    if (!animateYears) {
      if (animRef.current) {
        window.clearInterval(animRef.current);
        animRef.current = null;
      }
      return;
    }
    animRef.current = window.setInterval(() => {
      setYear((y) => {
        const next = y >= 2025 ? 2019 : y + 1;
        // also update GUI controller value if present
        // (dat.GUI mutates objects we passed, but we re-create setYear so just set state)
        return next;
      });
    }, 800);
    return () => {
      if (animRef.current) {
        window.clearInterval(animRef.current);
        animRef.current = null;
      }
    };
  }, [animateYears]);

  // click outside to deselect
  const { gl } = useThree();
  useEffect(() => {
    const handler = (e) => {
      if (e.target === gl.domElement) setSelected(null);
    };
    window.addEventListener("pointerdown", handler);
    return () => window.removeEventListener("pointerdown", handler);
  }, [gl]);

  // animate a very slow rotation on the group to hint scene (optional)
  const groupRef = useRef();
  useFrame((state, delta) => {
    if (groupRef.current) groupRef.current.rotation.y += delta * 0.02;
  });

  // helper: convert normalized x/y to world coords
  const worldFromNorm = (nx, ny, scale = 1600) => [(nx - 0.5) * scale, (ny - 0.5) * scale];

  // helper: build trend line geometry for a capability (years -> height)
  const buildTrend = (cap) => {
    const pts = YEARS.map((y, i) => {
      const h = Number((cap.heights && cap.heights[String(y)]) ?? 0);
      const [wx, wz] = worldFromNorm(cap.x, cap.y, 1200);
      // small horizontal offset per year to visualize trend near marker
      const offsetX = (i - (YEARS.length - 1) / 2) * 12;
      return new THREE.Vector3(wx + offsetX, -200 + h * 600, wz + 6); // slight z offset to avoid z-fighting
    });
    return new THREE.BufferGeometry().setFromPoints(pts);
  };

  // helper: sinkhole ring for low values (smaller height => deeper sinkhole)
  const buildSinkholeRing = (cap, heightVal) => {
    const [wx, wz] = worldFromNorm(cap.x, cap.y, 1200);
    const center = new THREE.Vector3(wx, -200 + heightVal * 600, wz);
    const radius = Math.max(6, (0.12 - Math.min(0.12, Number(heightVal) || 0)) * 350); // deeper => larger ring radius
    const segments = 40;
    const pts = [];
    for (let i = 0; i <= segments; i++) {
      const a = (i / segments) * Math.PI * 2;
      pts.push(new THREE.Vector3(center.x + Math.cos(a) * radius, center.y - Math.abs(Math.sin(a)) * Math.max(6, (0.12 - heightVal) * 120), center.z + Math.sin(a) * radius));
    }
    const curve = new THREE.CatmullRomCurve3(pts, true);
    const geom = new THREE.BufferGeometry().setFromPoints(curve.getPoints(100));
    return geom;
  };

  // helper: find related capabilities by checking top_models overlap
  const findRelatedCapabilities = (capKey, cap) => {
    const related = [];
    if (!cap.top_models) return related;
    
    Object.entries(capabilityHeights.all).forEach(([otherKey, other]) => {
      if (otherKey === capKey) return;
      if (!other.top_models) return;
      
      // check for overlapping top models
      const overlap = Object.keys(cap.top_models).filter(
        model => other.top_models[model]
      );
      if (overlap.length > 0) {
        related.push({
          key: otherKey,
          overlap: overlap.length,
          pos: other
        });
      }
    });
    return related;
  };

  // build capability nodes with labels and connections
  const capabilityNodes = useMemo(() => {
    if (!capabilityHeights?.all) return [];
    
    const nodes = Object.entries(capabilityHeights.all).map(([capKey, cap]) => {
      const category = cap.category || "unknown";
      if (capabilitiesState && category && capabilitiesState[category] === false) return null;

      const heights = cap.heights || {};
      const selectedHeight = Number(heights[String(year)] ?? 0);
      
      // Get world position for this capability
      const [wx, wz] = worldFromNorm(cap.x, cap.y, 1200);
      const yearIndex = YEARS.indexOf(year);
      const offsetX = (yearIndex - (YEARS.length - 1) / 2) * 12;
      const markerPos = [wx + offsetX, -200 + selectedHeight * 600, wz + 6];

      // Find related capabilities to draw connections
      const related = findRelatedCapabilities(capKey, cap);
      
      // Color from category config
      let col = new THREE.Color(0x888888);
      const catCfg = categories?.capability_categories?.[category];
      if (catCfg?.color && Array.isArray(catCfg.color)) {
        const [r, g, b] = catCfg.color;
        col = new THREE.Color().setRGB(r, g, b);
      }

      return (
        <group key={capKey}>
          {/* Marker & trend lines as before */}
          <line geometry={buildTrend(cap)}>
            <lineBasicMaterial attach="material" color={col.getHex()} linewidth={2} transparent opacity={0.9} />
          </line>

          <mesh position={markerPos}>
            <sphereGeometry args={[5.5, 10, 10]} />
            <meshStandardMaterial 
              color={selectedHeight < 0.12 ? 0xff3333 : col} 
              emissive={selectedHeight < 0.12 ? new THREE.Color(0x6b0000) : col} 
              emissiveIntensity={0.4} 
            />
          </mesh>

          {/* Label */}
          <Html
            position={[markerPos[0], markerPos[1] + 20, markerPos[2]]}
            center
            style={{
              background: 'rgba(0,0,0,0.8)',
              padding: '4px 8px',
              borderRadius: '4px',
              color: 'white',
              fontSize: '12px',
              pointerEvents: 'none',
              whiteSpace: 'nowrap'
            }}
          >
            {capKey.split('_').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')}
          </Html>

          {/* Connection lines to related capabilities */}
          {related.map(rel => (
            <Line
              key={`${capKey}-${rel.key}`}
              points={[
                new THREE.Vector3(markerPos[0], markerPos[1], markerPos[2]),
                new THREE.Vector3(
                  rel.pos.x * 1200 - 600,
                  -200 + (rel.pos.heights?.[year] ?? 0) * 600,
                  rel.pos.y * 1200 - 600
                )
              ]}
              color={col.getHex()}
              lineWidth={1}
              transparent
              opacity={0.3}
            />
          ))}

          {/* Sinkhole if needed */}
          {selectedHeight > 0 && selectedHeight < 0.12 && (
            <line geometry={buildSinkholeRing(cap, selectedHeight)}>
              <lineBasicMaterial attach="material" color={0xff2222} linewidth={2} transparent opacity={0.85} />
            </line>
          )}
        </group>
      );
    });

    return nodes;
  }, [capabilityHeights, capabilitiesState, year, categories]);

  return (
    <group ref={groupRef}>
      <ambientLight intensity={0.9} />
      <directionalLight position={[400, 800, 200]} intensity={1.2} />
      <gridHelper args={[2000, 100, 0x444444, 0x222222]} position={[0, -300, 0]} />

      {/* Points */}
      {points.map((pt, i) => (
        <mesh key={i} ref={(el) => (meshRefs.current[i] = el)} position={[pt.x, pt.y, pt.z]} onPointerDown={(e) => { e.stopPropagation(); setSelected(i); }} castShadow>
          <sphereGeometry args={[10, 16, 12]} />
          <meshStandardMaterial color={selected === i ? 0xffff00 : 0x156289} />
        </mesh>
      ))}

      {/* Capability trend lines + sinkhole visualization */}
      {capabilityNodes}

      {/* TransformControls attached to selected mesh */}
      <TransformControls ref={transformRef} object={selected != null ? meshRefs.current[selected] : undefined} mode="translate" />
      <SplineLines points={points} show={show} />
    </group>
  );
}

export default function Visualizer() {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "90vh", width: "100%" }}>
      <header style={{ padding: 12, background: "#fafafa", borderBottom: "1px solid #eee" }}>
        <h2 style={{ margin: 0 }}>AI Capabilities Visualizer</h2>
      </header>

      <div style={{ flex: 1 }}>
        <Canvas
          shadows
          gl={{ antialias: true }}
          camera={{ position: [0, 400, 800], fov: 45, near: 0.1, far: 5000 }}
          style={{ width: "100%", height: "100%" }}
        >
          <color attach="background" args={["#f0f0f0"]} />
          <Scene />
          <OrbitControls
            makeDefault
            enableDamping
            dampingFactor={0.06}
            minDistance={20}
            maxDistance={3500}
            maxPolarAngle={Math.PI * 0.495}
          />
        </Canvas>
      </div>
    </div>
  );
}