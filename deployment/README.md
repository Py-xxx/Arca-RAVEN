# Deployment

Scripts for deploying trained RAVEN policies to real hardware.

## Target Hardware
NVIDIA Jetson AGX Orin — same CUDA ecosystem as training machine.

## Pipeline
1. Export policy to ONNX from training
2. Convert ONNX → TensorRT engine on Jetson
3. ROS2 Humble node subscribes to sensor topics, runs inference, publishes motor commands
