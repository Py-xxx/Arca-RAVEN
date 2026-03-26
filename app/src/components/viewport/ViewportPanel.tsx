import { useEffect, useRef } from "react";
import * as THREE from "three";
import { useRoverStore } from "../../store/roverStore";

export default function ViewportPanel() {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<{
    renderer: THREE.WebGLRenderer;
    scene: THREE.Scene;
    camera: THREE.PerspectiveCamera;
    rover: THREE.Mesh;
    animId: number;
  } | null>(null);

  const roverState = useRoverStore((s) => s.roverState);
  const connectionStatus = useRoverStore((s) => s.connectionStatus);

  // Initialize Three.js scene once
  useEffect(() => {
    if (!mountRef.current) return;

    const el = mountRef.current;
    const w = el.clientWidth;
    const h = el.clientHeight;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(w, h);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.setClearColor(0x050608);
    el.appendChild(renderer.domElement);

    // Scene
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050608, 0.025);

    // Camera
    const camera = new THREE.PerspectiveCamera(55, w / h, 0.1, 500);
    camera.position.set(0, 20, 22);
    camera.lookAt(0, 0, 0);

    // Lights
    const ambient = new THREE.AmbientLight(0x1a2030, 1.2);
    scene.add(ambient);
    const sun = new THREE.DirectionalLight(0xfff4e0, 2.0);
    sun.position.set(30, 60, 20);
    sun.castShadow = true;
    scene.add(sun);

    // Grid (terrain placeholder)
    const gridHelper = new THREE.GridHelper(80, 40, 0x1c1f2b, 0x1c1f2b);
    scene.add(gridHelper);

    // Ground plane
    const groundGeo = new THREE.PlaneGeometry(80, 80);
    const groundMat = new THREE.MeshLambertMaterial({ color: 0x0a0b10 });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Rover mesh (placeholder box — replaced by USD model in Phase 2)
    const roverGroup = new THREE.Group();

    const bodyGeo = new THREE.BoxGeometry(1.2, 0.4, 0.8);
    const bodyMat = new THREE.MeshLambertMaterial({ color: 0xc8a870 });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 0.35;
    body.castShadow = true;
    roverGroup.add(body);

    // Wheels
    const wheelGeo = new THREE.CylinderGeometry(0.18, 0.18, 0.12, 12);
    const wheelMat = new THREE.MeshLambertMaterial({ color: 0x2a2a2a });
    const wheelPositions = [
      [-0.55, 0.18, 0.42], [0.55, 0.18, 0.42],
      [-0.55, 0.18, 0],    [0.55, 0.18, 0],
      [-0.55, 0.18, -0.42],[0.55, 0.18, -0.42],
    ];
    wheelPositions.forEach(([x, y, z]) => {
      const wheel = new THREE.Mesh(wheelGeo, wheelMat);
      wheel.position.set(x, y, z);
      wheel.rotation.z = Math.PI / 2;
      roverGroup.add(wheel);
    });

    // Mast (camera/sensor tower)
    const mastGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.6, 8);
    const mastMat = new THREE.MeshLambertMaterial({ color: 0x888888 });
    const mast = new THREE.Mesh(mastGeo, mastMat);
    mast.position.set(0.1, 0.85, 0);
    roverGroup.add(mast);

    scene.add(roverGroup);

    // Orbit-style camera rotation (auto)
    let camAngle = 0;
    let camRadius = 28;

    const animate = () => {
      const id = requestAnimationFrame(animate);
      sceneRef.current!.animId = id;

      camAngle += 0.003;
      camera.position.x = Math.sin(camAngle) * camRadius;
      camera.position.z = Math.cos(camAngle) * camRadius;
      camera.position.y = 18;
      camera.lookAt(roverGroup.position);

      renderer.render(scene, camera);
    };

    const animId = requestAnimationFrame(animate);

    sceneRef.current = { renderer, scene, camera, rover: roverGroup as unknown as THREE.Mesh, animId };

    // Resize handler
    const onResize = () => {
      const w2 = el.clientWidth;
      const h2 = el.clientHeight;
      camera.aspect = w2 / h2;
      camera.updateProjectionMatrix();
      renderer.setSize(w2, h2);
    };
    const ro = new ResizeObserver(onResize);
    ro.observe(el);

    return () => {
      cancelAnimationFrame(animId);
      ro.disconnect();
      renderer.dispose();
      el.removeChild(renderer.domElement);
      sceneRef.current = null;
    };
  }, []);

  // Update rover position from WebSocket state
  useEffect(() => {
    if (!roverState || !sceneRef.current) return;
    const { rover: roverMesh } = sceneRef.current;
    const pos = roverState.rover.position;
    const ori = roverState.rover.orientation;
    (roverMesh as unknown as THREE.Group).position.set(pos.x, pos.z, -pos.y);
    (roverMesh as unknown as THREE.Group).rotation.set(ori.pitch, -ori.yaw, ori.roll);
  }, [roverState]);

  const terrain = roverState?.environment.terrain ?? "—";
  const simTime = roverState?.environment.simulation_time.toFixed(1) ?? "—";

  return (
    <div className="viewport-container" ref={mountRef}>
      <div className="viewport-overlay">
        <div className="viewport-badge">
          TERRAIN: <span>{terrain.toUpperCase()}</span>
        </div>
        <div className="viewport-badge">
          SIM: <span>{simTime}s</span>
        </div>
        <div className="viewport-badge">
          STATUS: <span style={{ color: connectionStatus === "connected" ? "var(--success)" : "var(--danger)" }}>
            {connectionStatus.toUpperCase()}
          </span>
        </div>
      </div>
    </div>
  );
}
