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
            if not self.__dead_edge_server(self.clients[client_id]):
                print(f"Client {client_id} is already allocated to edge server {self.clients[client_id]}")
                #raise RuntimeError(f"Edge server {self.clients[client_id]} did not start in time")
                return {"edge_server": self.clients[client_id], "message": "Client already allocated to an edge server"}
            else:
                print(f"The requested edge server is dead, allocating a new one for client {client_id}")
        
        edge_server_ip = None
        with self.requests_lock:
            if not self.edge_servers or len(self.edge_servers[self.current_edge_server]) >= self.max_clients_per_edge_server:
                print("[LOG] Allocating a new edge server for client:", client_id)
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
                print("[LOG] Allocating to the current edge server for client:", client_id)
                edge_server_ip = self.current_edge_server
        

        if self.__dead_edge_server(edge_server_ip):
            raise RuntimeError(f"Edge server {edge_server_ip} is dead, cannot allocate client")
        
        self.edge_servers[edge_server_ip].append(client_id)
        self.clients[client_id] = edge_server_ip
        return {"edge_server": edge_server_ip, "message": "Client allocated to edge server"}
    
    def __dead_edge_server(self, edge_server_ip: str) -> bool:
        """Check if an edge server is dead by trying to connect to it.
        If the connection fails, it is considered dead.
        In case of a dead edge server, it will be removed from the list of edge servers. Other clients will be removed from it.
        Returns True if the edge server is dead, False otherwise.
        """
        try:
            # if the connection is successful, the edge server is alive
            if self.__wait_for_edge_server(edge_server_ip):
                print(f"[LOG] Edge server {edge_server_ip} is alive")
                return False
            else: 
                raise ConnectionRefusedError(f"[CRITICAL] Issue with edge server {edge_server_ip}")
        except (socket.timeout, ConnectionRefusedError, OSError):
            # If the connection fails, the edge server is considered dead
            print(f"[CRITICAL] Edge server {edge_server_ip} is dead, removing it and its clients")
            with self.requests_lock:
                if edge_server_ip in self.edge_servers:
                    clients = self.edge_servers[edge_server_ip]
                    for client_id in clients:
                        self.clients.pop(client_id, None)
                    self.edge_servers.pop(edge_server_ip, None)
            return True
        
    def __wait_for_edge_server(self, edge_server_ip: str, timeout: int = 10) -> bool:
        """Wait for an edge server to start by trying to connect to it.
        Returns True if the edge server is alive, False if it times out.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Attempt to connect to the edge server
                socket.create_connection((edge_server_ip, self.config["network"]["port"]), timeout=1)
                return True
            except (socket.timeout, ConnectionRefusedError, OSError):
                time.sleep(1)
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
    