from fastapi import FastAPI
from contextlib import asynccontextmanager
from utils.run_sh import run_shell_script
from configs.utils import load_config
import argparse
import threading
import sys

edge_servers = {}
current_edge_server = None

parser = argparse.ArgumentParser(description="Orchestrator")
parser.add_argument(
    "--config", type=str, default="configs/config.yaml", help="Path to the config file"
)
args = parser.parse_args()
cfg = load_config(args.config)

#root_path = os.path.join(os.getcwd(), "orchestrator")

MAX_CLIENTS_PER_EDGE_SERVER = cfg["orchestrator"]["max_clients_per_edge_server"]

def cleanup_edge_servers(edge_servers: list, script_path: str):
    """Clean up edge servers by terminating their processes."""
    for edge_server in edge_servers:
        run_shell_script(script_path, edge_server)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Shutting down Orchestrator...")
    for edge_server in edge_servers.keys():
        #script_path = os.path.join(root_path, "utils", "kill_edge_server.sh")
        cleanup_edge_servers(edge_servers.keys(), cfg["orchestrator"]["kill_edge_path"])

app = FastAPI(lifespan=lifespan)
requests_lock = threading.Lock()
current_edge_server = None

@app.get("/allocate/{client_id}", response_model=dict)
async def allocate(client_id: str):

    with requests_lock:
        if not edge_servers: #or len(edge_servers[current_edge_server]) > MAX_CLIENTS_PER_EDGE_SERVER:
            # allocate a new edge server
            edge_server_ip = f"edge{len(edge_servers) + 1}"
            current_edge_server = edge_server_ip
            edge_servers[edge_server_ip] = [client_id]
            #script_path = os.path.join(root_path, "utils", "run_edge_server.sh")
            run_shell_script(cfg["orchestrator"]["run_edge_path"], edge_server_ip)
            return {"edge_server": edge_server_ip, "message": "New edge server allocated."}
        else:
            # allocate to the current edge server
            edge_servers[current_edge_server].append(client_id)
            return {"edge_server": current_edge_server, "message": "Client allocated to existing edge server."}

if __name__ == "__main__":
    print(f"Starting Orchestrator...")
    import uvicorn
    uvicorn.run(app, host=cfg["network"]["ip"], port=cfg["network"]["port"])
    print(f"Orchestrator running on {cfg['network']['ip']}:{cfg['network']['port']}")
