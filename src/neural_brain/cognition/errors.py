"""Fail-closed errors for the first NB-1 cognitive runtime slice."""


class CognitiveRuntimeError(RuntimeError):
    """Base error for safe serial cognition failures."""


class CognitiveScopeError(CognitiveRuntimeError):
    """Authenticated session scope is missing or inconsistent."""


class StaleCognitiveCheckpointError(CognitiveRuntimeError):
    """The expected checkpoint version is no longer current."""


class UnknownNeuralModelError(CognitiveRuntimeError):
    """The requested fixed neural model version is not registered."""


class CognitiveCheckpointUnavailableError(CognitiveRuntimeError):
    """A checkpoint is absent from the authenticated session scope."""
