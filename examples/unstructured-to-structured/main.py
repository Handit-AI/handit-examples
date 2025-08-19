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
from services.handit_service import tracker

load_dotenv()

# Configure logging with emojis
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
    # Startup
    logger.info("🎉 Application starting up...")
    logger.info("🔧 CORS middleware configured")
    logger.info("📡 API endpoints registered")
    
    yield
    
    # Shutdown
    logger.info("🛑 Application shutting down...")
    logger.info("👋 Goodbye!")

app = FastAPI(
    title="Unstructured to Structured API",
    description="API for converting unstructured data to structured format",
    version="1.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with emojis"""
    start_time = time.time()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url.path} - Request started")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(f"📤 {request.method} {request.url.path} - Response sent (Status: {response.status_code}) in {process_time:.3f}s")
    
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://localhost",
        "https://localhost:3000",
        "https://localhost:8000",
        "https://127.0.0.1",
        "https://127.0.0.1:3000",
        "https://127.0.0.1:8000",
        # Add other domains as needed
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# No need for Pydantic model since we're handling files directly

class BulkProcessingResponse(BaseModel):
    message: str
    status: str
    processed_count: int
    session_id: str = ""
    saved_files: List[str] = []

@app.get("/health")
async def health_check():
    """Health check endpoint"""
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
async def bulk_unstructured_to_structured(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """Document upload endpoint - saves actual files to session directory"""
    logger.info(f"🚀 File upload requested for session: {session_id}")
    logger.info(f"📄 Uploading {len(files)} files")

    # Start tracing with Handit.ai
    
    agent_name = "unstructured_to_structured_data" # Set agent name for tracing, this is the name of your application
    tracing_response = tracker.start_tracing(agent_name=agent_name)
    execution_id = tracing_response.get("executionId") # Get execution id for tracing

    logger.info(f"✅ Handit.ai Tracing running correctly with execution_id: {execution_id}")
    
    try:
        # Create session directory
        session_dir = Path(f"assets/outputs/{session_id}/unstructured")
        session_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Created session directory: {session_dir}")
        
        saved_files = []
        unstructured_paths = []
        
        for i, file in enumerate(files):
            try:
                # Get file content
                content = await file.read()
                
                # Create filename with original extension
                original_filename = file.filename
                if not original_filename:
                    original_filename = f"document_{i+1}"
                
                file_path = session_dir / original_filename
                
                # Save file content (binary for images, text for others)
                if original_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf')):
                    # Binary files
                    with open(file_path, "wb") as f:
                        f.write(content)
                else:
                    # Text files
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content.decode('utf-8'))
                
                saved_files.append(original_filename)
                # Add full path to unstructured_paths for LangGraph
                unstructured_paths.append(str(file_path))
                logger.info(f"💾 Saved file: {original_filename}")
                
            except Exception as e:
                logger.error(f"❌ Error saving file {i+1}: {str(e)}")
                 # End tracing
                tracker.end_tracing(execution_id=execution_id, agent_name= agent_name) # When the workflow has finished, end tracing

        # Invoke LangGraph with full file paths
        graph_result = langgraph_app.invoke(input={"session_id": session_id, "unstructured_paths": unstructured_paths, "agent_name": agent_name, "execution_id": execution_id})        
        
        # Update response message
        response = BulkProcessingResponse(
            message=f"Hola! Successfully saved {len(saved_files)} files to session {session_id}",
            status="success",
            processed_count=len(saved_files),
            session_id=session_id,
            saved_files=saved_files,
            classification_results=graph_result
        )
        
        logger.info(f"✨ File upload completed successfully - {len(saved_files)} files saved to {session_dir}")

        # End tracing
        tracker.end_tracing(execution_id=execution_id, agent_name=agent_name) # When the workflow has finished, end tracing

        return response
        
    except Exception as e:
        logger.error(f"💥 Error in file upload: {str(e)}")
        # End tracing
        tracker.end_tracing(execution_id=execution_id, agent_name=agent_name) # When the workflow has finished, end tracing

        return BulkProcessingResponse(
            message=f"Error uploading files: {str(e)}",
            status="error",
            processed_count=0,
            session_id=session_id,
            saved_files=[]
        )

@app.get("/")
async def root():
    """Root endpoint"""
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
    logger.info("🚀 Starting Unstructured to Structured API server...")
    logger.info("🌐 Server will be available at http://localhost:8000")
    logger.info("📚 API documentation available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
