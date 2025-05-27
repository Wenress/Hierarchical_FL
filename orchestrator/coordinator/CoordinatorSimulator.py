from coordinator import CoordinatorBase
from coordinator.utils import run_shell_script

class CoordinatorSimulator(CoordinatorBase):
    def __init__(self, config):
        super().__init__(config)
        self.kill_script_path = config["orchestrator"]["kill_edge_path"]
        self.run_script_path = config["orchestrator"]["run_edge_path"]

    def _remove_edge(self, edge_server_ip: str):
            """Simulate removing an edge server."""
            run_shell_script(self.kill_script_path, edge_server_ip)

    def _add_edge(self, edge_server_ip: str):
            """Simulate adding a new edge server."""
            run_shell_script(self.run_script_path, edge_server_ip)
    
    def allocate(self, client_id):
        message = super().allocate(client_id)
        super().print_status()
        return message
