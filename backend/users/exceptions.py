class InvalidInvitationTransition(ValueError):
    """Raised when an admin invitation cannot move to the requested status."""


class AdminInvitationUserExistsError(ValueError):
    """Raised when inviting an email that already has a registered user account."""
