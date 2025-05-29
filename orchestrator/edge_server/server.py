import flwr as fl
from flwr.server.strategy import FedAvg
from configs.utils import load_config
from FedAvgCustom import FedAvgLogger
import argparse

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
