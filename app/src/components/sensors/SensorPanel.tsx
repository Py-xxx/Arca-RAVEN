import { useRoverStore } from "../../store/roverStore";
import LidarViz from "./LidarViz";

function fmt(n: number | undefined, dec = 4) {
  return n !== undefined ? n.toFixed(dec) : "—";
}

export default function SensorPanel() {
  const roverState = useRoverStore((s) => s.roverState);
  const imu = roverState?.sensors.imu;

  return (
    <>
      <div className="section-label">IMU — Accelerometer (m/s²)</div>
      <div className="data-row">
        <span className="data-label">Ax</span>
        <span className="data-value">{fmt(imu?.accelerometer.x)}</span>
      </div>
      <div className="data-row">
        <span className="data-label">Ay</span>
        <span className="data-value">{fmt(imu?.accelerometer.y)}</span>
      </div>
      <div className="data-row">
        <span className="data-label">Az</span>
        <span className="data-value">{fmt(imu?.accelerometer.z)}</span>
      </div>

      <div className="section-label">IMU — Gyroscope (rad/s)</div>
      <div className="data-row">
        <span className="data-label">Gx</span>
        <span className="data-value">{fmt(imu?.gyroscope.x, 6)}</span>
      </div>
      <div className="data-row">
        <span className="data-label">Gy</span>
        <span className="data-value">{fmt(imu?.gyroscope.y, 6)}</span>
      </div>
      <div className="data-row">
        <span className="data-label">Gz</span>
        <span className="data-value">{fmt(imu?.gyroscope.z, 6)}</span>
      </div>

      <div className="section-label">LiDAR — Top-Down</div>
      <LidarViz />
    </>
  );
}
