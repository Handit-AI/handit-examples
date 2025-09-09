"""Assessment and profile schemas."""

from typing import Optional, List, Dict, Literal, Any
from datetime import date
from pydantic import BaseModel, Field

from .documents import IDRecord, PayslipRecord, BankStatementRecord


class Identity(BaseModel):
    """Applicant identity profile."""
    
    full_name: str
    id_number: str
    dob: Optional[date] = None
    nationality: Optional[str] = None
    country_of_issue: Optional[str] = None
    residence_country: Optional[str] = None
    expiry_date: Optional[date] = None


class Employment(BaseModel):
    """Applicant employment profile."""
    
    employer_name: Optional[str] = None
    pay_frequency: Optional[Literal["weekly", "biweekly", "semimonthly", "monthly", "other"]] = None
    stated_income_monthly_gross: Optional[float] = None
    stated_income_monthly_net: Optional[float] = None


class SalaryDetection(BaseModel):
    """Salary detection from bank statements."""
    
    employer_name_from_inflows: Optional[str] = None
    salary_inflows_sum: float = 0
    salary_inflows_count: int = 0
    salary_regular_interval: bool = False


class Banking(BaseModel):
    """Applicant banking profile."""
    
    accounts: List[str] = []  # Last 4 digits of accounts
    period_months: int = 0
    avg_monthly_income: float = 0
    avg_monthly_spend: float = 0
    income_volatility_pct: float = 0
    cash_buffer_days: float = 0
    nsf_count_total: int = 0
    overdraft_days_total: int = 0
    category_spend_month_avg: Dict[str, float] = Field(default_factory=dict)
    salary_detection: SalaryDetection = Field(default_factory=SalaryDetection)


class Consistency(BaseModel):
    """Cross-document consistency checks."""
    
    name_match: bool = False
    employer_match: bool = False
    currency_consistent: bool = True
    balance_math_ok: bool = True


class ApplicantFinancialProfile(BaseModel):
    """Complete applicant financial profile."""
    
    identity: Identity
    employment: Employment = Field(default_factory=Employment)
    banking: Banking = Field(default_factory=Banking)
    consistency: Consistency = Field(default_factory=Consistency)


class Check(BaseModel):
    """Risk check result."""
    
    check_id: Optional[str] = None
    id: Optional[str] = None
    category: Optional[str] = "data"
    passed: bool = False
    severity: Optional[str] = "medium"
    details: Optional[str] = ""


class ExtractedDocuments(BaseModel):
    """All extracted documents."""
    
    ID: Optional[Dict[str, Any]] = None
    PAYSLIP: Optional[Dict[str, Any]] = None
    BANK_STATEMENTS: List[Dict[str, Any]] = []


class Assessment(BaseModel):
    """Complete risk assessment."""
    
    risk_score: float = 0
    risk_tier: str = "INVALID"
    reasons: List[str] = []
    checks: List[Dict[str, Any]] = []
    doc_types: Dict[str, str] = {}  # File index to document type
    extracted: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None


class ChatMessage(BaseModel):
    """Chat message."""
    
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """Chat request options."""
    
    country: str = "US"
    currency: str = "USD"
    disable_checks: List[str] = []


class ChatResponse(BaseModel):
    """Complete chat response."""
    
    assistant_message: str
    assessment: Assessment