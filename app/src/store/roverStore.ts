import { create } from "zustand";
import type { RoverState, TerrainId, RoverTypeId } from "../types/rover";

const BRIDGE_URL = "ws://localhost:8765/ws";
const REST_URL = "http://localhost:8765";

export interface TrainingPoint {
  step: number;
  reward: number;
  episode: number;
}

interface RoverStore {
  connectionStatus: "disconnected" | "connecting" | "connected";
  roverState: RoverState | null;
  selectedTerrain: TerrainId;
  selectedRover: RoverTypeId;
  isSimulating: boolean;
  trainingHistory: TrainingPoint[];
  socket: WebSocket | null;

  connect: () => void;
  disconnect: () => void;
  setTerrain: (terrain: TerrainId) => void;
  setRover: (rover: RoverTypeId) => void;
  startTraining: () => void;
  stopTraining: () => void;
  resetSimulation: () => void;
}

export const useRoverStore = create<RoverStore>((set, get) => ({
  connectionStatus: "disconnected",
  roverState: null,
  selectedTerrain: "mars",
  selectedRover: "rocker_bogie",
  isSimulating: false,
  trainingHistory: [],
  socket: null,

  connect: () => {
    const existing = get().socket;
    if (existing) existing.close();

    set({ connectionStatus: "connecting" });

    const ws = new WebSocket(BRIDGE_URL);

    ws.onopen = () => {
      set({ connectionStatus: "connected", isSimulating: true });
    };

    ws.onmessage = (event) => {
      try {
        const state: RoverState = JSON.parse(event.data);
        set((s) => {
          const newHistory = [...s.trainingHistory];
          if (state.training.is_training && state.training.step > 0) {
            newHistory.push({
              step: state.training.step,
              reward: state.training.reward,
              episode: state.training.episode,
            });
            if (newHistory.length > 500) newHistory.splice(0, newHistory.length - 500);
          }
          return { roverState: state, trainingHistory: newHistory };
        });
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      set({ connectionStatus: "disconnected", isSimulating: false, socket: null });
    };

    ws.onerror = () => {
      set({ connectionStatus: "disconnected", isSimulating: false });
    };

    set({ socket: ws });
  },

  disconnect: () => {
    get().socket?.close();
    set({ connectionStatus: "disconnected", isSimulating: false, socket: null });
  },

  setTerrain: async (terrain: TerrainId) => {
    set({ selectedTerrain: terrain });
    const ws = get().socket;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "set_terrain", terrain }));
    }
  },

  setRover: async (rover: RoverTypeId) => {
    set({ selectedRover: rover });
    const ws = get().socket;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "set_rover", rover_type: rover }));
    }
  },

  startTraining: async () => {
    await fetch(`${REST_URL}/training/start`, { method: "POST" });
    const ws = get().socket;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "set_training", active: true }));
    }
    set({ trainingHistory: [] });
  },

  stopTraining: async () => {
    await fetch(`${REST_URL}/training/stop`, { method: "POST" });
    const ws = get().socket;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "set_training", active: false }));
    }
  },

  resetSimulation: async () => {
    await fetch(`${REST_URL}/simulation/reset`, { method: "POST" });
    const ws = get().socket;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "reset" }));
    }
    set({ trainingHistory: [] });
  },
}));
