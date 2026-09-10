class FoodFlowException(Exception):
    """Base exception for application errors."""


class NotFoundError(FoodFlowException):
    """Requested resource does not exist."""


class UnauthorizedError(FoodFlowException):
    """Authentication failed."""


class ForbiddenError(FoodFlowException):
    """Authenticated user lacks permission."""


class ValidationError(FoodFlowException):
    """Request or business rule validation failed."""


class ConflictError(FoodFlowException):
    """Request conflicts with current system state."""


class InvalidStateTransitionError(FoodFlowException):
    """Requested state transition is not allowed."""


class IdempotencyConflictError(FoodFlowException):
    """Idempotency key conflicts with an existing operation."""