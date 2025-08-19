from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Resolve model from environment; default to a compact but capable model
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)


# Keep the original invoice prompt defined above (unused), and define a generic schema-driven mapping prompt

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

user_template = """
Schema (JSON):
{schema_json}

Map the following document to the schema. Keep the schema's section/field names. For each field output an object:
{{"value": <any|null>, "normalized_value": <any|null>, "reason": <string>, "confidence": <number optional>}}.
Normalize when possible (dates to ISO-8601, numbers without locale separators, emails lowercased, trim whitespace, unify currencies/units if indicated by context).
"""

mapping_prompt = ChatPromptTemplate.from_messages([
    ("system", mapping_system),
    ("user", user_template),
        MessagesPlaceholder("messages"),
])

parser = JsonOutputParser()

# Public chain export (returns dict)
invoice_data_extractor: RunnableSequence = mapping_prompt | llm | parser

def get_system_prompt() -> str:
    """Get the mapping system prompt for external use (e.g., tracking)"""
    return mapping_system

def get_user_prompt() -> str:
    """Get the user template for external use (e.g., tracking)"""
    return user_template
