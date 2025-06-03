from fastapi import FastAPI
from contextlib import asynccontextmanager
from configs import load_config
import argparse
import uvicorn
import sys
import signal
from coordinator import CoordinatorSimulator
import multiprocessing as mp
from flwr.server.strategy import FedAvg
from flwr.server import ServerConfig
import flwr as fl

parser = argparse.ArgumentParser(description="Orchestrator")
parser.add_argument(
    "--config", type=str, default="configs/config.yaml", help="Path to the config file"
)
args = parser.parse_args()
cfg = load_config(args.config)

coordinator = CoordinatorSimulator(cfg)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Shutting down Orchestrator...")
    coordinator.cleanup_edge_servers()

app = FastAPI(lifespan=lifespan)

@app.post("/allocate/{client_id}", response_model=dict)
async def allocate(client_id: str):
    """Allocate a client to an edge server."""
    return coordinator.allocate(client_id)

def start_web_server():
    """Start the FastAPI web server."""
    uvicorn.run(app, host=cfg["network"]["ip"], port=cfg["network"]["port"])

def start_flower_server():
    """Start the Flower server."""
    strategy = FedAvg(
        min_fit_clients=cfg["fed_avg"]["min_fit_clients"],
        min_available_clients=cfg["fed_avg"]["min_available_clients"],
        min_evaluate_clients=cfg["fed_avg"]["min_evaluate_clients"],
        fraction_fit=cfg["fed_avg"]["fraction_fit"],
        fraction_evaluate=cfg["fed_avg"]["fraction_evaluate"],
    )
    ip = f"[::]:{cfg['fed_avg']['port']}"
    config = ServerConfig(
        num_rounds=1, # orchestrator will simply aggregate the results
    )

    try:
        fl.server.start_server(
            server_address=ip,
            config=config,
            strategy=strategy
        )
    except Exception as e:
        print(f"Error with Flower server: {e}")
        sys.exit(1)

    print("Federated session has been completed.")
    

if __name__ == "__main__":
    web_server = mp.Process(target=start_web_server, daemon=False, name="APIWebServer")
    flower_server = mp.Process(target=start_flower_server, daemon=False, name="FlowerServer")

    def _signal_handler(sig, frame):
        print("\n[orchestrator] SIGINT received, killing servers…")
        for p in (web_server, flower_server):
            if p.is_alive():
                print(f"[orchestrator] Process {p.name} (pid={p.pid}) has been killed.")
                p.terminate()
        # wait for processes to finish
        web_server.join(timeout=5)
        #p_flower.join(timeout=5)
        print("[orchestrator] All servers have been killed.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, _signal_handler)

    print(f"Starting Orchestrator...")
    web_server.start()
    print(f"Orchestrator running on {cfg['network']['ip']}:{cfg['network']['port']}")
    print("Starting Flower server...")
    flower_server.start()
    print("Flower server started.")

    # Wait for the web server to finish
    flower_server.join()  # Wait for the Flower server to finish
    print("Flower server has stopped.")
    # when the Flower server is stopped, the orchestrator will also stop
    print("Waiting for the web server to finish...")
    # kill the web server if it is still running
    web_server.terminate()  # Terminate the web server process
    print("Web server has been terminated.")
    web_server.join()  # Wait for the web server to finish
    print("Orchestrator has stopped.")

