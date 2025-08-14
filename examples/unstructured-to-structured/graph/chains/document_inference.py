from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os

load_dotenv()

# Resolve model from environment variable, default to gpt-4o-mini
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
llm = ChatOpenAI(model=model_name, temperature=0)


class SchemaField(BaseModel):
    """Represents a single field in the inferred schema."""

    name: str = Field(description="Field name")
    types: List[str] = Field(description="Allowed JSON types, e.g., ['string'], ['number'], ['string','null'], ['object'], ['array']")
    description: str = Field(description="What the field represents and how to interpret it")
    required: bool = Field(description="Whether this field is commonly present across the provided documents")
    examples: Optional[List[str]] = Field(default=None, description="Representative example values if known")
    enum: Optional[List[str]] = Field(default=None, description="Enumerated set of possible values when applicable")
    format: Optional[str] = Field(default=None, description="Special format hint like 'date', 'email', 'phone', 'currency', 'lang' etc.")
    reason: str = Field(description="Brief rationale for inferring this field (signals, patterns, layout cues)")


class SchemaSection(BaseModel):
    """Logical grouping of fields (keep generic, not tied to a specific document type)."""

    name: str = Field(description="Section name (generic), e.g., 'core', 'entities', 'dates', 'financial', 'items', 'metadata'")
    fields: List[SchemaField] = Field(description="Fields within this section")


class InferredSchema(BaseModel):
    """Top-level inferred schema for a heterogeneous set of documents."""

    title: str = Field(description="Human-readable title of the inferred schema")
    version: str = Field(description="Schema semantic version, e.g., '0.1.0'")
    description: str = Field(description="High-level description of the schema and how it was inferred")

    common_sections: List[SchemaSection] = Field(description="Sections that apply broadly across the provided documents")
    specialized_sections: Optional[Dict[str, List[SchemaSection]]] = Field(
        default=None,
        description="Optional mapping of document_type -> sections specific to that type",
    )

    rationale: str = Field(description="Concise explanation of the main signals used to infer this schema")


# Configure the LLM to emit the structured schema directly
structured_llm_schema = llm.with_structured_output(InferredSchema)

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

schema_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("messages"),
    ]
)

# Create the schema inference chain
schema_inferencer: RunnableSequence = schema_prompt | structured_llm_schema
