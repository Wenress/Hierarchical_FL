import flwr as fl

from model import ModelV2
from torchvision import datasets
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
from FlowerClient import FlowerClient

import argparse
from configs.utils import load_config

import requests


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

BATCH_SIZE = 64
trainloader = DataLoader(dataset=train_data, batch_size=cfg["training"]["batch_size"], shuffle=True)
testloader = DataLoader(dataset=test_data, batch_size=cfg["training"]["batch_size"], shuffle=False)
n_classes = len(train_data.classes)
model = ModelV2(input_shape=1, hidden_units = 10, output_shape=n_classes)


fl_client = FlowerClient(model=model, trainloader=trainloader, testloader=testloader)
ip_address = f"{cfg['server']['ip']}:{cfg['server']['port']}"
orchestrator_ip = f"{cfg['orchestrator']['ip']}:{cfg['orchestrator']['port']}"
url = f"http://{orchestrator_ip}/allocate/{args.client_id}"
response = requests.post(url)
try:
    response.raise_for_status()  # Raise an error for bad responses
    edge_server = response.json().get("edge_server")
    message = response.json().get("message")
    print(f"{message}: {edge_server}")
except requests.exceptions.RequestException as e:
    print(f"Error allocating edge server: {e}")
    exit(1)

# fl.client.start_numpy_client(server_address=ip_address, client=fl_client)

