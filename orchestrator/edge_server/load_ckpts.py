from typing import Callable, Sequence, Any
import numpy as np
import os

def load_ckpt_as_parameters(
    path: str,
    *,
    ordered_keys: Sequence[str] | None = None,
    sort_fn: Callable[[str], Any] | None = None,
    strict: bool = True,
) -> list[np.ndarray] | None:
    if not os.path.exists(path):
        return None

    with np.load(path, allow_pickle=True) as data:
        keys = list(data.files)

        # 1. Ordine esplicito
        if ordered_keys is not None:
            missing = set(ordered_keys) - set(keys)
            if strict and missing:
                raise ValueError(f"Missing keys in the checkpoints: {missing}")
            selected = ordered_keys

        # 2. Ordine tramite funzione
        elif sort_fn is not None:
            selected = sorted(keys, key=sort_fn)

        # 3. Ordine numerico arr_0, arr_1, …
        elif all(k.startswith("arr_") and k[4:].isdigit() for k in keys):
            selected = sorted(keys, key=lambda k: int(k.split('_')[1]))

        # 4. Ordine “così come viene”
        else:
            selected = keys

        return [data[k] for k in selected]
