from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

# Get model from environment variable, default to gpt-4o if not set
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
llm = ChatOpenAI(model=model_name, temperature=0)


class DocumentClassification(BaseModel):
    """Classification result for a single document."""
    
    filename: str = Field(description="Name of the file being classified")
    document_type: str = Field(
        description="Type of document. Must be one of: invoice, receipt, contract, report, letter, form, certificate, statement, manual, policy, agreement, other"
    )
    confidence: float = Field(
        description="Confidence level from 0.0 to 1.0 for this classification"
    )
    language: str = Field(
        description="Language of the document (e.g., English, Spanish, French, etc.)"
    )
    reason: str = Field(
        description="Brief explanation of why this document was classified as this type"
    )


class ClassifyDocuments(BaseModel):
    """Classification results for multiple documents."""
    
    classifications: List[DocumentClassification] = Field(
        description="List of classification results for each document"
    )


# Parsing the answer
structured_llm_classifier = llm.with_structured_output(ClassifyDocuments)

system = """You are an expert document classifier with extensive knowledge of business and administrative documents across multiple languages and cultures.

Your task is to analyze and classify documents based on their content, structure, and purpose. You must identify the document type regardless of the language it's written in.

IMPORTANT CLASSIFICATION RULES:
1. Document types must be one of these categories:
   - invoice: Bills, invoices, billing statements
   - receipt: Purchase receipts, payment confirmations, transaction records
   - contract: Legal agreements, contracts, terms of service
   - report: Business reports, financial reports, analysis documents
   - letter: Business letters, official correspondence, memos
   - form: Application forms, registration forms, questionnaires
   - certificate: Certificates, diplomas, official documents
   - statement: Bank statements, financial statements, declarations
   - manual: User manuals, instruction guides, procedures
   - policy: Company policies, rules, guidelines
   - agreement: Agreements, understandings, arrangements
   - other: Any document that doesn't fit the above categories

2. Language detection: Identify the language regardless of the document type
3. Confidence scoring: Provide confidence level from 0.0 to 1.0 based on clarity of document characteristics
4. Brief reasoning: Provide a concise explanation of why you classified the document as this type

OUTPUT SCHEMA:
You must return a JSON object with this exact structure:
{{
  "classifications": [
    {{
      "filename": "exact_filename_with_extension",
      "document_type": "one_of_the_12_types",
      "confidence": 0.95,
      "language": "detected_language",
      "reason": "brief_explanation_why"
    }}
  ]
}}

Analyze each document carefully and provide accurate classifications following this exact schema."""

classification_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("user", """Classify the following documents:

Documents to classify:
{unstructured_paths}

Please analyze each document and provide a comprehensive classification.""")
    ]
)

# Create the classification chain
document_classifier: RunnableSequence = classification_prompt | structured_llm_classifier
