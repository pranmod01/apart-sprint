// import { useState } from 'react'
import Visualizer from './components/Visualizer'
// import TerrainScene from './components/TerrainScene'
// import { Canvas } from '@react-three/fiber'
// import Cube from './components/Cube'


function App() {
  // const [count, setCount] = useState(0)

  return (
    <>
      <Visualizer />

      {/* <Canvas>
        <ambientLight intensity={Math.PI / 2} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} decay={0} intensity={Math.PI} />
        <pointLight position={[-10, -10, -10]} decay={0} intensity={Math.PI} />
        <Cube position={[-1.2, 0, 0]} />
        <Cube position={[1.2, 0, 0]} />
      </Canvas> */}
      {/* <section className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
      </section> */}
    </>
  )
}

export default App
