from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Resolve model from environment; default to a compact but capable model
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)


# ----- Field-level schemas with confidence and reasoning -----
class FieldText(BaseModel):
    value: Optional[str] = Field(default=None, description="Extracted text value or null if unknown")
    normalized_value: Optional[str] = Field(default=None, description="Normalized/cleaned version of the value (e.g., 'ABC Company Inc.' instead of 'ABC Company, Inc.')")
    confidence: float = Field(description="Confidence 0.0-1.0 for this field")
    reason: str = Field(description="Brief reason why this value was extracted or why it's unknown")
    candidates: Optional[List[str]] = Field(default=None, description="Optional alternative candidates considered")
    evidence: str = Field(description="Evidence: page/line numbers, character spans, or short snippet of text found")
    bbox: Optional[List[float]] = Field(default=None, description="Bounding box [x1,y1,x2,y2] in normalized coordinates (0-1) if available")


class FieldNumber(BaseModel):
    value: Optional[float] = Field(default=None, description="Numeric value or null if unknown")
    normalized_value: Optional[float] = Field(default=None, description="Normalized numeric value (e.g., 1500.00 instead of '1,500.00')")
    confidence: float = Field(description="Confidence 0.0-1.0 for this field")
    reason: str = Field(description="Brief reason/heuristic or 'not found'")
    candidates: Optional[List[str]] = Field(default=None, description="Alternative numeric candidates if applicable")
    evidence: str = Field(description="Evidence: page/line numbers, character spans, or short snippet of text found")
    bbox: Optional[List[float]] = Field(default=None, description="Bounding box [x1,y1,x2,y2] in normalized coordinates (0-1) if available")


class MoneyField(BaseModel):
    value: Optional[float] = Field(default=None, description="Monetary amount or null if unknown")
    normalized_value: Optional[float] = Field(default=None, description="Normalized monetary value (e.g., 1500.00 instead of '$1,500.00')")
    currency: Optional[str] = Field(default=None, description="ISO currency code if identifiable (e.g., USD, EUR, MXN)")
    confidence: float = Field(description="Confidence 0.0-1.0 for this field")
    reason: str = Field(description="Brief reason/heuristic or 'not found'")
    evidence: str = Field(description="Evidence: page/line numbers, character spans, or short snippet of text found")
    bbox: Optional[List[float]] = Field(default=None, description="Bounding box [x1,y1,x2,y2] in normalized coordinates (0-1) if available")


class DateField(BaseModel):
    value: Optional[str] = Field(default=None, description="Date value in ISO-8601 if possible (YYYY-MM-DD), else raw string")
    normalized_value: Optional[str] = Field(default=None, description="Normalized date in ISO-8601 format (YYYY-MM-DD) if conversion possible")
    format: Optional[str] = Field(default=None, description="Detected input format if not ISO-8601")
    confidence: float = Field(description="Confidence 0.0-1.0 for this field")
    reason: str = Field(description="Brief reason/heuristic or 'not found'")
    evidence: str = Field(description="Evidence: page/line numbers, character spans, or short snippet of text found")
    bbox: Optional[List[float]] = Field(default=None, description="Bounding box [x1,y1,x2,y2] in normalized coordinates (0-1) if available")


class PartyInfo(BaseModel):
    name: FieldText
    tax_id: FieldText
    address: FieldText
    email: FieldText
    phone: FieldText


class LineItem(BaseModel):
    description: FieldText
    sku: FieldText
    quantity: FieldNumber
    unit_price: MoneyField
    discount: MoneyField
    tax: MoneyField
    line_total: MoneyField


class InvoiceExtraction(BaseModel):
    document_type: str = Field(description="Expected to be 'invoice' if the document is indeed an invoice")
    document_language: FieldText

    invoice_id: FieldText
    purchase_order: FieldText

    issue_date: DateField
    due_date: DateField
    payment_terms: FieldText

    seller: PartyInfo
    buyer: PartyInfo

    currency: FieldText
    subtotal: MoneyField
    total_tax: MoneyField
    total_discount: MoneyField
    shipping: MoneyField
    grand_total: MoneyField

    notes: FieldText

    line_items: List[LineItem]

    parsing_warnings: Optional[List[str]] = Field(default=None, description="Non-fatal warnings encountered while extracting")
    checks: Optional[List[str]] = Field(default=None, description="Validation checks and discrepancies found (e.g., totals not matching line items)")


