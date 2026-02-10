"""Business logic services for Perpetua Flow Backend."""

from src.services.auth_service import (
    AuthService,
    AuthServiceError,
    InvalidRefreshTokenError,
    UserNotFoundError,
    get_auth_service,
)
from src.services.credit_service import (
    ConsumptionResult,
    CreditBalance,
    CreditService,
    get_credit_service,
)
from src.services.recurring_service import (
    InvalidRRuleError,
    RecurringServiceError,
    RecurringTaskService,
    TemplateNotFoundError,
    TemplateUpdateForbiddenError,
    get_recurring_service,
)
from src.services.task_service import (
    SubtaskLimitExceededError,
    SubtaskNotFoundError,
    TaskArchivedError,
    TaskDueDateExceededError,
    TaskLimitExceededError,
    TaskNotFoundError,
    TaskService,
    TaskServiceError,
    TaskVersionConflictError,
    get_task_service,
)
from src.services.user_service import (
    InvalidNameError,
    InvalidTimezoneError,
    UserService,
    UserServiceError,
    get_user_service,
)

__all__ = [
    # Auth Service
    "AuthService",
    "AuthServiceError",
    "InvalidRefreshTokenError",
    "UserNotFoundError",
    "get_auth_service",
    # Credit Service
    "CreditService",
    "CreditBalance",
    "ConsumptionResult",
    "get_credit_service",
    # Recurring Service
    "RecurringTaskService",
    "RecurringServiceError",
    "TemplateNotFoundError",
    "InvalidRRuleError",
    "TemplateUpdateForbiddenError",
    "get_recurring_service",
    # Task Service
    "TaskService",
    "TaskServiceError",
    "TaskNotFoundError",
    "TaskVersionConflictError",
    "TaskArchivedError",
    "TaskLimitExceededError",
    "TaskDueDateExceededError",
    "SubtaskNotFoundError",
    "SubtaskLimitExceededError",
    "get_task_service",
    # User Service
    "UserService",
    "UserServiceError",
    "InvalidNameError",
    "InvalidTimezoneError",
    "get_user_service",
]
