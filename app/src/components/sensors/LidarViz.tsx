import { useEffect, useRef } from "react";
import { useRoverStore } from "../../store/roverStore";

const SIZE = 180;
const CENTER = SIZE / 2;
const MAX_RANGE = 50;
const SCALE = (SIZE / 2 - 8) / MAX_RANGE;

export default function LidarViz() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const roverState = useRoverStore((s) => s.roverState);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const ranges = roverState?.sensors.lidar.ranges ?? [];

    ctx.clearRect(0, 0, SIZE, SIZE);

    // Background
    ctx.fillStyle = "#050608";
    ctx.beginPath();
    ctx.arc(CENTER, CENTER, CENTER - 2, 0, Math.PI * 2);
    ctx.fill();

    // Range rings
    [10, 20, 30, 40, 50].forEach((r) => {
      ctx.beginPath();
      ctx.arc(CENTER, CENTER, r * SCALE, 0, Math.PI * 2);
      ctx.strokeStyle = "#1c1f2b";
      ctx.lineWidth = 0.5;
      ctx.stroke();
    });

    // Cross hairs
    ctx.strokeStyle = "#1c1f2b";
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(CENTER, 4); ctx.lineTo(CENTER, SIZE - 4);
    ctx.moveTo(4, CENTER); ctx.lineTo(SIZE - 4, CENTER);
    ctx.stroke();

    if (ranges.length === 0) return;

    // LiDAR sweep fill
    ctx.beginPath();
    ranges.forEach((r, i) => {
      const angle = (i / ranges.length) * Math.PI * 2 - Math.PI / 2;
      const d = Math.min(r, MAX_RANGE) * SCALE;
      const x = CENTER + Math.cos(angle) * d;
      const y = CENTER + Math.sin(angle) * d;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = "rgba(0, 200, 248, 0.08)";
    ctx.fill();
    ctx.strokeStyle = "rgba(0, 200, 248, 0.5)";
    ctx.lineWidth = 0.8;
    ctx.stroke();

    // Rover dot
    ctx.beginPath();
    ctx.arc(CENTER, CENTER, 3, 0, Math.PI * 2);
    ctx.fillStyle = "#00e89a";
    ctx.fill();
  }, [roverState?.sensors.lidar.ranges]);

  return (
    <canvas
      ref={canvasRef}
      width={SIZE}
      height={SIZE}
      className="lidar-canvas"
      style={{ borderRadius: "50%", border: "1px solid var(--border)" }}
    />
  );
}
