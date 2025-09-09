"""OpenAI integration tools for the workflow."""

import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import config


# Initialize OpenAI client
openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

# Initialize LangChain OpenAI for use in LangGraph
def get_llm(model: Optional[str] = None, temperature: float = 0) -> ChatOpenAI:
    """Get a configured LangChain OpenAI instance."""
    return ChatOpenAI(
        model=model or config.EXTRACTION_MODEL,
        temperature=temperature,
        api_key=config.OPENAI_API_KEY
    )


def call_openai_structured(
    system_prompt: str,
    user_prompt: str,
    images_base64: Optional[List[str]] = None,
    model: Optional[str] = None,
    temperature: float = 0
) -> Dict[str, Any]:
    """Call OpenAI with structured JSON output.
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        images_base64: List of base64 encoded images (always a list, even for single image)
        model: Model to use
        temperature: Temperature setting
    
    Returns:
        Parsed JSON response
    """
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    if images_base64 and len(images_base64) > 0:
        # Always handle as list of images
        content = [{"type": "text", "text": user_prompt}]
        
        # Add each image to the content
        for i, img_b64 in enumerate(images_base64):
            if len(images_base64) > 1:
                # Only add page labels if multiple pages
                content.append({
                    "type": "text",
                    "text": f"Page {i+1}:"
                })
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_b64}"
                }
            })
        
        messages.append({
            "role": "user",
            "content": content
        })
        
        # Use vision model for images
        model = model or config.CLASSIFICATION_MODEL
    else:
        messages.append({"role": "user", "content": user_prompt})
        model = model or config.EXTRACTION_MODEL
    
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI call failed: {e}")
        return {}


def call_openai_text(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 500
) -> str:
    """Call OpenAI for text generation."""
    
    model = model or config.ASSISTANT_MODEL
    
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI text generation failed: {e}")
        return ""