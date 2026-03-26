import { useRoverStore } from "../../store/roverStore";
import SensorPanel from "../sensors/SensorPanel";

function fmt(n: number | undefined, dec = 3) {
  return n !== undefined ? n.toFixed(dec) : "—";
}

function toDeg(rad: number) {
  return ((rad * 180) / Math.PI).toFixed(1);
}

export default function TelemetryPanel() {
  const roverState = useRoverStore((s) => s.roverState);
  const r = roverState?.rover;
  const env = roverState?.environment;

  const tiltWarning = r ? Math.abs(r.orientation.roll) > 0.3 || Math.abs(r.orientation.pitch) > 0.3 : false;

  return (
    <>
      <div className="panel-header">
        <span className="panel-title">Telemetry</span>
        {r && (
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text-3)" }}>
            {r.id}
          </span>
        )}
      </div>
      <div className="panel-body">
        <div className="section-label">Position (m)</div>
        <div className="data-row">
          <span className="data-label">X</span>
          <span className="data-value">{fmt(r?.position.x)}</span>
        </div>
        <div className="data-row">
          <span className="data-label">Y</span>
          <span className="data-value">{fmt(r?.position.y)}</span>
        </div>
        <div className="data-row">
          <span className="data-label">Z</span>
          <span className="data-value">{fmt(r?.position.z)}</span>
        </div>

        <div className="section-label">Orientation (°)</div>
        <div className="data-row">
          <span className="data-label">Roll</span>
          <span className={`data-value ${tiltWarning ? "warn" : "ok"}`}>
            {r ? toDeg(r.orientation.roll) : "—"}°
          </span>
        </div>
        <div className="data-row">
          <span className="data-label">Pitch</span>
          <span className={`data-value ${tiltWarning ? "warn" : "ok"}`}>
            {r ? toDeg(r.orientation.pitch) : "—"}°
          </span>
        </div>
        <div className="data-row">
          <span className="data-label">Yaw</span>
          <span className="data-value">
            {r ? toDeg(r.orientation.yaw) : "—"}°
          </span>
        </div>

        <div className="section-label">Velocity</div>
        <div className="data-row">
          <span className="data-label">Linear</span>
          <span className="data-value">{fmt(r?.velocity.linear, 4)} m/s</span>
        </div>
        <div className="data-row">
          <span className="data-label">Angular</span>
          <span className="data-value">{fmt(r?.velocity.angular, 5)} rad/s</span>
        </div>

        <div className="section-label">GPS</div>
        <div className="data-row">
          <span className="data-label">Lat</span>
          <span className="data-value">{fmt(roverState?.sensors.gps.latitude, 5)}°</span>
        </div>
        <div className="data-row">
          <span className="data-label">Lon</span>
          <span className="data-value">{fmt(roverState?.sensors.gps.longitude, 5)}°</span>
        </div>
        <div className="data-row">
          <span className="data-label">Alt</span>
          <span className="data-value">{fmt(roverState?.sensors.gps.altitude, 1)} m</span>
        </div>

        <SensorPanel />
      </div>
    </>
  );
}
