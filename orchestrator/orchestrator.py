from fastapi import FastAPI
from contextlib import asynccontextmanager
from configs import load_config
import argparse
import uvicorn
from coordinator import CoordinatorSimulator

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

if __name__ == "__main__":
    print(f"Starting Orchestrator...")
    uvicorn.run(app, host=cfg["network"]["ip"], port=cfg["network"]["port"])
    print(f"Orchestrator running on {cfg['network']['ip']}:{cfg['network']['port']}")
