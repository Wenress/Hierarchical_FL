import torch
from collections import OrderedDict

def get_model_ndarrays(model: torch.nn.Module):
    """Restituisce i pesi del modello in formato lista di ndarray (per NumPyClient)."""
    return [w.detach().cpu().numpy() for w in model.state_dict().values()]

def set_model_params(model: torch.nn.Module, params_nd: list):
    """Carica nel modello la lista di ndarray ricevuta da Flower."""
    state_dict = OrderedDict({
        k: torch.tensor(v) for k, v in zip(model.state_dict().keys(), params_nd)
    })
    model.load_state_dict(state_dict, strict=True)

