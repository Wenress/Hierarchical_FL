import flwr as fl
import os
import numpy as np 
from flwr.common import FitRes, EvaluateRes
from typing import List, Tuple, Dict


class EdgeAggregatorClient(fl.client.NumPyClient):
    """
    Flower client for federated learning.
    This class is responsible for training and evaluating the model on the local dataset.
    """
    
    def __init__(self, strategy, server_name="edge_server", log_path="./logs/"):
        self.strategy = strategy
        log_path = os.path.join(log_path, server_name)
        os.makedirs(log_path, exist_ok=True)
        self.log_path = os.path.join(log_path, "aggregation.log")

    def get_parameters(self, config) -> List[np.ndarray]:
        with open(self.log_path, "a") as f:
            f.write(f"[CLIENT] get_parameters called on the edge_server.\n")
        return self.strategy.last_parameters

    def fit(self, parameters, config) -> Tuple[List[np.ndarray], int, Dict]:
        with open(self.log_path, "a") as f:
            f.write(f"[CLIENT] fit called on the edge_server. Parameters are just loaded, no training performed.\n")
        return (
            self.strategy.last_parameters,
            self.strategy.client_samples,
            {}
        )

    def evaluate(self, parameters, config):
        with open(self.log_path, "a") as f:
            f.write(f"[CLIENT] evaluate called on the edge_server. Evaluation is not performed on Edge Server.\nSent dummy results.\n")
        return None