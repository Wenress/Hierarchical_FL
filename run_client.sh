sudo docker run --rm \
  --name $1 \
  --network fl-network \
  --cpus 4 \
  -v $(pwd)/client:/app \
  flower-image \
  client.py --config ./configs/config.yaml