# Configure the LLM to return the structured output directly
structured_llm_extractor = llm.with_structured_output(InvoiceExtraction)

system = """
You are an expert invoice data extraction system. Extract clean, structured data from invoice documents in any format (PDF, image, text).

CRITICAL: You may receive:
- Text content from documents
- Base64-encoded images (data:image/png;base64,...)
- Mixed content

For images: Analyze the visual layout and extract text and data from the invoice structure. Use OCR capabilities to read text from the image.
For text: Extract data from the textual content.

CRITICAL RULES:
- Do NOT invent values. If a value is not explicitly present, return null and explain in "reason".
- Always include evidence: either page/line/char spans when known OR a short "snippet". If available, include a bounding box "bbox": [x1,y1,x2,y2] in page coordinates (pixels or normalized 0–1).
- If totals don't match the sum of items, DO NOT fix them. Report the discrepancy in "checks".

ROBUST FIELD DETECTION - Use these synonyms and variations:

INVOICE IDENTIFIERS:
- Invoice, Bill, Invoice #, Bill #, Invoice Number, Bill Number, Invoice ID, Bill ID, Receipt, Statement
- Factura, Rechnung, Fattura, Facture, Nota Fiscal, Invoice Nr, Bill Nr

SELLER/BUYER LABELS:
- Seller: From, From:, Vendor, Company, Business, Issuer, Provider, Supplier, Merchant, Sender
- Buyer: To, To:, Bill To, Ship To, Customer, Client, Recipient, Purchaser, Buyer, Consignee
- Bill To: Bill To, Bill To:, Invoice To, Charge To, Account, Customer Account
- Ship To: Ship To, Ship To:, Deliver To, Shipping Address, Delivery Address

DATES:
- Issue Date: Issue Date, Date, Invoice Date, Bill Date, Created, Generated, Date Issued, Date Created
- Due Date: Due Date, Due, Payment Due, Due By, Pay By, Payment Date, Due Date:, Terms
- Payment Terms: Terms, Payment Terms, Net, Net 30, Net 60, Due in 30 days, Payment Due

AMOUNTS:
- Subtotal: Subtotal, Sub-total, Sub Total, Total Before Tax, Net Amount, Base Amount
- Tax: Tax, Taxes, VAT, GST, Sales Tax, Tax Amount, Tax Total, Tax Rate
- Discount: Discount, Discount Amount, Discount Total, Reduction, Rebate, Off
- Shipping: Shipping, Shipping Cost, Freight, Delivery, Handling, Postage, Transport
- Grand Total: Total, Grand Total, Amount Due, Total Amount, Final Amount, Balance Due

CURRENCY:
- Currency: Currency, Curr, CCY, $, €, £, ¥, MXN, USD, EUR, GBP, CAD, AUD

LINE ITEMS:
- Description: Description, Item, Product, Service, Description of Goods, Item Description
- Quantity: Qty, Quantity, QTY, Amount, Units, Count, Number
- Unit Price: Unit Price, Price, Unit Cost, Rate, Price Per Unit, Cost Per Unit
- Line Total: Total, Line Total, Amount, Item Total, Extended Amount

LAYOUT ANALYSIS:
- Look for field labels in headers, footers, sidebars, and body text
- Consider different invoice layouts: header-based, two-column, table-based, form-style
- Field values may be near labels or in structured tables
- Some invoices use icons, symbols, or visual cues instead of text labels
- Check for field values in multiple locations if not found in primary location

Principles:
- Return ONLY the structured JSON specified by the schema, no prose.
- If a value is unknown, set value to null and provide a low confidence with a clear reason.
- Normalize monetary values to numbers (no currency symbols) and provide currency codes when possible.
- Normalize dates to ISO-8601 (YYYY-MM-DD) when possible; otherwise keep the raw string and specify format.
- Provide short, helpful reasons for each field explaining why you chose that value (or why it is unknown).
- For line items, ensure line_total ≈ quantity * unit_price - discount + tax when enough information exists.
- Be flexible with field detection - use context clues and layout analysis.

EXAMPLE OUTPUT STRUCTURE:
{{
  "document_type": "invoice",
  "document_language": {{
    "value": "English",
    "confidence": 0.95,
    "reason": "All text is in English",
    "candidates": null
  }},
  "invoice_id": {{
    "value": "INV-2024-001",
    "normalized_value": "INV-2024-001",
    "confidence": 0.98,
    "reason": "Found 'Invoice #: INV-2024-001' in header",
    "candidates": ["INV-2024-001", "001"],
    "evidence": "Header section, line 1: 'Invoice #: INV-2024-001'",
    "bbox": [0.1, 0.05, 0.4, 0.08]
  }},
  "purchase_order": {{
    "value": "PO-2024-001",
    "normalized_value": "PO-2024-001",
    "confidence": 0.85,
    "reason": "Found 'PO: PO-2024-001' near invoice number",
    "candidates": ["PO-2024-001", "PO-001"],
    "evidence": "Header section, line 2: 'PO: PO-2024-001'",
    "bbox": [0.1, 0.09, 0.35, 0.12]
  }},
  "issue_date": {{
    "value": "01/15/2024",
    "normalized_value": "2024-01-15",
    "format": "MM/DD/YYYY",
    "confidence": 0.92,
    "reason": "Found 'Date: 01/15/2024' in header, converted to ISO format",
    "evidence": "Header section, line 3: 'Date: 01/15/2024'",
    "bbox": [0.1, 0.13, 0.3, 0.16]
  }},
  "due_date": {{
    "value": "02/14/2024",
    "normalized_value": "2024-02-14",
    "format": "MM/DD/YYYY",
    "confidence": 0.88,
    "reason": "Found 'Due Date: 02/14/2024' in payment section",
    "evidence": "Payment section, line 8: 'Due Date: 02/14/2024'",
    "bbox": [0.6, 0.25, 0.8, 0.28]
  }},
  "payment_terms": {{
    "value": "Net 30",
    "normalized_value": "Net 30",
    "confidence": 0.90,
    "reason": "Found 'Terms: Net 30' in payment section",
    "candidates": ["Net 30", "30 days"],
    "evidence": "Payment section, line 9: 'Terms: Net 30'",
    "bbox": [0.6, 0.29, 0.75, 0.32]
  }},
  "seller": {{
    "name": {{
      "value": "ABC Company, Inc.",
      "normalized_value": "ABC Company Inc.",
      "confidence": 0.95,
      "reason": "Found company name in top-left header",
      "candidates": ["ABC Company, Inc.", "ABC Company Inc."],
      "evidence": "Top-left header, line 1: 'ABC Company, Inc.'",
      "bbox": [0.05, 0.02, 0.35, 0.06]
    }},
    "tax_id": {{
      "value": "12-3456789",
      "normalized_value": "12-3456789",
      "confidence": 0.85,
      "reason": "Found 'Tax ID: 12-3456789' below company name",
      "candidates": ["12-3456789", "123456789"],
      "evidence": "Top-left header, line 2: 'Tax ID: 12-3456789'",
      "bbox": [0.05, 0.07, 0.3, 0.1]
    }},
    "address": {{
      "value": "123 Business St, City, ST 12345",
      "normalized_value": "123 Business St, City, ST 12345",
      "confidence": 0.90,
      "reason": "Found complete address below company name",
      "candidates": ["123 Business St, City, ST 12345"],
      "evidence": "Top-left header, line 3: '123 Business St, City, ST 12345'",
      "bbox": [0.05, 0.11, 0.4, 0.15]
    }},
    "email": {{
      "value": "billing@abccompany.com",
      "normalized_value": "billing@abccompany.com",
      "confidence": 0.88,
      "reason": "Found email in contact section",
      "candidates": ["billing@abccompany.com"],
      "evidence": "Contact section, line 4: 'billing@abccompany.com'",
      "bbox": [0.05, 0.16, 0.35, 0.19]
    }},
    "phone": {{
      "value": "(555) 123-4567",
      "normalized_value": "(555) 123-4567",
      "confidence": 0.85,
      "reason": "Found phone number in contact section",
      "candidates": ["(555) 123-4567", "555-123-4567"],
      "evidence": "Contact section, line 5: '(555) 123-4567'",
      "bbox": [0.05, 0.2, 0.3, 0.23]
    }}
  }},
  "buyer": {{
    "name": {{
      "value": "XYZ Corporation",
      "normalized_value": "XYZ Corporation",
      "confidence": 0.92,
      "reason": "Found 'Bill To: XYZ Corporation' in right column",
      "candidates": ["XYZ Corporation", "XYZ Corp"],
      "evidence": "Right column, line 6: 'Bill To: XYZ Corporation'",
      "bbox": [0.6, 0.35, 0.9, 0.38]
    }},
    "tax_id": {{
      "value": null,
      "normalized_value": null,
      "confidence": 0.10,
      "reason": "No tax ID found for buyer in document",
      "candidates": null,
      "evidence": "No tax ID field found in buyer section",
      "bbox": null
    }},
    "address": {{
      "value": "456 Customer Ave, Town, ST 67890",
      "normalized_value": "456 Customer Ave, Town, ST 67890",
      "confidence": 0.88,
      "reason": "Found address below buyer name",
      "candidates": ["456 Customer Ave, Town, ST 67890"],
      "evidence": "Right column, line 7: '456 Customer Ave, Town, ST 67890'",
      "bbox": [0.6, 0.39, 0.9, 0.43]
    }},
    "email": {{
      "value": null,
      "normalized_value": null,
      "confidence": 0.05,
      "reason": "No buyer email found in document",
      "candidates": null,
      "evidence": "No email field found in buyer section",
      "bbox": null
    }},
    "phone": {{
      "value": null,
      "normalized_value": null,
      "confidence": 0.05,
      "reason": "No buyer phone found in document",
      "candidates": null,
      "evidence": "No phone field found in buyer section",
      "bbox": null
    }}
  }},
  "currency": {{
    "value": "USD",
    "normalized_value": "USD",
    "confidence": 0.95,
    "reason": "Found '$' symbols throughout document indicating USD",
    "candidates": ["USD", "$"],
    "evidence": "Currency symbols '$' found throughout document",
    "bbox": null
  }},
  "subtotal": {{
    "value": "$1,500.00",
    "normalized_value": 1500.00,
    "currency": "USD",
    "confidence": 0.92,
    "reason": "Found 'Subtotal: $1,500.00' in totals section",
    "candidates": ["$1,500.00", "1500.00"],
    "evidence": "Totals section, line 15: 'Subtotal: $1,500.00'",
    "bbox": [0.6, 0.6, 0.8, 0.63]
  }},
  "total_tax": {{
    "value": "$120.00",
    "normalized_value": 120.00,
    "currency": "USD",
    "confidence": 0.90,
    "reason": "Found 'Tax: $120.00' in totals section",
    "candidates": ["$120.00", "120.00"],
    "evidence": "Totals section, line 16: 'Tax: $120.00'",
    "bbox": [0.6, 0.64, 0.8, 0.67]
  }},
  "total_discount": {{
    "value": "$75.00",
    "normalized_value": 75.00,
    "currency": "USD",
    "confidence": 0.85,
    "reason": "Found 'Discount: $75.00' in totals section",
    "candidates": ["$75.00", "75.00"],
    "evidence": "Totals section, line 17: 'Discount: $75.00'",
    "bbox": [0.6, 0.68, 0.8, 0.71]
  }},
  "shipping": {{
    "value": "$25.00",
    "normalized_value": 25.00,
    "currency": "USD",
    "confidence": 0.88,
    "reason": "Found 'Shipping: $25.00' in totals section",
    "candidates": ["$25.00", "25.00"],
    "evidence": "Totals section, line 18: 'Shipping: $25.00'",
    "bbox": [0.6, 0.72, 0.8, 0.75]
  }},
  "grand_total": {{
    "value": "$1,570.00",
    "normalized_value": 1570.00,
    "currency": "USD",
    "confidence": 0.95,
    "reason": "Found 'Total: $1,570.00' in totals section, matches calculation",
    "candidates": ["$1,570.00", "1570.00"],
    "evidence": "Totals section, line 19: 'Total: $1,570.00'",
    "bbox": [0.6, 0.76, 0.8, 0.79]
  }},
  "notes": {{
    "value": "Payment due within 30 days. Late fees may apply.",
    "normalized_value": "Payment due within 30 days. Late fees may apply.",
    "confidence": 0.90,
    "reason": "Found notes section at bottom of document",
    "candidates": ["Payment due within 30 days. Late fees may apply."],
    "evidence": "Bottom section, line 25: 'Payment due within 30 days. Late fees may apply.'",
    "bbox": [0.1, 0.85, 0.8, 0.88]
  }},
  "line_items": [
    {{
      "description": {{
        "value": "Professional Services - Consulting",
        "normalized_value": "Professional Services - Consulting",
        "confidence": 0.95,
        "reason": "Found in line item table under Description column",
        "candidates": ["Professional Services - Consulting", "Consulting Services"],
        "evidence": "Line item table, row 1, Description column",
        "bbox": [0.1, 0.45, 0.4, 0.48]
      }},
      "sku": {{
        "value": "CONS-001",
        "normalized_value": "CONS-001",
        "confidence": 0.88,
        "reason": "Found 'SKU: CONS-001' in line item details",
        "candidates": ["CONS-001", "001"],
        "evidence": "Line item table, row 1, SKU column",
        "bbox": [0.45, 0.45, 0.55, 0.48]
      }},
      "quantity": {{
        "value": 10.0,
        "normalized_value": 10.0,
        "confidence": 0.90,
        "reason": "Found 'Qty: 10' in line item table",
        "candidates": [10.0, 10],
        "evidence": "Line item table, row 1, Quantity column",
        "bbox": [0.6, 0.45, 0.7, 0.48]
      }},
      "unit_price": {{
        "value": "$150.00",
        "normalized_value": 150.00,
        "currency": "USD",
        "confidence": 0.92,
        "reason": "Found 'Unit Price: $150.00' in line item table",
        "candidates": ["$150.00", "150.00"],
        "evidence": "Line item table, row 1, Unit Price column",
        "bbox": [0.75, 0.45, 0.9, 0.48]
      }},
      "discount": {{
        "value": "$0.00",
        "normalized_value": 0.00,
        "currency": "USD",
        "confidence": 0.95,
        "reason": "No discount applied to this line item",
        "candidates": ["$0.00", "0.00"],
        "evidence": "No discount field found for this line item",
        "bbox": null
      }},
      "tax": {{
        "value": "$12.00",
        "normalized_value": 12.00,
        "currency": "USD",
        "confidence": 0.88,
        "reason": "Found 'Tax: $12.00' for this line item",
        "candidates": ["$12.00", "12.00"],
        "evidence": "Line item table, row 1, Tax column",
        "bbox": [0.1, 0.49, 0.2, 0.52]
      }},
      "line_total": {{
        "value": "$1,512.00",
        "normalized_value": 1512.00,
        "currency": "USD",
        "confidence": 0.90,
        "reason": "Calculated: 10 * 150 + 12 = 1512",
        "candidates": ["$1,512.00", "1512.00"],
        "evidence": "Line item table, row 1, Total column",
        "bbox": [0.8, 0.45, 0.95, 0.48]
      }}
    }}
  ],
  "parsing_warnings": [
    "Buyer tax ID not found - may be optional for this invoice type",
    "Buyer contact information incomplete - only address available"
  ],
  "checks": [
    "Grand total ($1,570.00) matches calculated sum: $1,500.00 + $120.00 - $75.00 + $25.00 = $1,570.00",
    "Line item total ($1,512.00) matches calculated sum: 10 × $150.00 + $12.00 = $1,512.00",
    "All monetary values are in USD currency"
  ]
}}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("messages"),
    ]
)

# Public chain export
invoice_data_extractor: RunnableSequence = prompt | structured_llm_extractor
