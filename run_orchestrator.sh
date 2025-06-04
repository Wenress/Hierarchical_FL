clear

ORCHESTRATOR_DIR="$(pwd)/orchestrator/"

sudo docker run --rm \
  --name orchestrator \
  --network fl-network \
  --cpus 4 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e HOST_ORCHESTRATOR_DIR="${ORCHESTRATOR_DIR}" \
  -e DOCKER_HOST=unix:///var/run/docker.sock \
  fl-orchestrator python3 orchestrator/orchestrator.py \
  --config "/app/orchestrator/configs/config.yaml" 