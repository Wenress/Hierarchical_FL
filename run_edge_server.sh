sudo docker run --rm \
  --name fl-server \
  --network fl-network \
  --cpus 2 \
  -v $(pwd)/server:/app \
  flower-image \
  server.py --config ./configs/config.yaml