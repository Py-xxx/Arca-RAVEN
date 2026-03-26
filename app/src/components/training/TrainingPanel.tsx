import { useRoverStore } from "../../store/roverStore";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

export default function TrainingPanel() {
  const roverState = useRoverStore((s) => s.roverState);
  const history = useRoverStore((s) => s.trainingHistory);
  const startTraining = useRoverStore((s) => s.startTraining);
  const stopTraining = useRoverStore((s) => s.stopTraining);
  const training = roverState?.training;

  // Downsample history for chart performance
  const chartData = history.filter((_, i) => i % Math.max(1, Math.floor(history.length / 200)) === 0);

  return (
    <>
      <div className="panel-header">
        <span className="panel-title">Training Dashboard</span>
        <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
          {training && (
            <>
              <StatBadge label="Episode" value={training.episode} />
              <StatBadge label="Step" value={training.step.toLocaleString()} />
              <StatBadge
                label="Reward"
                value={training.reward.toFixed(4)}
                color={training.reward > 0.5 ? "var(--success)" : training.reward > 0.2 ? "var(--warning)" : "var(--danger)"}
              />
              <StatBadge label="Cumulative" value={training.cumulative_reward.toFixed(3)} />
            </>
          )}
          {training?.is_training ? (
            <button className="btn btn-danger" onClick={stopTraining}>■ Stop</button>
          ) : (
            <button className="btn btn-success" onClick={startTraining}>▶ Start Training</button>
          )}
        </div>
      </div>

      <div style={{ flex: 1, padding: "8px 14px" }}>
        {chartData.length > 2 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1c1f2b" />
              <XAxis
                dataKey="step"
                tick={{ fill: "#3d4455", fontSize: 9, fontFamily: "var(--font-mono)" }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                tick={{ fill: "#3d4455", fontSize: 9, fontFamily: "var(--font-mono)" }}
                tickLine={false}
                axisLine={false}
                domain={["auto", "auto"]}
              />
              <Tooltip
                contentStyle={{
                  background: "var(--bg-panel-alt)",
                  border: "1px solid var(--border-bright)",
                  borderRadius: 6,
                  fontFamily: "var(--font-mono)",
                  fontSize: 10,
                  color: "var(--text-1)",
                }}
                labelStyle={{ color: "var(--text-2)" }}
              />
              <Line
                type="monotone"
                dataKey="reward"
                stroke="#00c8f8"
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div style={{
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: "var(--font-mono)",
            fontSize: 11,
            color: "var(--text-3)",
          }}>
            {training?.is_training ? "Collecting data..." : "Press Start Training to begin"}
          </div>
        )}
      </div>
    </>
  );
}

function StatBadge({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 1 }}>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text-3)", letterSpacing: "0.1em" }}>
        {label.toUpperCase()}
      </span>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: color ?? "var(--accent)" }}>
        {value}
      </span>
    </div>
  );
}
