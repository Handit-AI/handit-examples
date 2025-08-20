"""
Data Shaping Assistant Chain for LangGraph

This module provides an AI-powered system for converting structured JSON documents
into organized CSV table formats. It analyzes document structures and creates
intelligent table organizations that preserve all data while optimizing for
readability and analysis.

The chain performs intelligent data shaping by:
- Analyzing JSON document structures to understand data organization
- Creating multiple CSV tables based on logical data groupings
- Extracting actual values while omitting metadata fields
- Prioritizing normalized values over raw values for data quality
- Organizing related fields into coherent table structures

Key Features:
- AI-powered table structure analysis and planning
- Automatic CSV table generation from JSON documents
- Intelligent data organization and grouping
- Support for nested objects and array structures
- Comprehensive data extraction with value prioritization
- Clear table naming and description generation

Use Cases:
- Converting extracted document data to analysis-ready formats
- Creating structured datasets from heterogeneous document collections
- Generating reports and dashboards from processed documents
- Data preparation for machine learning and analytics workflows
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI model from environment variable with fallback to gpt-4o-mini
# This allows easy switching between different AI models for different use cases
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
llm = ChatOpenAI(model=model_name, temperature=0)

# System prompt that defines the AI's role and behavior for data shaping
# This prompt emphasizes data analysis, value extraction, and table organization
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

# User template that provides the documents for analysis
# This template ensures consistent input format and clear output requirements
user = """
Analyze these documents and create CSV tables with structured data:

Documents:
{documents_inventory}

Return only the JSON with the table structure and data_dict for each table.
"""

# Create the complete prompt template combining system instructions and user input
# This template guides the AI through the data shaping process
generation_prompt = ChatPromptTemplate.from_messages([
    ("system", system),  # AI's role and data shaping rules
    ("user", user),      # Document input and output requirements
])

# Public chain export that processes documents and returns structured table plans
# This chain combines the prompt template with the AI model for data shaping
csv_generation_planner: RunnableSequence = generation_prompt | llm

def get_system_prompt() -> str:
    """
    Get the generation system prompt for external use (e.g., tracking, debugging, or logging).
    
    This function allows other parts of the system to access the exact
    instructions given to the AI model for data shaping operations.
    
    Returns:
        str: The complete system prompt that defines the AI's behavior for data shaping
    """
    return system

def get_user_prompt() -> str:
    """
    Get the user template for external use (e.g., tracking, debugging, or logging).
    
    This function provides access to the user-facing instructions and document
    input template used for data shaping operations.
    
    Returns:
        str: The user template that defines the input format and output requirements
    """
    return user
