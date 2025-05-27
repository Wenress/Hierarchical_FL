from fastapi import FastAPI
from contextlib import asynccontextmanager
from configs import load_config
import argparse
import uvicorn
import sys
import signal
from coordinator import CoordinatorSimulator
import multiprocessing as mp

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
    

if __name__ == "__main__":
    web_server = mp.Process(target=start_web_server, daemon=False, name="APIWebServer")

    def _signal_handler(sig, frame):
        print("\n[orchestrator] SIGINT received, killing servers…")
        for p in (web_server, ):
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

    web_server.join()  # Wait for the web server to finish
    print("Orchestrator has stopped.")

