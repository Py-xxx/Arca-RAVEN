import { useRoverStore } from "../../store/roverStore";

export default function Header() {
  const status = useRoverStore((s) => s.connectionStatus);
  const isSimulating = useRoverStore((s) => s.isSimulating);
  const roverState = useRoverStore((s) => s.roverState);
  const connect = useRoverStore((s) => s.connect);
  const disconnect = useRoverStore((s) => s.disconnect);
  const resetSimulation = useRoverStore((s) => s.resetSimulation);
  const isTraining = roverState?.training.is_training ?? false;
  const startTraining = useRoverStore((s) => s.startTraining);
  const stopTraining = useRoverStore((s) => s.stopTraining);

  return (
    <header className="header">
      <div className="header-brand">
        <div className="header-logo">
          <span>ARCA</span> RAVEN
        </div>
        <div className="header-title">Mission Control — v0.1.0</div>
      </div>

      <div className="header-controls">
        {isSimulating && !isTraining && (
          <button className="btn btn-success" onClick={startTraining}>
            ▶ Train
          </button>
        )}
        {isTraining && (
          <button className="btn btn-danger" onClick={stopTraining}>
            ■ Stop Training
          </button>
        )}
        {isSimulating && (
          <button className="btn" onClick={resetSimulation}>
            ↺ Reset
          </button>
        )}
        {status === "disconnected" && (
          <button className="btn btn-accent" onClick={connect}>
            Connect
          </button>
        )}
        {status === "connected" && (
          <button className="btn btn-danger" onClick={disconnect}>
            Disconnect
          </button>
        )}
      </div>

      <div className="header-status">
        <div className={`status-dot ${status}`} />
        {status === "connected" && "CONNECTED"}
        {status === "connecting" && "CONNECTING..."}
        {status === "disconnected" && "DISCONNECTED"}
      </div>
    </header>
  );
}
