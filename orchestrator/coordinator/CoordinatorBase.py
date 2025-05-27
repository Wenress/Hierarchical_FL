import threading
from abc import ABC, abstractmethod

class CoordinatorBase(ABC):
    def __init__(self, config):
        self.edge_servers = {}
        self.max_clients_per_edge_server = config["orchestrator"]["max_clients_per_edge_server"]
        self.current_edge_server = None
        self.config = config
        self.requests_lock = threading.Lock()

    def allocate(self, client_id: str) -> dict:
        """Allocate a client to an edge server."""
        with self.requests_lock:
            if not self.edge_servers or len(self.edge_servers[self.current_edge_server]) >= self.max_clients_per_edge_server:
                # Allocate a new edge server
                edge_server_ip = f"edge{len(self.edge_servers) + 1}"
                self.current_edge_server = edge_server_ip
                self.edge_servers[edge_server_ip] = [client_id]
                self._add_edge(edge_server_ip)
                return {"edge_server": edge_server_ip, "message": "New edge server allocated."}
            else:
                # Allocate to the current edge server
                self.edge_servers[self.current_edge_server].append(client_id)
                return {"edge_server": self.current_edge_server, "message": "Client allocated to existing edge server."}
    
    def cleanup_edge_servers(self,):
        """Clean up edge servers by terminating their processes."""
        for edge_server in self.edge_servers.keys():
            self._remove_edge(edge_server)
    
    def print_status(self):
        """Print the current status of edge servers and their clients."""
        print("Current Edge Servers and Clients:")
        for edge_server, clients in self.edge_servers.items():
            print(f"Edge Server: {edge_server}, Clients: {clients}")
        print("")
    
    @abstractmethod
    def _remove_edge(self, edge_server_ip: str):
        """Remove an edge server."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    @abstractmethod
    def _add_edge(self, edge_server_ip: str):
        """Add a new edge server."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    