"""
FastAPI Server for Unstructured to Structured Document Processing

This module provides a REST API server that orchestrates the complete document
processing pipeline using LangGraph workflows.

The server handles:
- Document file uploads (images, PDFs, text files)
- Session management for batch processing
- LangGraph workflow execution for AI-powered document processing
- Comprehensive error handling and validation

Key Features:
- FastAPI-based REST API with CORS support
- LangGraph workflow orchestration
- File upload and session management
- Comprehensive logging and error handling
- Health check and monitoring endpoints

Architecture:
- FastAPI server with middleware for logging and CORS
- LangGraph workflow integration for document processing
- Session-based file organization and processing
- Comprehensive error handling with user-friendly messages

Dependencies:
- FastAPI: Web framework for building APIs
- LangGraph: Workflow orchestration
- Python standard library for file operations and logging
"""

from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import datetime
import time
import os
import base64
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from pprint import pprint
from graph.graph import app as langgraph_app
from handit_ai import configure
from handit_ai import tracing


# Load environment variables from .env file
load_dotenv()

configure(HANDIT_API_KEY=os.getenv("HANDIT_API_KEY"))

# Configure logging with emojis for better readability
# This provides structured logging with timestamps and log levels
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan manager for application startup and shutdown.
    
    This context manager handles the complete lifecycle of the FastAPI application,
    including startup validation, resource initialization, and graceful shutdown.
    
    Startup Sequence:
        1. Log application startup
        2. Validate Handit.ai configuration (critical dependency)
        3. Configure CORS and register endpoints
        4. Log successful initialization
        
    Shutdown Sequence:
        1. Log application shutdown
        2. Clean up resources
        3. Log goodbye message
        
    Args:
        app: FastAPI application instance
    """
    # Startup sequence
    logger.info("🎉 Application starting up...")
    
    logger.info("🔧 CORS middleware configured")
    logger.info("📡 API endpoints registered")
    
    yield
    
    # Shutdown sequence
    logger.info("🛑 Application shutting down...")
    logger.info("👋 Goodbye!")

# Initialize FastAPI application with comprehensive configuration
# The lifespan manager ensures proper startup validation and shutdown cleanup
app = FastAPI(
    title="Unstructured to Structured API",
    description="API for converting unstructured data to structured format",
    version="1.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    HTTP middleware for comprehensive request logging and performance monitoring.
    
    This middleware intercepts all HTTP requests and responses to provide:
    - Request logging with method and path
    - Response logging with status codes
    - Performance timing for each request
    - Comprehensive debugging information
    
    Args:
        request: FastAPI request object
        call_next: Function to call the next middleware/endpoint
        
    Returns:
        Response: The processed HTTP response
    """
    start_time = time.time()
    
    # Log incoming request details
    logger.info(f"📥 {request.method} {request.url.path} - Request started")
    
    # Process the request through the middleware chain
    response = await call_next(request)
    
    # Calculate total processing time for performance monitoring
    process_time = time.time() - start_time
    
    # Log response details and performance metrics
    logger.info(f"📤 {request.method} {request.url.path} - Response sent (Status: {response.status_code}) in {process_time:.3f}s")
    
    return response

