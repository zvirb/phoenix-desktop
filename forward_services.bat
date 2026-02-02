@echo off
echo Starting Port Forwarding for Phoenix Services...
start "Phoenix Task Intelligence" kubectl port-forward svc/phoenix-task-intelligence 8001:8000
start "Phoenix Media Processor" kubectl port-forward svc/phoenix-media-processor 8002:8000
start "Phoenix Adaptive Intervention" kubectl port-forward svc/phoenix-adaptive-intervention 8003:8000
echo Services exposed:
echo - Task Intelligence: localhost:8001
echo - Media Processor: localhost:8002
echo - Adaptive Intervention: localhost:8003
echo Keep this window open.
