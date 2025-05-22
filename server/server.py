import flwr as fl
from FedAvgCustom import FedAvgSafe
from configs.utils import load_config
import argparse

parser = argparse.ArgumentParser(description="Flower server")
parser.add_argument(
	"--config",
	type=str,
	default="config.yaml",
	help="Path to the configuration file (YAML format)",
)

args = parser.parse_args()
config = load_config(args.config)
# Load the configuration file
cfg = load_config(args.config)



strategy = FedAvgSafe(
	min_fit_clients       = cfg["fed_avg"]["min_fit_clients"],
    min_available_clients = cfg["fed_avg"]["min_available_clients"],
    min_evaluate_clients  = cfg["fed_avg"]["min_evaluate_clients"],
    fraction_fit          = cfg["fed_avg"]["fraction_fit"],
    fraction_evaluate     = cfg["fed_avg"]["fraction_evaluate"],
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
