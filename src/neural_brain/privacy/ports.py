"""Ports exposed by privacy preparation without a mutation-authorizing surface."""

from datetime import datetime
from typing import Protocol

from neural_brain.privacy.models import (
    PrivacyPreparationDecision,
    PrivacyPreparationInput,
)


class PrivacyPreparationEvaluator(Protocol):
    """Classify blocking preparation outcomes; cannot authorize storage."""

    def evaluate(
        self, request: PrivacyPreparationInput, *, evaluated_at: datetime
    ) -> PrivacyPreparationDecision:
        """Return a decision whose mutation_authorized field is always false."""
        ...
