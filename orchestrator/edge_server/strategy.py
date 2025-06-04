from flwr.server.strategy import FedAvg
import os
from flwr.common import parameters_to_ndarrays
import numpy as np
    
class FedAvgLogger(FedAvg):
    """Custom FedAvg used for logging.
    This class is used to log the model parameters after each round.
    It inherits from FedAvg and overrides the `aggregate_fit` method to log the model parameters and evaluation results.
    """

    def __init__(self, log_path="./logs/", model_path="./models/", server_name="edge_server", *args, **kwargs):
        """Initialize FedAvgLogger with a path to save logs and with a path to save the model weights."""
        super().__init__()
        self.log_path = os.path.join(log_path, server_name)
        os.makedirs(self.log_path, exist_ok=True)
        self.model_path = os.path.join(model_path, server_name)
        os.makedirs(self.model_path, exist_ok=True)
        self.total_rounds = kwargs.get("num_rounds", 1)
        self.client_samples = 0
        self.last_parameters = None
        self.server_name = server_name
        
    
    def aggregate_fit(self, rnd, results, failures):
        """Aggregate model parameters and log the results."""
        log_file = os.path.join(self.log_path, f"fit.log")
        if failures:
            with open(log_file, "a") as f:
                f.write(f"[ERROR] Round {rnd} failed for clients: {failures}\n")

        aggregated_weights, _ = super().aggregate_fit(rnd, results, failures)
        weights_nd = parameters_to_ndarrays(aggregated_weights)
        self.client_samples = sum(res.num_examples for _, res in results)
        self.last_parameters = weights_nd

        # Log the aggregated weights
        with open(log_file, "a") as f:
            f.write(f"Round {rnd} aggregated weights shapes: {[w.shape for w in weights_nd]}\n")
            f.write(f"Round {rnd} total samples: {self.client_samples}\n")

        # Save the aggregated weights to a file during each round
        save_path = os.path.join(self.model_path, f"round_{rnd}_model")
        np.savez(save_path, *weights_nd)
        with open(log_file, "a") as f:
            f.write(f"Round {rnd} model saved to {save_path}\n")
            
        # Return the aggregated weights
        return aggregated_weights, {}
    
    def aggregate_evaluate(self, server_round, results, failures):
        """Aggregate evaluation results and log them."""
        log_file = os.path.join(self.log_path, f"evaluate.log")
        if failures:
            with open(log_file, "a") as f:
                f.write(f"[ERROR] Evaluation failed for clients: {failures}\n")

        weighted_loss, _ = super().aggregate_evaluate(server_round, results, failures)

        # Log the aggregated evaluation results
        with open(log_file, "a") as f:
            f.write(f"Round {server_round} aggregated evaluation loss: {weighted_loss}\n")
        return weighted_loss, {}