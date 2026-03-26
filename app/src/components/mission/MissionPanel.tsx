import { useRoverStore } from "../../store/roverStore";
import { TERRAIN_LABELS, ROVER_LABELS, type TerrainId, type RoverTypeId } from "../../types/rover";

const TERRAINS: TerrainId[] = ["mars", "moon", "asteroid", "earth"];
const ROVERS: RoverTypeId[] = ["rocker_bogie", "skid_steer"];

export default function MissionPanel() {
  const selectedTerrain = useRoverStore((s) => s.selectedTerrain);
  const selectedRover = useRoverStore((s) => s.selectedRover);
  const setTerrain = useRoverStore((s) => s.setTerrain);
  const setRover = useRoverStore((s) => s.setRover);
  const roverState = useRoverStore((s) => s.roverState);

  return (
    <>
      <div className="panel-header">
        <span className="panel-title">Mission Control</span>
      </div>
      <div className="panel-body">
        <div className="section-label">Rover</div>
        <div className="radio-group">
          {ROVERS.map((r) => (
            <div
              key={r}
              className={`radio-item ${selectedRover === r ? "selected" : ""}`}
              onClick={() => setRover(r)}
            >
              <div className="radio-dot">
                {selectedRover === r && <div className="radio-dot-inner" />}
              </div>
              <span className="radio-text">{ROVER_LABELS[r]}</span>
            </div>
          ))}
        </div>

        <div className="section-label">Terrain</div>
        <div className="radio-group">
          {TERRAINS.map((t) => (
            <div
              key={t}
              className={`radio-item ${selectedTerrain === t ? "selected" : ""}`}
              onClick={() => setTerrain(t)}
            >
              <div className="radio-dot">
                {selectedTerrain === t && <div className="radio-dot-inner" />}
              </div>
              <span className="radio-text">{TERRAIN_LABELS[t]}</span>
            </div>
          ))}
        </div>

        {roverState && (
          <>
            <div className="section-label">Environment</div>
            <div className="data-row">
              <span className="data-label">Location</span>
              <span className="data-value" style={{ fontSize: 9 }}>
                {roverState.environment.description}
              </span>
            </div>
            <div className="data-row">
              <span className="data-label">Gravity</span>
              <span className="data-value">
                {roverState.environment.gravity.toFixed(2)} m/s²
              </span>
            </div>
            <div className="data-row">
              <span className="data-label">Sim Time</span>
              <span className="data-value">
                {roverState.environment.simulation_time.toFixed(1)} s
              </span>
            </div>
          </>
        )}
      </div>
    </>
  );
}
