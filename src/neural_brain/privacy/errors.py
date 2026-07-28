"""Errors raised by the non-authorizing privacy preparation boundary."""


class PrivacyPreparationError(RuntimeError):
    """Base error for fail-closed privacy preparation operations."""


class InvalidPolicyTransitionError(PrivacyPreparationError):
    """Raised when a proposed policy lifecycle transition is not allowed."""


class PrivacyActivationNotAuthorizedError(PrivacyPreparationError):
    """Raised when preparation code is asked to activate a policy."""


class PrivacyReferenceMismatchError(PrivacyPreparationError):
    """Raised when a resolved evidence or approval binding is not exact."""
