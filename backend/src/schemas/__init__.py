"""Pydantic schemas for API request/response validation.

T061: Export all schemas in src/schemas/__init__.py
"""

# Enums (T059)
from src.schemas.enums import (
    UserTier,
    TaskPriority,
    CompletedBy,
    SubtaskSource,
    TranscriptionStatus,
    ReminderType,
    NotificationMethod,
    AchievementCategory,
    PerkType,
    CreditType,
    CreditOperation,
    SubscriptionStatus,
    EntityType,
    ActivitySource,
    NotificationType,
    JobStatus,
    JobType,
    TombstoneEntityType,
)

# Common schemas (T055)
from src.schemas.common import (
    PaginationParams,
    PaginationMeta,
    PaginatedResponse,
    DataResponse,
    ErrorDetail,
    ErrorResponse,
    ErrorWrapper,
    DeleteResponse,
    MessageResponse,
    CountResponse,
    ErrorCode,
)

# Auth schemas (T046)
from src.schemas.auth import (
    GoogleCallbackRequest,
    RefreshRequest,
    LogoutRequest,
    UserInfo,
    TokenResponse,
    TokenRefreshResponse,
    JWKSResponse,
)

# Task schemas (T047)
from src.schemas.task import (
    TaskCreate,
    TaskUpdate,
    ForceCompleteRequest,
    TaskResponse,
    SubtaskInTask,
    ReminderInTask,
    TaskDetailResponse,
    TaskListFilters,
)

# Subtask schemas (T048)
from src.schemas.subtask import (
    SubtaskCreate,
    SubtaskUpdate,
    SubtaskReorderRequest,
    SubtaskResponse,
    SubtaskOrderResponse,
)

# Note schemas (T049)
from src.schemas.note import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    NoteListFilters,
    TaskSuggestion,
    NoteConvertResponse,
)

# Reminder schemas (T050)
from src.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
)

# AI schemas (T051)
from src.schemas.ai import (
    ChatContext,
    ChatRequest,
    SuggestedAction,
    ChatResponse,
    SubtaskGenerationRequest,
    SubtaskSuggestion,
    SubtaskGenerationResponse,
    ConfirmActionRequest,
    TranscribeRequest,
    TranscriptionResponse,
    CreditBalance,
    CreditBalanceResponse,
)

# Achievement schemas (T052)
from src.schemas.achievement import (
    AchievementPerk,
    UnlockedAchievement,
    AchievementProgress,
    UserStats,
    EffectiveLimits,
    AchievementResponse,
    UserStatsResponse,
    EffectiveLimitsResponse,
)

# Subscription schemas (T053)
from src.schemas.subscription import (
    SubscriptionFeatures,
    SubscriptionResponse,
    CheckoutSessionResponse,
    CancelSubscriptionResponse,
    WebhookPayload,
    PurchaseCreditsRequest,
    PurchaseCreditsResponse,
)

# Notification schemas (T054)
from src.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationListFilters,
    MarkAllReadResponse,
    PushSubscriptionRequest,
    PushSubscriptionResponse,
)

# AI Agent schemas (T056-T058)
from src.schemas.ai_agents import (
    SubtaskSuggestionAgent,
    SubtaskGenerationResult,
    ActionSuggestion,
    ChatAgentResult,
    NoteConversionResult,
)

# Focus schemas (Phase 16)
from src.schemas.focus import (
    FocusStartRequest,
    FocusEndRequest,
    FocusSessionResponse,
)

# Template schemas (Phase 6)
from src.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListResponse,
    GenerateInstanceResponse,
)

__all__ = [
    # Enums
    "UserTier",
    "TaskPriority",
    "CompletedBy",
    "SubtaskSource",
    "TranscriptionStatus",
    "ReminderType",
    "NotificationMethod",
    "AchievementCategory",
    "PerkType",
    "CreditType",
    "CreditOperation",
    "SubscriptionStatus",
    "EntityType",
    "ActivitySource",
    "NotificationType",
    "JobStatus",
    "JobType",
    "TombstoneEntityType",
    # Common
    "PaginationParams",
    "PaginationMeta",
    "PaginatedResponse",
    "DataResponse",
    "ErrorDetail",
    "ErrorResponse",
    "ErrorWrapper",
    "DeleteResponse",
    "MessageResponse",
    "CountResponse",
    "ErrorCode",
    # Auth
    "GoogleCallbackRequest",
    "RefreshRequest",
    "LogoutRequest",
    "UserInfo",
    "TokenResponse",
    "TokenRefreshResponse",
    "JWKSResponse",
    # Task
    "TaskCreate",
    "TaskUpdate",
    "ForceCompleteRequest",
    "TaskResponse",
    "SubtaskInTask",
    "ReminderInTask",
    "TaskDetailResponse",
    "TaskListFilters",
    # Subtask
    "SubtaskCreate",
    "SubtaskUpdate",
    "SubtaskReorderRequest",
    "SubtaskResponse",
    "SubtaskOrderResponse",
    # Note
    "NoteCreate",
    "NoteUpdate",
    "NoteResponse",
    "NoteListFilters",
    "TaskSuggestion",
    "NoteConvertResponse",
    # Reminder
    "ReminderCreate",
    "ReminderUpdate",
    "ReminderResponse",
    # AI
    "ChatContext",
    "ChatRequest",
    "SuggestedAction",
    "ChatResponse",
    "SubtaskGenerationRequest",
    "SubtaskSuggestion",
    "SubtaskGenerationResponse",
    "ConfirmActionRequest",
    "TranscribeRequest",
    "TranscriptionResponse",
    "CreditBalance",
    "CreditBalanceResponse",
    # Achievement
    "AchievementPerk",
    "UnlockedAchievement",
    "AchievementProgress",
    "UserStats",
    "EffectiveLimits",
    "AchievementResponse",
    "UserStatsResponse",
    "EffectiveLimitsResponse",
    # Subscription
    "SubscriptionFeatures",
    "SubscriptionResponse",
    "CheckoutSessionResponse",
    "CancelSubscriptionResponse",
    "WebhookPayload",
    "PurchaseCreditsRequest",
    "PurchaseCreditsResponse",
    # Notification
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationListFilters",
    "MarkAllReadResponse",
    "PushSubscriptionRequest",
    "PushSubscriptionResponse",
    # AI Agents
    "SubtaskSuggestionAgent",
    "SubtaskGenerationResult",
    "ActionSuggestion",
    "ChatAgentResult",
    "NoteConversionResult",
    # Focus
    "FocusStartRequest",
    "FocusEndRequest",
    "FocusSessionResponse",
    # Template
    "TemplateCreate",
    "TemplateUpdate",
    "TemplateResponse",
    "TemplateListResponse",
    "GenerateInstanceResponse",
]
