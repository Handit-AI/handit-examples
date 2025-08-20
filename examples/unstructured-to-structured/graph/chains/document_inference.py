"""
Document Inference Chain for LangGraph

This module provides an AI-powered system for automatically generating JSON schemas
from unstructured documents. It uses OpenAI's vision and language models to analyze
document content and infer appropriate data structures.

The system can handle various document types including:
- Images (PNG, JPG, JPEG, GIF, BMP)
- PDF files
- Text documents
- Binary files

Key Components:
- SchemaField: Defines individual data fields with types, validation, and metadata
- SchemaSection: Groups related fields into logical sections
- InferredSchema: Top-level schema structure for heterogeneous documents
- schema_inferencer: LangChain chain that processes documents and generates schemas

Usage:
    The schema_inferencer chain takes multimodal messages containing document content
    and returns structured JSON schemas that can be used for data extraction and
    validation across different document types.
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI model from environment variable with fallback to gpt-4o-mini
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
llm = ChatOpenAI(model=model_name, temperature=0)


class SchemaField(BaseModel):
    """
    Represents a single field in the inferred schema.
    
    Each field defines the structure, validation rules, and metadata for a piece
    of data extracted from documents. Fields can be simple (string, number) or
    complex (objects, arrays) depending on the document structure.
    """

    name: str = Field(description="Field name")
    types: List[str] = Field(description="Allowed JSON types, e.g., ['string'], ['number'], ['string','null'], ['object'], ['array']")
    description: str = Field(description="What the field represents and how to interpret it")
    required: bool = Field(description="Whether this field is commonly present across the provided documents")
    examples: Optional[List[str]] = Field(default=None, description="Representative example values if known")
    enum: Optional[List[str]] = Field(default=None, description="Enumerated set of possible values when applicable")
    format: Optional[str] = Field(default=None, description="Special format hint like 'date', 'email', 'phone', 'currency', 'lang' etc.")
    reason: str = Field(description="Brief rationale for inferring this field (signals, patterns, layout cues)")


class SchemaSection(BaseModel):
    """
    Logical grouping of fields to organize the schema structure.
    
    Sections help organize related fields into meaningful groups rather than
    having all fields in a flat list. This improves schema readability and
    makes it easier to understand the document structure.
    """

    name: str = Field(description="Section name (generic), e.g., 'core', 'entities', 'dates', 'financial', 'items', 'metadata'")
    fields: List[SchemaField] = Field(description="Fields within this section")


class InferredSchema(BaseModel):
    """
    Top-level inferred schema for a heterogeneous set of documents.
    
    This schema represents the unified structure that can accommodate various
    document types and formats. It combines common patterns found across
    multiple documents into a single, flexible schema definition.
    """

    title: str = Field(description="Human-readable title of the inferred schema")
    version: str = Field(description="Schema semantic version, e.g., '0.1.0'")
    description: str = Field(description="High-level description of the schema and how it was inferred")

    common_sections: List[SchemaSection] = Field(description="Sections that apply broadly across the provided documents")
    specialized_sections: Optional[Dict[str, List[SchemaSection]]] = Field(
        default=None,
        description="Optional mapping of document_type -> sections specific to that type",
    )

    rationale: str = Field(description="Concise explanation of the main signals used to infer this schema")


# Configure the LLM to emit structured output matching our Pydantic models
# This ensures type safety and consistent output format
structured_llm_schema = llm.with_structured_output(InferredSchema)

# System prompt that instructs the AI model on how to generate schemas
# The prompt emphasizes document-driven inference and consistent formatting
system = """
You are a senior information architect. Given multiple heterogeneous documents (any type, any language), infer the most appropriate, general JSON schema that can represent them.

Guidance:
- Infer structure purely from the supplied documents; avoid biasing toward any specific document type.
- Use lower_snake_case for field names.
- Use JSON types: string, number, boolean, object, array, null. When a field may be missing, include null in its types.
- Allow nested objects and arrays where the documents imply hierarchical structure.
- Include brief, useful descriptions for fields when possible without inventing content.
- Return ONLY JSON that matches the provided Pydantic model for an inferred schema.

 Per-field requirements:
 - For each field, add a short 'reason' explaining the signals used to infer the field (keywords, repeated labels, table headers, layout proximity, visual grouping, etc.).
"""

# Create prompt template combining system instructions with user input
# MessagesPlaceholder allows dynamic insertion of document content
schema_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("messages"),
    ]
)

# Create the complete schema inference chain
# This chain processes documents through the prompt and returns structured schemas
schema_inferencer: RunnableSequence = schema_prompt | structured_llm_schema

def get_system_prompt() -> str:
    """
    Get the system prompt for external use (e.g., tracking, debugging, or logging).
    
    This function allows other parts of the system to access the exact
    instructions given to the AI model for transparency and debugging.
    
    Returns:
        str: The complete system prompt that defines the AI's behavior
    """
    return system
