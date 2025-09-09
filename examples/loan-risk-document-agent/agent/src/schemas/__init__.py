"""Schema definitions for the loan risk document agent."""

from .documents import (
    IDRecord,
    PayslipRecord,
    BankStatementRecord,
    Transaction,
    ComputedMetrics,
    Deduction
)

from .assessment import (
    Identity,
    Employment,
    Banking,
    SalaryDetection,
    Consistency,
    ApplicantFinancialProfile,
    Check,
    ExtractedDocuments,
    Assessment,
    ChatMessage,
    ChatRequest,
    ChatResponse
)

__all__ = [
    # Documents
    "IDRecord",
    "PayslipRecord",
    "BankStatementRecord",
    "Transaction",
    "ComputedMetrics",
    "Deduction",
    # Assessment
    "Identity",
    "Employment",
    "Banking",
    "SalaryDetection",
    "Consistency",
    "ApplicantFinancialProfile",
    "Check",
    "ExtractedDocuments",
    "Assessment",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse"
]