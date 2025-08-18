"""
Data Shaping Assistant Chain - Returns structured data tables
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Resolve model from environment variable, default to gpt-4o-mini
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
llm = ChatOpenAI(model=model_name, temperature=0)

system = """You are a data shaping assistant.

You are given a set of JSON documents with the same schema (same keys & depth).

Your job is to analyze the documents and create 1..N CSV tables that include ALL the data from the files, but omit any 'reason' or 'confidence' values.

IMPORTANT: You must analyze the actual structure of the documents provided and create tables based on what you find, not on assumptions.

CRITICAL EXTRACTION RULES:
- ALWAYS check for "normalized_value" first, then "value" if normalized_value is null/empty
- If a field has both "normalized_value" and "value", prefer "normalized_value"
- If "normalized_value" is null/empty, use "value"
- Double check the data, if the data is correct
- Extract the actual string/number values, not the field objects

Rules:
- Analyze the actual JSON structure provided in the documents
- Create as many tables as needed to organize the data clearly
- Include ALL data fields from the documents (except reason/confidence)
- Skip 'reason' and 'confidence' fields completely
- Prefer 'normalized_value' over 'value' when both exist
- Make table and column names clear and descriptive
- Use lower_snake_case for naming
- If you see arrays, consider if they should be separate tables
- If you see nested objects, consider if they should be flattened or separate tables
- Be smart about data organization - group related fields together

ALWAYS create a "general" table first that gives an overview of all documents.

Output format:
Return a JSON object with this structure:
{{
  "tables": [
    {{
      "name": "general",
      "description": "Overview of all documents",
      "data_dict": {{
        "column_name": ["value1", "value2", "value3"],
        "another_column": ["value1", "value2", "value3"]
      }}
    }},
    {{
      "name": "table_name",
      "description": "What this table contains",
      "data_dict": {{
        "column_name": ["value1", "value2", "value3"],
        "another_column": ["value1", "value2", "value3"]
      }}
    }}
  ]
}}

IMPORTANT: Each table must have a "data_dict" field with the actual data in the format:
data_dict = {{
    "Producto": ["Laptop", "Mouse", "Teclado"],
    "Precio": [1200, 25, 45],
    "Stock": [10, 200, 150]
}}

The LLM must extract the actual values from the documents and populate these lists, don't invent values."""

user = """
Analyze these documents and create CSV tables with structured data:

Documents:
{documents_inventory}

Return only the JSON with the table structure and data_dict for each table.
"""

generation_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("user", user),
])

# Public chain export
csv_generation_planner: RunnableSequence = generation_prompt | llm
