import threading
from abc import ABC, abstractmethod
import time
import socket

class CoordinatorBase(ABC):
    def __init__(self, config):
        self.edge_servers = {}
        self.max_clients_per_edge_server = config["orchestrator"]["max_clients_per_edge_server"]
        self.current_edge_server = None
        self.config = config
        self.requests_lock = threading.Lock()
        self.clients = {}

    def allocate(self, client_id: str) -> dict:
        """Allocate a client to an edge server."""
        if client_id in self.clients:
            if not self.__wait_for_edge_server(self.clients[client_id]):
                raise RuntimeError(f"Edge server {self.clients[client_id]} did not start in time")
            return {"edge_server": self.clients[client_id], "message": "Client already allocated to an edge server"}
        
        edge_server_ip = None
        with self.requests_lock:
            if not self.edge_servers or len(self.edge_servers[self.current_edge_server]) >= self.max_clients_per_edge_server:
                # Allocate a new edge server
                edge_server_ip = f"edge{len(self.edge_servers) + 1}"
                try:
                    self._add_edge(edge_server_ip)
                except Exception as e:
                    raise RuntimeError(f"Failed to add edge server {edge_server_ip}: {e}")
                self.current_edge_server = edge_server_ip
                self.edge_servers[edge_server_ip] = []
            else:
                # Allocate to the current edge server
                edge_server_ip = self.current_edge_server
        
        if not self.__wait_for_edge_server(edge_server_ip):
            self._remove_edge(edge_server_ip)
            raise RuntimeError(f"Edge server {edge_server_ip} did not start in time")
        
        self.edge_servers[edge_server_ip].append(client_id)
        self.clients[client_id] = edge_server_ip
        return {"edge_server": edge_server_ip, "message": "Client allocated to edge server"}
    
    def __wait_for_edge_server(self, edge_server_ip: str) -> bool:
        """Wait for an edge server to be ready. Also checks if the edge server is reachable."""
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                with socket.create_connection((edge_server_ip, 8080), timeout=2):
                    return True
            except (socket.timeout, ConnectionRefusedError, OSError):
                time.sleep(3)
        return False

    
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
    