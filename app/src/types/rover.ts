export interface Vec3 {
  x: number;
  y: number;
  z: number;
}

export interface Orientation {
  roll: number;
  pitch: number;
  yaw: number;
}

export interface IMUData {
  accelerometer: Vec3;
  gyroscope: Vec3;
}

export interface LidarData {
  ranges: number[];
  min_range: number;
  max_range: number;
  num_rays: number;
}

export interface GPSData {
  latitude: number;
  longitude: number;
  altitude: number;
}

export interface RoverData {
  id: string;
  type: string;
  position: Vec3;
  orientation: Orientation;
  velocity: { linear: number; angular: number };
  wheel_speeds: number[];
}

export interface TrainingData {
  episode: number;
  step: number;
  reward: number;
  cumulative_reward: number;
  is_training: boolean;
}

export interface EnvironmentData {
  terrain: string;
  gravity: number;
  description: string;
  simulation_time: number;
}

export interface RoverState {
  type: string;
  timestamp: number;
  rover: RoverData;
  sensors: {
    imu: IMUData;
    lidar: LidarData;
    gps: GPSData;
  };
  training: TrainingData;
  environment: EnvironmentData;
}

export type TerrainId = "mars" | "moon" | "asteroid" | "earth";
export type RoverTypeId = "rocker_bogie" | "skid_steer";

export const TERRAIN_LABELS: Record<TerrainId, string> = {
  mars: "Mars",
  moon: "Moon",
  asteroid: "Asteroid",
  earth: "Earth",
};

export const ROVER_LABELS: Record<RoverTypeId, string> = {
  rocker_bogie: "Rocker-Bogie (6-Wheel)",
  skid_steer: "Skid-Steer (4-Wheel)",
};
