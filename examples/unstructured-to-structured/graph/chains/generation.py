from __future__ import annotations

import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import logging


# Ensure environment variables (.env) are loaded before LLM init
load_dotenv()

# Initialize LLM (temperature 0 for deterministic CSV formatting)
llm = ChatOpenAI(temperature=0, model=os.getenv("OPENAI_MODEL","gpt-4o-mini"))
logger = logging.getLogger("graph.generation")
logger.info("🤖 Using model: %s", getattr(llm, "model_name", "<unknown>"))


# Robust system prompt to convert multiple JSON records into a single CSV
system_prompt = """
You are a precise data transformation engine. Your task is to read multiple arbitrary JSON records and output a SINGLE CSV that aggregates the data across all records.

STRICT RULES:
- Output ONLY the CSV text. No explanations, no markdown, no code fences.
- Use comma (,) as the separator. Quote fields with commas, newlines, or quotes using standard CSV escaping (double quotes, and escape internal quotes by doubling them).

COLUMN MAPPING STRATEGY:
1. FIRST, analyze ALL records to identify semantic similarities between fields
2. Group similar fields under unified column names:
   - "items", "productos", "products" → "items"
   - "total", "suma_total", "amount" → "total"
   - "date", "fecha", "issue_date" → "date"
   - "invoice_number", "factura_num", "bill_no" → "invoice_number"
   - "customer", "cliente", "bill_to" → "customer"
   - "subtotal", "subtotal", "base_amount" → "subtotal"
   - "tax", "impuesto", "tax_amount" → "tax"
   - "discount", "descuento", "discount_amount" → "discount"
3. Always include these base columns: filename, session_id
4. Add semantic columns based on the unified mapping above
5. For arrays/lists: create summary columns (items_count, items_summary)

COLUMN GENERATION PROCESS:
1. Scan all records to find field names and their semantic meanings
2. Create a mapping of similar fields to unified column names
3. Generate the CSV header with unified column names
4. For each record, map its fields to the unified columns
5. If a field doesn't exist in a record, leave it empty

OUTPUT FORMAT:
- Header row with unified column names
- One data row per input record
- Empty fields for missing data (don't invent values)
- Consistent column alignment across all rows

EXAMPLE MAPPING:
- Record 1 has "items": [{{"name": "Product A", "qty": 2}}] → maps to "items" column
- Record 2 has "productos": [{{"nombre": "Product B", "cantidad": 1}}] → maps to "items" column
- Both get items_count=1 and items_summary="Product A|2;Product B|1"

GOAL:
- Produce a clean CSV with unified columns that semantically group similar data across different records.
- Ensure all rows have the same columns in the same order.
- Map similar fields intelligently to create a consistent structure.
"""


# Build prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        (
            "human",
            "Build a CSV from these JSON records.\n\nFilenames: {filenames}\n\nJSON Records:\n{records_text}",
        ),
    ]
)


# Final chain: prompt -> llm -> parse to raw string
generation_chain = prompt | llm | StrOutputParser()

# Add logging wrapper to see what LLM returns
def logged_generation_chain(inputs):
    logger.info("🚀 Sending to LLM: filenames=%s, records_text_len=%d", 
                inputs.get("filenames", ""), len(inputs.get("records_text", "")))
    result = generation_chain.invoke(inputs)
    logger.info("🤖 Raw LLM output: %s", repr(result))
    return result



