from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Resolve model from environment variable, default to gpt-4o-mini
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
llm = ChatOpenAI(model=model_name, temperature=0)


class ColumnSpec(BaseModel):
    name: str = Field(description="Column name to appear in the CSV (lower_snake_case)")
    value_path: str = Field(
        description="Dot path to the field in the JSON. For arrays, reference current item with '.' prefix, e.g., '.description.value' or '.price.normalized_value'"
    )
    prefer_normalized: bool = Field(
        default=True, description="If true, prefer normalized_value when available; fallback to value"
    )
    description: Optional[str] = Field(default=None, description="Brief explanation for what the column represents")


class TableSpec(BaseModel):
    name: str = Field(description="CSV/table file name without extension (lower_snake_case)")
    row_scope: str = Field(
        description="Either 'per_document' or 'per_array'. If 'per_array', specify array_path"
    )
    array_path: Optional[str] = Field(
        default=None, description="When row_scope is 'per_array', dot path to array (e.g., 'line_items')"
    )
    columns: List[ColumnSpec] = Field(description="Columns to include in the table")
    rationale: Optional[str] = Field(default=None, description="Reasoning for this table design")


class CsvPlan(BaseModel):
    tables: List[TableSpec] = Field(description="List of tables to generate")
    rationale: Optional[str] = Field(default=None, description="High-level plan reasoning")


# Parsing the answer
structured_plan = llm.with_structured_output(CsvPlan)

system = """
You are a data modeling expert. Analyze a set of structured JSON documents (roots can vary; do not assume fixed top-level keys). Design CSV tables to present all available data clearly.

Requirements:
- Always include a primary table named 'general' with row_scope='per_document'. Map as many scalar fields as possible per document into this table (non-arrays). Arrays should be handled in additional tables.
- Add as many extra tables as needed for readability (e.g., per_array tables for repeated elements) so that all data across documents is visible and well organized.
- For every cell: prefer normalized_value when present; otherwise use value; if neither exists or is null, leave the cell empty. Never include 'reason' or 'confidence'. Never place objects/arrays in a cell.
- Use lower_snake_case for table and column names.
- For per_array tables, create one row per array element. When referencing fields of the current item, use '.field.subfield' and target scalar subfields such as '.amount.normalized_value'.

Output:
- Return JSON matching the CsvPlan schema. For each TableSpec: set name, row_scope, optional array_path, and columns where each column has name, value_path, prefer_normalized.
- value_path must reference a scalar location (e.g., '*.normalized_value' or '*.value').
- array_path must be the dot path of the array (omit '[]' from the path).
"""

user = """
You will receive an inventory of documents that lists flattened field paths and sample values/types for all provided structured_json_paths. Use only this inventory to decide paths; do not assume fixed roots.

Goals:
- Design a set of tables that makes all document data visible and well organized.
- Always include a 'general' per_document table and add any extra tables you deem useful (especially per_array tables) to cover arrays and improve readability.
- For each field, use normalized_value if present; else value; if both are missing/null, the cell should be empty. Never include reason or confidence.
- Ensure every field path appears in at least one table.

Inventory:
{documents_inventory}
"""

generation_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("user", user),
    ]
)

# Public chain export
csv_generation_planner: RunnableSequence = generation_prompt | structured_plan
