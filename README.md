# Towards Adaptive and Scalable Hierarchical Federated Learning

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A reference implementation of **Hierarchical Federated Learning (HFL)** using [Flower](https://flower.dev) as the orchestration framework and [PyTorch](https://pytorch.org/) for model definition and training. The hierarchy comprises three logical layers:

1. **Clients** – simulate edge devices holding local data.
2. **Edge Servers** – aggregate updates from a subset of clients.
3. **Central Server** – coordinates the global aggregation across edge servers.

All components are containerised with Docker to enable reproducible, local‑only experiments. Our HFL approach is built around a dynamic allocation of edge servers: in production, these would be provisioned on‑demand via [Azure Virtual Machine Scale Sets (VMSS)](https://azure.microsoft.com/en-us/products/virtual-machine-scale-sets). Because the Education subscription imposes quota limits that block VMSS and public IPs creation, we emulate the same elastic behaviour using local Docker containers. While several prior works rely on Docker (or Kubernetes) for federation, this project explicitly aims to mirror the auto‑scaling characteristics of a VMSS‑based architecture.

Authors: 

- [Marco Lettiero](https://github.com/Wenress) (me)
- [Simone Cioffi](https://github.com/SimoneCff)
- [Daniele D'Alessandro](https://github.com/DanieleDalex)

This project has been realized as part of the Cloud Computing exam at [@uniparthenope](https://github.com/uniparthenope) during the a.y. 2024/2025. Related paper and presentation are available in `Paper` folder.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Building the Docker Images](#building-the-docker-images)
- [Running the Simulation](#running-the-simulation)
- [Configuration](#configuration)
- [Datasets](#datasets)
- [Extending the Project](#extending-the-project)
- [License](#license)
- [Citation](#citation)

---

## Project Structure

```
.
├── client/                 # Flower client implementation (PyTorch)
├── orchestrator/           # Central server logic
│   └── edge_server/        # Edge‑level aggregator logic
├── run_client.sh           # Simple shell script to run a new client with basic configs
├── run_orchestrator.sh     # Simple shell script to run a new orchestrator with basic configs
└── README.md               # You are here

```

---

## Prerequisites

| Tool           | Version (tested) |
| -------------- | ---------------- |
| Python         | $3.10$           |
| Docker         | $28.0$           |


> **Note**: GPU support is optional but recommended for large‐scale experiments. The project *may* work with newer or older versions of the above tools, but these configurations have not been tested.

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Wenress/Hierarchical_FL.git
   cd Hierarchical‑FL
   ```
2. **Create and activate a virtual environment** (optional but encouraged)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## Building the Docker Images

Each layer has its own Dockerfile under `docker/`. 
To build the orchestrator/coordinator image, run from the root directory:
```bash
sudo docker build --no-cache -f orchestrator/Dockerfile -t fl-orchestrator .
```

To build the edge-server image, run from the root directory:
```bash
sudo docker build --no-cache -f orchestrator/edge_server/Dockerfile -t fl-edge .
```

To build the client image, run from the root directory:
```bash
sudo docker build --no-cache -f client/Dockerfile -t fl-client .
```

For the simulation, is also required to create a docker run. To this aim, run:
```bash
sudo docker network create fl-network
```

(Optional) To remove Docker caches, run (and confirm):
```bash
sudo docker builder prune
```

---

## Running the Simulation

Below is the orchestration sequence. 

```bash
# 1. Start the central server using shell script:
sh run_orchestrator.sh

# or, if you want to different Docker options:
sudo docker run --rm \
  --name orchestrator \
  --network fl-network \
  --cpus 4 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e DOCKER_HOST=unix:///var/run/docker.sock \
  fl-orchestrator python3 orchestrator/orchestrator.py \
  --config "/app/orchestrator/configs/config.yaml" 


# 3. Launch, for each desired client, as a shell script:
sh run_client <client_id>

# or, if you want to different Docker options:
sudo docker run --rm \
  --name $1 \
  --network fl-network \
  --cpus 4 \
  fl-client python3 client/client.py \
  --config /app/client/configs/config.yaml --client_id <client_id>
```

If you want to use your configuration file, add the following option:
```bash
-v <your/host/path/file-config.yaml>:<destination/container/path/file-config.yaml>:ro \
```

and, then, just modify the option:
```bash
--config <destination/container/path/file-config.yaml>
```

---

## Configuration

All runtime parameters are expressed in YAML files under `configs/` for each entity. Key sections include:

- `orchestrator`: Global aggregation strategy parameters, number of total rounds, network configuration.
- `edge_server`: Local aggregation strategy parameters, number of rounds, model and logging paths, network configuration (own and orchestrator).
- `client`: training and validation split (for simulation), training batch size, orchestrator IP and port. 

Override any parameter at launch via the `--config` CLI flag or environment variables.

---

## Datasets

The default demo uses **Fasioh-MNIST** for quick iteration. To experiment with your own data, you have to modify accordignly the client script to load other datasets. 
In order to simulate variance among data in different clients, each entity uses a random small fraction of the whole dataset, both for training and validation. Thus, the seed is **not** fixed. 

---

## Extending the Project

- **Different Model** – Swap `model.py` inside `client/` with your architecture.
- **New Dataset** – Implement a new subclass of `torch.utils.data.Dataset`.
- **Custom Aggregation** – Create a new strategy in `orchestrator/strategy.py` or `edge_server/strategy.py` and reference it in the config.

---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## Citation

If you use this repository in your research, please cite it as:

```bibtex
@misc{hfl2025,
  title   = {Towards Adaptive and Scalable Hierarchical Federated Learning},
  author  = {Marco Lettiero and Simone Cioffi and Daniele D'Alessandro},
  year    = {2025},
  howpublished = {\url{https://github.com/Wenress/Hierarchical_FL}}
}
```
