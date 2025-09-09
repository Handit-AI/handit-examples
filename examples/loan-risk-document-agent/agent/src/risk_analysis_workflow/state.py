"""State definition for the risk analysis workflow."""

from typing import Dict, List, Any, Optional, TypedDict
from datetime import date


class WorkflowState(TypedDict):
    """State passed between workflow nodes."""
    
    # Input data
    files: List[Dict[str, Any]]  # List of {"content": bytes, "type": str, "name": str}
    messages: List[Dict[str, str]]  # Chat messages [{"role": "user/assistant", "content": str}]
    options: Dict[str, Any]  # {"country": "US", "currency": "USD", "disable_checks": []}
    
    # Document classification
    doc_types: Dict[str, str]  # {file_index: "ID"|"PAYSLIP"|"BANK_STATEMENT"|"OTHER"}
    
    # Extracted data (all as JSON from AI)
    extracted_data: Dict[str, Any]  # {
        # "ID": {...},
        # "PAYSLIP": {...},
        # "BANK_STATEMENTS": [...]
    # }
    
    # Identity profile
    identity_profile: Dict[str, Any]  # {
        # "full_name": str,
        # "id_number": str,
        # "expiry_date": str,
        # ...
    # }
    
    # Cross-document analysis
    cross_doc_analysis: Dict[str, Any]  # {
        # "name_match": bool,
        # "employer_match": bool,
        # "currency_consistent": bool,
        # ...
    # }
    
    # Fraud signals
    fraud_signals: Dict[str, Any]  # {
        # "balance_math_ok": bool,
        # "income_plausible": bool,
        # "gambling_exposure": float,
        # ...
    # }
    
    # Risk checks performed
    checks: List[Dict[str, Any]]  # [
        # {"id": str, "category": str, "passed": bool, "severity": str, "details": str}
    # ]
    
    # Risk assessment
    risk_score: float  # 0-100
    risk_tier: str  # "LOW"|"MEDIUM"|"HIGH"|"INVALID"
    reasons: List[str]  # Top reasons for the assessment
    
    # Final response
    assistant_message: str  # Friendly summary for the user
    
    # Metadata
    errors: List[str]
    warnings: List[str]