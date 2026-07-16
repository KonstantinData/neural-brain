"""Fixed-version recurrent neural workspace with learned bounded attention."""

import math
from typing import Literal

from neural_brain.cognition.models import (
    AttentionDecision,
    NeuralWorkspaceParameters,
    RecordedObservation,
)

type AttentionMode = Literal["learned", "uniform"]


class NeuralWorkspace:
    """Apply immutable learned parameters without an online training surface."""

    def __init__(
        self,
        parameters: NeuralWorkspaceParameters,
        *,
        attention_mode: AttentionMode = "learned",
        recurrence_enabled: bool = True,
    ) -> None:
        self.parameters = parameters
        self._attention_mode = attention_mode
        self._recurrence_enabled = recurrence_enabled

    def step(
        self, *, observation: RecordedObservation, previous_hidden: float
    ) -> tuple[AttentionDecision, float]:
        """Run one deterministic attention and recurrent-state transition."""
        distribution = self._attention_distribution()
        projected = sum(
            feature * weight * attention
            for feature, weight, attention in zip(
                observation.features,
                self.parameters.input_weights,
                distribution,
                strict=True,
            )
        )
        recurrent = (
            self.parameters.recurrent_weight * previous_hidden if self._recurrence_enabled else 0.0
        )
        hidden = math.tanh(projected + recurrent + self.parameters.bias)
        selected: Literal[0, 1] = 0 if distribution[0] >= distribution[1] else 1
        return (
            AttentionDecision(distribution=distribution, selected_feature_index=selected),
            hidden,
        )

    def _attention_distribution(self) -> tuple[float, float]:
        if self._attention_mode == "uniform":
            return (0.5, 0.5)
        maximum = max(self.parameters.attention_logits)
        exponentials = tuple(
            math.exp(value - maximum) for value in self.parameters.attention_logits
        )
        total = sum(exponentials)
        return (exponentials[0] / total, exponentials[1] / total)
