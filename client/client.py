import flwr as fl

from model import ModelV2
from torchvision import datasets
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader, random_split
from FlowerClient import FlowerClient

import argparse
from configs.utils import load_config

import requests
import torch


# Dataset 
train_data = datasets.FashionMNIST(
    root="data", #where to download data
    train=True, #we want the training dataset
    download=True, #do we want to download?
    transform=ToTensor(), #which transformation to apply to the data
    target_transform=None #which transformation to apply to the target/label
)

test_data = datasets.FashionMNIST(
    root="data", #where to download data
    train=False, #we want the test dataset
    download=True, #do we want to download?
    transform=ToTensor(), #which transformation to apply to the data
    target_transform=None #which transformation to apply to the target/label
)

n_classes = len(train_data.classes)

# Load config
parser = argparse.ArgumentParser(description="Federated Learning Client")
parser.add_argument(
    "--config", type=str, default="configs/config.yaml", help="Path to the config file"
)
parser.add_argument(
    "--client_id", type=str, default="unknown", help="Unique identifier for the client"
)
args = parser.parse_args()
cfg = load_config(args.config)

generator = torch.Generator()
train_data, _ = random_split(
    train_data,
    [int(cfg["federated_split"]["train"] * len(train_data)), len(train_data) - int(cfg["federated_split"]["train"] * len(train_data))],
    generator=generator
)

validation_data, _ = random_split(
    test_data,
    [int(cfg["federated_split"]["validation"] * len(test_data)), len(test_data) - int(cfg["federated_split"]["validation"] * len(test_data))],
    generator=generator
)


BATCH_SIZE = cfg["training"]["batch_size"]
trainloader = DataLoader(dataset=train_data, batch_size=cfg["training"]["batch_size"], shuffle=True)
testloader = DataLoader(dataset=validation_data, batch_size=cfg["training"]["batch_size"], shuffle=False)
model = ModelV2(input_shape=1, hidden_units = 10, output_shape=n_classes)

# Initialize Flower client
fl_client = FlowerClient(model=model, trainloader=trainloader, testloader=testloader)

# Get edge server IP from orchestrator
orchestrator_ip = f"{cfg['orchestrator']['ip']}:{cfg['orchestrator']['port']}"
url = f"http://{orchestrator_ip}/allocate/{args.client_id}"
response = requests.post(url)
try:
    response.raise_for_status()  # Raise an error for bad responses
    edge_server = response.json().get("edge_server")
    edge_server = f"{edge_server}:{cfg['server']['port']}"
    message = response.json().get("message")
    print(f"{message}: {edge_server}")
except requests.exceptions.RequestException as e:
    print(f"Error allocating edge server: {e}")
    exit(1)

try:
    fl.client.start_numpy_client(server_address=edge_server, client=fl_client)
except Exception as e:
    print(f"Error in Flower client: {e}")

