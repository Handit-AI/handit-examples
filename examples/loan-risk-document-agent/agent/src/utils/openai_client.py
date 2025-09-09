"""OpenAI client wrapper with retry logic and structured outputs."""

import json
import time
from typing import Dict, Any, Optional, Type, List
from pydantic import BaseModel
import openai
from openai import OpenAI

from src.config import config


class OpenAIClient:
    """OpenAI client with retry logic and structured output support."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.max_retries = 2
        self.retry_delay = 1.0
    
    def classify_document(
        self,
        content: str,
        image_base64: Optional[str] = None,
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Classify a document using GPT-4 vision or text.
        
        Args:
            content: Text content or description
            image_base64: Base64 encoded image (optional)
            confidence_threshold: Minimum confidence for classification
        
        Returns:
            Dict with "label" and "confidence"
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a document classification expert. Classify the document as one of: "
                    "ID (government ID, passport, driver license), "
                    "PAYSLIP (pay stub, salary slip), "
                    "BANK_STATEMENT (bank statement, account statement), "
                    "or OTHER. "
                    "Return JSON with 'label' and 'confidence' (0-1)."
                )
            }
        ]
        
        if image_base64:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Classify this document:"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            })
            model = config.CLASSIFICATION_MODEL
        else:
            messages.append({
                "role": "user",
                "content": f"Classify this document based on its content:\n\n{content[:2000]}"
            })
            model = config.CLASSIFICATION_MODEL
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # Validate result
                if "label" in result and "confidence" in result:
                    return result
                else:
                    raise ValueError("Invalid classification result format")
                    
            except Exception as e:
                print(f"Classification attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    return {"label": "OTHER", "confidence": 0.0}
        
        return {"label": "OTHER", "confidence": 0.0}
    
    def extract_structured(
        self,
        content: str,
        schema: Type[BaseModel],
        additional_instructions: str = ""
    ) -> Optional[BaseModel]:
        """Extract structured data from content using a Pydantic schema.
        
        Args:
            content: Text content to extract from
            schema: Pydantic model class defining the structure
            additional_instructions: Extra instructions for extraction
        
        Returns:
            Instance of the schema or None if extraction fails
        """
        schema_json = schema.model_json_schema()
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a data extraction expert. Extract information from documents "
                    "and return it in the exact JSON format specified. "
                    "Only include fields you can extract with confidence. "
                    "Use null for missing optional fields. "
                    f"{additional_instructions}"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Extract data from this document according to the schema:\n\n"
                    f"Schema: {json.dumps(schema_json, indent=2)}\n\n"
                    f"Document content:\n{content[:4000]}"
                )
            }
        ]
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=config.EXTRACTION_MODEL,
                    messages=messages,
                    temperature=0,
                    response_format={"type": "json_object"}
                )
                
                result_json = json.loads(response.choices[0].message.content)
                
                # Parse into Pydantic model
                return schema(**result_json)
                
            except Exception as e:
                print(f"Extraction attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    # Add retry instruction
                    messages.append({
                        "role": "system",
                        "content": f"Previous attempt failed with error: {e}. Please ensure the output exactly matches the JSON schema."
                    })
                else:
                    return None
        
        return None
    
    def generate_assistant_reply(
        self,
        user_message: str,
        assessment: Dict[str, Any],
        max_length: int = 200
    ) -> str:
        """Generate a friendly assistant reply based on the assessment.
        
        Args:
            user_message: The user's last message
            assessment: The risk assessment results
            max_length: Maximum response length in characters
        
        Returns:
            Assistant message string
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful loan assessment assistant. "
                    "Based on the risk assessment, provide a brief, friendly response. "
                    "Focus on: 1) The risk tier, 2) Top 1-2 issues found, 3) Clear next steps. "
                    "Be concise (2-4 sentences). Do not provide legal or financial advice. "
                    "If documents are missing, specifically request them."
                )
            },
            {
                "role": "user",
                "content": (
                    f"User's message: {user_message}\n\n"
                    f"Assessment results:\n"
                    f"- Risk tier: {assessment.get('risk_tier', 'UNKNOWN')}\n"
                    f"- Risk score: {assessment.get('risk_score', 0)}\n"
                    f"- Top reasons: {', '.join(assessment.get('reasons', [])[:3])}\n"
                    f"- Documents provided: {list(assessment.get('doc_types', {}).values())}\n\n"
                    "Generate a helpful response:"
                )
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=config.ASSISTANT_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=100
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Ensure response isn't too long
            if len(reply) > max_length:
                reply = reply[:max_length-3] + "..."
            
            return reply
            
        except Exception as e:
            print(f"Failed to generate assistant reply: {e}")
            return "I've completed the risk assessment. Please review the detailed results above."
    
    def categorize_transaction_batch(
        self,
        transactions: List[str],
        categories: List[str]
    ) -> List[str]:
        """Categorize a batch of transaction descriptions.
        
        Args:
            transactions: List of transaction descriptions
            categories: List of allowed categories
        
        Returns:
            List of categories corresponding to each transaction
        """
        if not transactions:
            return []
        
        messages = [
            {
                "role": "system",
                "content": (
                    f"Categorize each transaction into one of these categories: {', '.join(categories)}. "
                    "Return a JSON array with one category per transaction, in the same order."
                )
            },
            {
                "role": "user",
                "content": (
                    "Categorize these transactions:\n" +
                    "\n".join(f"{i+1}. {t}" for i, t in enumerate(transactions[:50]))
                )
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=config.CLASSIFICATION_MODEL,
                messages=messages,
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Extract categories array from various possible formats
            if isinstance(result, list):
                return result[:len(transactions)]
            elif "categories" in result:
                return result["categories"][:len(transactions)]
            else:
                return ["other"] * len(transactions)
                
        except Exception as e:
            print(f"Failed to categorize transactions: {e}")
            return ["other"] * len(transactions)


# Global client instance
openai_client = OpenAIClient()