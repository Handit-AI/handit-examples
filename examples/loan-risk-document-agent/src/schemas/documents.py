"""Document data schemas."""

from typing import Optional, List, Dict, Literal
from datetime import date
from pydantic import BaseModel, Field


class IDRecord(BaseModel):
    """Identity document schema."""
    
    id_type: Literal["passport", "national_id", "driver_license", "other"]
    full_name: str
    id_number: str
    nationality: Optional[str] = None
    country_of_issue: Optional[str] = None
    date_of_birth: Optional[date] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    mrz: Optional[str] = None


class Deduction(BaseModel):
    """Payslip deduction."""
    name: str
    amount: float


class PayslipRecord(BaseModel):
    """Payslip document schema."""
    
    employer_name: str
    employer_tax_id: Optional[str] = None
    employee_name: str
    employee_id: Optional[str] = None
    
    pay_period_start: date
    pay_period_end: date
    pay_date: Optional[date] = None
    pay_frequency: Literal["weekly", "biweekly", "semimonthly", "monthly", "other"]
    
    currency: str = Field(description="ISO-4217 currency code")
    gross_pay: float
    net_pay: float
    taxes_withheld: float
    deductions: List[Deduction] = []
    overtime_pay: float = 0
    bonus_pay: float = 0
    
    ytd_gross: Optional[float] = None
    ytd_net: Optional[float] = None


class Transaction(BaseModel):
    """Bank transaction."""
    
    date: date
    description: str
    amount: float  # Positive for credits, negative for debits
    category: Literal[
        "housing", "utilities", "debt_repayment", "groceries", "dining",
        "transport", "insurance", "healthcare", "subscriptions", "education",
        "salary", "cash", "fees", "gambling", "transfer", "other"
    ] = "other"


class ComputedMetrics(BaseModel):
    """Computed bank statement metrics."""
    
    avg_daily_balance: float
    min_daily_balance: float
    max_daily_balance: float
    salary_inflows_sum: float
    salary_inflows_count: int
    avg_monthly_income: float
    avg_monthly_spend: float
    category_spend_month: Dict[str, float] = Field(
        default_factory=lambda: {
            "housing": 0, "utilities": 0, "debt_repayment": 0,
            "groceries": 0, "dining": 0, "transport": 0,
            "insurance": 0, "healthcare": 0, "subscriptions": 0,
            "education": 0, "cash": 0, "fees": 0, "gambling": 0, "other": 0
        }
    )


class BankStatementRecord(BaseModel):
    """Bank statement document schema."""
    
    account_id_last4: Optional[str] = None
    institution: Optional[str] = None
    statement_start: date
    statement_end: date
    currency: str = Field(description="ISO-4217 currency code")
    
    opening_balance: float
    closing_balance: float
    credits_sum: float
    debits_sum: float
    
    transactions: List[Transaction] = []
    
    nsf_count: int = 0
    overdraft_days: int = 0
    inflow_descriptions: List[str] = []
    
    computed: ComputedMetrics