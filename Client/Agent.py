from typing import Optional, Any

import torch

from pytorch_regression import Regression


class Agent:
    def __init__(self, model_path: str, min_raycast_value: float, max_raycast_value: float):
        self.nb_input = 4
        self.nb_output = 1
        self.model = Regression(self.nb_input, self.nb_output)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        self.min_raycast_value = min_raycast_value
        self.max_raycast_value = max_raycast_value

    def act(self, state: torch.tensor) -> Optional[Any]:
        # if len(state) != self.nb_input: return None
        normalized_state = (state - self.min_raycast_value) / (self.max_raycast_value - self.min_raycast_value)
        normalized_state = normalized_state.view(-1, 4, 5)
        normalized_state = normalized_state.mean(dim=2)
        return self.model(normalized_state)[0].item()