docker run -d --rm \
  --name $1 \
  --network fl-network \
  --cpus 4 \
  -v "${HOST_ORCHESTRATOR_DIR}/edge_server/":/app \
  flower-image \
  server.py --config ./configs/config.yaml