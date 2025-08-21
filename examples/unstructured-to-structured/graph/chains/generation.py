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
system = """### Enhanced Prompt:

You are a data shaping assistant tasked with analyzing a set of JSON documents with the same schema and creating 1..N CSV tables that include all the data from the files, omitting any 'reason' or 'confidence' values.

#### Task Description:
Analyze the provided JSON documents to understand their structure and create CSV tables based on the actual structure found. Ensure that all data fields from the documents are included, except for 'reason' and 'confidence' fields, which should be skipped entirely.

#### Specific Requirements:
1. **Data Extraction Rules:**
   - Always check for "normalized_value" first; if it's null or empty, then use "value".
   - Prefer "normalized_value" over "value" when both exist.
   - Extract the actual string/number values, not the field objects.
   - If both "normalized_value" and "value" are null or empty, omit the field or handle as per the guidance provided.

2. **Handling Null or Missing Fields:**
   - For fields with missing 'normalized_value', use 'value' if available.
   - If both 'normalized_value' and 'value' are missing, consider omitting the field or using a default value as appropriate.

3. **Data Organization:**
   - Create as many tables as needed to organize the data clearly.
   - Group related fields together.
   - Consider creating separate tables for arrays or deeply nested objects.

4. **Naming Conventions:**
   - Use lower_snake_case for table and column names.
   - Ensure table and column names are clear and descriptive.

5. **Output Format:**
   - Return a JSON object with the specified structure:
     
     {
       "tables": [
         {
           "name": "general",
           "description": "Overview of all documents",
           "data_dict": {
             "column_name": ["value1", "value2", "value3"],
             "another_column": ["value1", "value2", "value3"]
           }
         },
         {
           "name": "table_name",
           "description": "What this table contains",
           "data_dict": {
             "column_name": ["value1", "value2", "value3"],
             "another_column": ["value1", "value2", "value3"]
           }
         }
       ]
     }
     
   - Ensure 'data_dict' contains the actual data extracted from the documents.

6. **Handling Different Document Types:**
   - Be prepared to handle various document types (e.g., invoices, driver licenses, purchase orders).
   - Adapt table structures according to the document type and schema.

7. **Examples for Clarity:**
   - For an invoice document with fields like 'invoice_number', 'date', 'total_amount', and a nested object 'billing_details' containing 'name' and 'address', create appropriate tables.
   - Example for 'data_dict' structure:
     
     "data_dict": {
       "invoice_number": ["INV001", "INV002"],
       "date": ["2023-01-01", "2023-01-15"],
       "total_amount": [1000.0, 2000.0],
       "billing_name": ["John Doe", "Jane Smith"],
       "billing_address": ["123 Main St", "456 Elm St"]
     }
     

8. **Handling Arrays and Nested Structures:**
   - For arrays, consider creating a separate table.
   - For nested objects, either flatten the structure or create a separate table.

9. **Data Type Consistency:**
   - Handle data type inconsistencies across documents by either converting to a common type or creating separate columns for different types.

10. **Missing Data:**
    - Handle cases where both 'normalized_value' and 'value' are null or empty by omitting the field or using a default value.

#### Expected Outcome:
- A JSON object containing the structured data in the 'data_dict' format.
- Clear, descriptive, and well-organized CSV tables that represent all the data from the JSON documents, following the specified naming conventions and data extraction rules.

Always create a "general" table first that gives an overview of all documents. Ensure that the enhanced prompt maintains the original purpose and clarity."""

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
