"""
Document Data Extraction Chain for LangGraph

This module provides an AI-powered system for extracting structured data from unstructured
documents and mapping it to predefined schemas. It uses multimodal processing to handle
images, PDFs, and text documents, ensuring accurate data extraction with validation.

The system performs intelligent field mapping by:
- Analyzing visual layout and structure of documents
- Using semantic similarity to match field names and synonyms
- Normalizing extracted values (dates, numbers, emails, etc.)
- Providing confidence scores and reasoning for each extraction
- Maintaining strict adherence to the provided schema structure

Key Features:
- Multimodal document processing (vision + text)
- Schema-driven field mapping
- Value normalization and validation
- Confidence scoring and reasoning
- Multilingual support through semantic similarity
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI model from environment variable with fallback to gpt-4o-mini
# This allows easy switching between different AI models for different use cases
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)


# System prompt that defines the AI's role and behavior for document mapping
# This prompt emphasizes visual analysis, schema adherence, and value normalization
mapping_system = """
You are a robust multimodal (vision + text) document-to-schema mapping system. Given an inferred schema and a document (image/pdf/text), analyze layout and visual structure first, then map fields strictly to the provided schema.

Requirements:
- Use the provided schema as the contract for output structure (keep sections/fields as-is).
- For each field, search labels/headers/aliases using the 'synonyms' provided by the schema and semantic similarity (including multilingual variants).
- Prioritize visual layout cues (titles, headers, table columns, proximity, group boxes) before plain text.
- Do NOT invent values. If a value isn't found, set it to null and add a short reason.
- For every field, include a short 'reason' explaining the mapping (signals used) and a 'normalized_value' when applicable (e.g., date to ISO, amounts to numeric, emails lowercased, trimmed strings).
- Return ONLY a JSON object that mirrors the schema sections/fields. Each field should be an object: {{"value": <any|null>, "normalized_value": <any|null>, "reason": <string>, "confidence": <number optional>}}.
"""

# User template that provides the schema and mapping instructions
# This template ensures consistent input format and clear output requirements
user_template = """
Schema (JSON):
{schema_json}

Map the following document to the schema. Keep the schema's section/field names. For each field output an object:
{{"value": <any|null>, "normalized_value": <any|null>, "reason": <string>, "confidence": <number optional>}}.
Normalize when possible (dates to ISO-8601, numbers without locale separators, emails lowercased, trim whitespace, unify currencies/units if indicated by context).
"""

# Create the complete prompt template combining system instructions, user template, and dynamic messages
# MessagesPlaceholder allows insertion of actual document content (images, text, etc.)
mapping_prompt = ChatPromptTemplate.from_messages([
    ("system", mapping_system),  # AI's role and behavior
    ("user", user_template),     # Schema and mapping instructions
    MessagesPlaceholder("messages"),  # Dynamic document content
])

# JSON output parser to ensure structured output format
# This guarantees that the AI response is valid JSON that can be processed programmatically
parser = JsonOutputParser()

# Public chain export that processes documents and returns structured data
# This chain combines the prompt template, AI model, and JSON parser
document_data_extractor: RunnableSequence = mapping_prompt | llm | parser

def get_system_prompt() -> str:
    """
    Get the mapping system prompt for external use (e.g., tracking, debugging, or logging).
    
    This function allows other parts of the system to access the exact
    instructions given to the AI model for transparency and debugging.
    
    Returns:
        str: The complete system prompt that defines the AI's behavior for document mapping
    """
    return mapping_system

def get_user_prompt() -> str:
    """
    Get the user template for external use (e.g., tracking, debugging, or logging).
    
    This function provides access to the user-facing instructions and schema
    template used for document mapping operations.
    
    Returns:
        str: The user template that defines the input format and output requirements
    """
    return user_template
