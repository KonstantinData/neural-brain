"""Non-activating policy lifecycle state machine for preparation evidence."""

from types import MappingProxyType

from neural_brain.privacy.errors import (
    InvalidPolicyTransitionError,
    PrivacyActivationNotAuthorizedError,
)
from neural_brain.privacy.models import (
    PolicyState,
    PreparedPolicyTransition,
    PrivacyOpaqueId,
)

_ALLOWED_TRANSITIONS = MappingProxyType(
    {
        PolicyState.DRAFT: frozenset({PolicyState.PENDING_REVIEW, PolicyState.REJECTED}),
        PolicyState.PENDING_REVIEW: frozenset({PolicyState.APPROVED, PolicyState.REJECTED}),
        PolicyState.APPROVED: frozenset({PolicyState.ACTIVE, PolicyState.SUPERSEDED}),
        PolicyState.ACTIVE: frozenset(
            {
                PolicyState.SUSPENDED,
                PolicyState.REVOKED,
                PolicyState.EXPIRED,
                PolicyState.SUPERSEDED,
            }
        ),
        PolicyState.SUSPENDED: frozenset(
            {PolicyState.ACTIVE, PolicyState.REVOKED, PolicyState.EXPIRED, PolicyState.SUPERSEDED}
        ),
        PolicyState.REVOKED: frozenset(),
        PolicyState.EXPIRED: frozenset(),
        PolicyState.REJECTED: frozenset(),
        PolicyState.SUPERSEDED: frozenset(),
    }
)


class PreparationPolicyStateMachine:
    """Validate the proposed structural graph while prohibiting entry into ``ACTIVE``.

    This preparation helper validates only state adjacency and a non-empty
    reason. It does not validate the actor, authority, evidence, scope, time,
    or audit requirements owned by the future Protected Control Plane gate.
    """

    def allowed_targets(self, current_state: PolicyState) -> frozenset[PolicyState]:
        """Return the proposed graph targets; this does not authorize a transition."""
        return _ALLOWED_TRANSITIONS[current_state]

    def transition(
        self,
        *,
        current_state: PolicyState,
        target_state: PolicyState,
        reason: PrivacyOpaqueId,
    ) -> PreparedPolicyTransition:
        """Return one valid non-activating transition or fail closed."""
        if target_state is PolicyState.ACTIVE:
            raise PrivacyActivationNotAuthorizedError(
                "policy activation requires an accepted ADR and qualified approval"
            )
        if target_state not in self.allowed_targets(current_state):
            raise InvalidPolicyTransitionError(
                f"policy transition {current_state.value} -> {target_state.value} is invalid"
            )
        return PreparedPolicyTransition(
            from_state=current_state,
            to_state=target_state,
            transition_reason=reason,
        )
