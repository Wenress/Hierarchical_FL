import flwr as fl
from configs.utils import load_config
from FedAvgCustom import FedAvgLogger
from EdgeAggregatorClient import EdgeAggregatorClient
import argparse
import os

parser = argparse.ArgumentParser(description="Flower server")
parser.add_argument(
	"--config",
	type=str,
	default="config.yaml",
	help="Path to the configuration file (YAML format)",
)

parser.add_argument(
    "--name",
	type=str,
	default="edge_server",
	help="Name of the edge server",
)

args = parser.parse_args()
config = load_config(args.config)
# Load the configuration file
cfg = load_config(args.config)
log_path = os.path.join(cfg["logging"]["log_path"], args.name,)
os.makedirs(log_path, exist_ok=True)
log_path = os.path.join(log_path, "server.log")
with open(log_path, "w") as f:
	f.write(f"[INIT] Starting Flower server with configuration: {args.config}\n")

strategy = FedAvgLogger(
	min_fit_clients       	= cfg["fed_avg"]["min_fit_clients"],
    min_available_clients 	= cfg["fed_avg"]["min_available_clients"],
    min_evaluate_clients  	= cfg["fed_avg"]["min_evaluate_clients"],
    fraction_fit          	= cfg["fed_avg"]["fraction_fit"],
    fraction_evaluate     	= cfg["fed_avg"]["fraction_evaluate"],
    num_rounds            	= cfg["config"]["num_rounds"],
    model_path 				= cfg["model"]["save_path"],
    log_path				= cfg["logging"]["log_path"],
    server_name 	   		= args.name,	
)

config = fl.server.ServerConfig(
	num_rounds=cfg["config"]["num_rounds"],
)

ip = f"[::]:{cfg['network']['port']}"
fl.server.start_server(
	server_address=ip,
	config=config,
	strategy=strategy
)

with open(log_path, "a") as f:
	f.write(f"Flower server completed with strategy: {strategy.__class__.__name__}\n")
	f.write(f"Server address: {ip}\n")
	f.write(f"[INIT] Edge server is now a client in the federated learning process.\n")

try:
	client = EdgeAggregatorClient(
		strategy=strategy,
		server_name=args.name,
		log_path=cfg["logging"]["log_path"],
	)
except Exception as e:
	with open(log_path, "a") as f:
		f.write(f"[ERROR] Failed to initialize EdgeAggregatorClient: {e}\n")
	exit(1)

try:
    fl.client.start_numpy_client(
        server_address=f"{cfg['orchestrator']['ip']}:{cfg['orchestrator']['port']}", 
        client=client,
	)
except Exception as e:
	with open(log_path, "a") as f:
		f.write(f"[ERROR] Failed to start Flower client: {e}\n")
	exit(1)