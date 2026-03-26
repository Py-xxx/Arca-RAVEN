import { useAutoConnect } from "./hooks/useWebSocket";
import Header from "./components/layout/Header";
import MissionPanel from "./components/mission/MissionPanel";
import ViewportPanel from "./components/viewport/ViewportPanel";
import TelemetryPanel from "./components/telemetry/TelemetryPanel";
import TrainingPanel from "./components/training/TrainingPanel";

export default function App() {
  useAutoConnect();

  return (
    <div className="app">
      <Header />
      <div className="main-layout">
        <div className="panel mission-col">
          <MissionPanel />
        </div>
        <div className="panel viewport-col">
          <ViewportPanel />
        </div>
        <div className="panel telemetry-col">
          <TelemetryPanel />
        </div>
        <div className="panel training-row">
          <TrainingPanel />
        </div>
      </div>
    </div>
  );
}
