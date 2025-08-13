"""
Handit.ai service initialization and configuration.
"""
import os
from dotenv import load_dotenv
from handit import HanditTracker

load_dotenv()

# Create a singleton tracker instance
tracker = HanditTracker()
tracker.config(api_key=os.getenv("HANDIT_API_KEY"))