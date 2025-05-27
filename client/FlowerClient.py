import torch
import flwr as fl
from torch import optim
from tqdm import tqdm
from torchmetrics import Accuracy
from torch.utils.data import DataLoader
from fl_utils.utils import set_model_params, get_model_ndarrays
from model import ModelV2


class FlowerClient(fl.client.NumPyClient):
    """
    Flower client for federated learning.
    This class is responsible for training and evaluating the model on the local dataset.
    """
    
    def __init__(self, 
                 model, 
                 trainloader: DataLoader, 
                 testloader: DataLoader, 
                 criterion=torch.nn.CrossEntropyLoss(), 
                 metric=Accuracy(task="multiclass", num_classes=10),
                ):
        self.model = model
        self.trainloader = trainloader
        self.testloader = testloader
        self.criterion = criterion
        self.metric = metric

    def get_parameters(self, config):
        print("[CLIENT] get_parameters chiamato")
        return get_model_ndarrays(self.model)

    def fit(self, parameters, config):
        print("[CLIENT] fit chiamato")
        try:
            set_model_params(self.model, parameters)
            opt = optim.SGD(self.model.parameters(), lr=0.01, momentum=0.9)
            print("[CLIENT] Parametri caricati correttamente")
        except Exception as e:
            print(f"[CLIENT] Errore caricamento parametri: {e}")
            raise e
        self.model.train()
        for X, y in tqdm(self.trainloader, desc="Training..."):
            opt.zero_grad()
            loss = self.criterion(self.model(X),y)
            loss.backward()
            opt.step()
        print("[CLIENT] Fit completato")
        return get_model_ndarrays(self.model), len(self.trainloader.dataset), {}

    def evaluate(self, parameters, config):
        print("[CLIENT] evaluate chiamato")
        set_model_params(self.model, parameters)
        self.model.eval()
        print("[CLIENT] Model parameters loaded in evaluation mode")
        try:
            
            total_loss   = 0.0
            total_samples = 0

            with torch.inference_mode():
                for X_test, y_test in tqdm(self.testloader, desc="Testing..."):
                    logits = self.model(X_test)
                    # ---- loss ----
                    total_loss += self.criterion(logits, y_test).item() * y_test.size(0) 

                    # ---- accuracy ----
                    self.metric.update(logits, y_test) 
                    total_samples += y_test.size(0)

            avg_loss = total_loss / total_samples
            avg_acc  = self.metric.compute().item()
            print(f"[CLIENT] Test Loss: {avg_loss:.4f}, Test Accuracy: {avg_acc:.4f}")
            return avg_loss, total_samples, {"accuracy": avg_acc}
        except Exception as e:
            print(f"[CLIENT] Errore durante l'evaluazione: {e}")
            return 0.0, 0, {"accuracy": 0.0}
        finally:
            self.metric.reset()
            print("[CLIENT] evaluate completato")