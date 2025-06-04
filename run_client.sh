clear

sudo docker run --rm \
  --name $1 \
  --network fl-network \
  --cpus 4 \
  fl-client python3 client/client.py \
  --config /app/client/configs/config.yaml --client_id $1