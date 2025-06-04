docker run -d --rm \
  --name $1 \
  --network fl-network \
  --cpus 4 \
  fl-edge python3 /app/edge_server/server.py \
  --config /app/edge_server/configs/config.yaml \
  --name $1