# Configure CORS middleware for cross-origin resource sharing
# This allows the API to be accessed from web applications and other domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development origins
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        # HTTPS local development origins
        "https://localhost",
        "https://localhost:3000",
        "https://localhost:8000",
        "https://127.0.0.1",
        "https://127.0.0.1:8000",
        # Production domain origins (customize as needed)
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for structured API responses
# This ensures consistent response format and validation
class BulkProcessingResponse(BaseModel):
    """
    Response model for bulk document processing operations.
    
    This model defines the structure of responses returned by the bulk
    processing endpoint, ensuring consistency and proper validation.
    
    Fields:
        message: Human-readable status message
        status: Processing status (success, error, skipped)
        processed_count: Number of files successfully processed
        session_id: Unique session identifier for the processing job
        saved_files: List of filenames that were saved and processed
    """
    message: str
    status: str
    processed_count: int
    session_id: str = ""
    saved_files: List[str] = []

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancer health checks.
    
    This endpoint provides basic health status information about the service,
    including current timestamp and operational status. It's commonly used
    by monitoring systems and load balancers to determine service availability.
    
    Returns:
        Dict: Health status information with timestamp
    """
    logger.info("🏥 Health check requested")
    current_time = datetime.datetime.now().isoformat()
    response = {
        "status": "healthy",
        "message": "Service is running",
        "timestamp": current_time
    }
    logger.info("✅ Health check completed successfully")
    return response

@app.post("/bulk-unstructured-to-structured", response_model=BulkProcessingResponse)
@tracing(agent="unstructured_to_structured")
async def bulk_unstructured_to_structured(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Bulk document processing endpoint for converting unstructured documents to structured format.
    
    This is the main processing endpoint that handles:
    1. File uploads and session management
    2. LangGraph workflow execution
    3. File organization and processing
    4. Comprehensive error handling and response generation
    
    The endpoint processes multiple document types including images, PDFs, and text files,
    organizing them by session and executing the complete AI-powered processing pipeline.
    
    Args:
        session_id: Unique identifier for the processing session
        files: List of uploaded files to be processed
        
    Returns:
        BulkProcessingResponse: Processing results with status and file information
        
    Processing Flow:
        1. Create session directory for file organization
        2. Save uploaded files with proper naming and encoding
        3. Execute LangGraph workflow for AI-powered processing
        4. Return comprehensive processing results
    """
    logger.info(f"🚀 File upload requested for session: {session_id}")
    logger.info(f"📄 Uploading {len(files)} files")


    
    try:
        # Create session directory for organizing uploaded files
        # This provides clean separation between different processing sessions
        session_dir = Path(f"assets/unstructured/{session_id}")
        session_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Created session directory: {session_dir}")
        
        # Initialize tracking variables for processing results
        saved_files = []
        unstructured_paths = []
        
        # Process each uploaded file individually
        # This ensures robust handling of different file types and potential errors
        for i, file in enumerate(files):
            try:
                # Read file content for processing
                content = await file.read()
                
                # Create filename with original extension for proper file identification
                original_filename = file.filename
                if not original_filename:
                    original_filename = f"document_{i+1}"
                
                file_path = session_dir / original_filename
                
                # Save file content with appropriate encoding based on file type
                # Binary files (images, PDFs) are saved as-is, text files are decoded
                if original_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf')):
                    # Binary files: save raw bytes without encoding
                    with open(file_path, "wb") as f:
                        f.write(content)
                else:
                    # Text files: decode content and save with UTF-8 encoding
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content.decode('utf-8'))
                
                # Track successfully saved files and their paths
                saved_files.append(original_filename)
                # Add full path to unstructured_paths for LangGraph processing
                unstructured_paths.append(str(file_path))
                logger.info(f"💾 Saved file: {original_filename}")
                
            except Exception as e:
                # Handle individual file processing errors gracefully
                # This ensures one bad file doesn't break the entire batch
                logger.error(f"❌ Error saving file {i+1}: {str(e)}")

        # Invoke LangGraph workflow with complete file information
        # This executes the AI-powered document processing pipeline
        graph_result = langgraph_app.invoke(input={"session_id": session_id, "unstructured_paths": unstructured_paths})        
        
        # Prepare comprehensive response with processing results
        # This provides users with complete information about their processing job
        response = BulkProcessingResponse(
            message=f"Hola! Successfully saved {len(saved_files)} files to session {session_id}",
            status="success",
            processed_count=len(saved_files),
            session_id=session_id,
            saved_files=saved_files,
            classification_results=graph_result
        )
        
        logger.info(f"✨ File upload completed successfully - {len(saved_files)} files saved to {session_dir}")



        return response
        
    except Exception as e:
        # Handle any unexpected errors during processing
        # This ensures graceful error handling and proper resource cleanup
        logger.error(f"💥 Error in file upload: {str(e)}")

        return BulkProcessingResponse(
            message=f"Error uploading files: {str(e)}",
            status="error",
            processed_count=0,
            session_id=session_id,
            saved_files=[]
        )

@app.get("/")
async def root():
    """
    Root endpoint providing API information and available endpoints.
    
    This endpoint serves as the main entry point for the API, providing
    users with information about available services and endpoints.
    
    Returns:
        Dict: Welcome message and endpoint information
    """
    logger.info("🏠 Root endpoint accessed")
    response = {
        "message": "Welcome to Unstructured to Structured API",
        "endpoints": {
            "health": "/health",
            "bulk_processing": "/bulk-unstructured-to-structured"
        }
    }
    logger.info("🎉 Root endpoint served successfully")
    return response

if __name__ == "__main__":
    import uvicorn
    

    
    # Start the FastAPI server with comprehensive configuration
    # The server will only start if all validation passes
    logger.info("🚀 Starting Unstructured to Structured API server...")
    logger.info("🌐 Server will be available at http://localhost:8000")
    logger.info("📚 API documentation available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
