"""Configuration module for the loan risk document agent."""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Models
    CLASSIFICATION_MODEL = os.getenv("CLASSIFICATION_MODEL", "gpt-4o-mini")
    EXTRACTION_MODEL = os.getenv("EXTRACTION_MODEL", "gpt-4o")
    ASSISTANT_MODEL = os.getenv("ASSISTANT_MODEL", "gpt-4o-mini")
    
    # Flask
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("PORT", 5000))
    
    # File Upload
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    MAX_FILES_PER_REQUEST = int(os.getenv("MAX_FILES_PER_REQUEST", 6))
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "csv"}
    
    # Risk Assessment
    LOW_RISK_THRESHOLD = int(os.getenv("LOW_RISK_THRESHOLD", 40))
    HIGH_RISK_THRESHOLD = int(os.getenv("HIGH_RISK_THRESHOLD", 70))
    
    # Document Processing
    PDF_DPI = int(os.getenv("PDF_DPI", 150))
    OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_PII = os.getenv("LOG_PII", "false").lower() == "true"
    
    # Check weights for scoring
    CHECK_WEIGHTS = {
        "high": 40,
        "medium": 20,
        "low": 10,
        "pass_bonus": -5
    }
    
    # Transaction categories
    TRANSACTION_CATEGORIES = [
        "housing", "utilities", "debt_repayment", "groceries", "dining",
        "transport", "insurance", "healthcare", "subscriptions", "education",
        "salary", "cash", "fees", "gambling", "transfer", "other"
    ]
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

# Export config instance
config = Config()