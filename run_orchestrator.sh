ORCHESTRATOR_DIR="$(pwd)/orchestrator/"

sudo docker run --rm \
  --name orchestrator \
  --network fl-network \
  --cpus 4 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "${ORCHESTRATOR_DIR}":/app \
  -e HOST_ORCHESTRATOR_DIR="${ORCHESTRATOR_DIR}" \
  -e DOCKER_HOST=unix:///var/run/docker.sock \
  flower-image \
  orchestrator.py --config ./configs/config.yaml