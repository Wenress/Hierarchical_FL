from flwr.server.strategy import FedAvg
from typing import List, Tuple, Dict, Optional
from flwr.server.client_proxy import ClientProxy
from flwr.common import EvaluateRes, Parameters

class FedAvgSafe(FedAvg):
    def aggregate_evaluate(
        self,
        server_round: int,
        results : List[Tuple[ClientProxy, EvaluateRes]],
        failures: List[BaseException],
    ) -> Optional[Tuple[float, Dict]]:
        total = sum(res.num_examples for _, res in results)
        if total == 0:
            print(f"[Round {server_round}]: No clients participated in evaluation. Returning None.")
            return None
        return super().aggregate_evaluate(server_round, results, failures)
