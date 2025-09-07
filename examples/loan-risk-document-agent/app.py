"""Flask API for the loan risk document agent."""

import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from src.config import config
from src.risk_analysis_workflow.workflow import run_workflow
from src.schemas import ChatResponse, Assessment
from handit_ai import configure, tracing

# Validate config on startup
config.validate()

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE_BYTES * config.MAX_FILES_PER_REQUEST


configure(HANDIT_API_KEY=os.getenv("HANDIT_API_KEY"))  # Get API key from https://dashboard.handit.ai/settings/integrations

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "loan-risk-agent"}), 200


@app.route('/v1/chat/messages', methods=['POST'])
@tracing(agent="process loan applications")
def process_loan_application():
    """Main endpoint for processing loan applications.
    
    Accepts multipart form data with:
    - messages: JSON array of chat messages
    - files[]: Binary files (PDFs, images, CSVs)
    - options: Optional JSON configuration
    """
    try:
        # Parse messages
        messages_json = request.form.get('messages', '[]')
        try:
            messages = json.loads(messages_json)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid messages JSON format"}), 400
        
        # Parse options
        options_json = request.form.get('options', '{}')
        try:
            options = json.loads(options_json)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid options JSON format"}), 400
        
        # Process files
        files_data = []
        if 'files' in request.files:
            files_list = request.files.getlist('files')
            
            # Check file count
            if len(files_list) > config.MAX_FILES_PER_REQUEST:
                return jsonify({
                    "error": f"Too many files. Maximum {config.MAX_FILES_PER_REQUEST} allowed"
                }), 413
            
            for file in files_list:
                if file and allowed_file(file.filename):
                    # Read file content
                    file_content = file.read()
                    
                    # Check file size
                    if len(file_content) > config.MAX_FILE_SIZE_BYTES:
                        return jsonify({
                            "error": f"File {file.filename} exceeds maximum size of {config.MAX_FILE_SIZE_MB}MB"
                        }), 413
                    
                    # Get file extension
                    file_ext = file.filename.rsplit('.', 1)[1].lower()
                    
                    files_data.append({
                        "content": file_content,
                        "type": file_ext,
                        "name": secure_filename(file.filename)
                    })
                else:
                    return jsonify({
                        "error": f"Invalid file type: {file.filename}"
                    }), 415
        
        # Check if we have at least one file
        if not files_data:
            return jsonify({
                "error": "At least one document must be provided"
            }), 400
        
        print(f"\nProcessing request with {len(files_data)} files and {len(messages)} messages")
        
        # Run the workflow
        result = run_workflow(
            files=files_data,
            messages=messages,
            options=options
        )
        
        # Prepare response - just pass through the data
        assessment = Assessment(
            risk_score=result.get("risk_score", 0),
            risk_tier=result.get("risk_tier", "INVALID"),
            reasons=result.get("reasons", []),
            checks=result.get("checks", []),
            doc_types=result.get("doc_types", {}),
            extracted=result.get("extracted_data"),
            profile=result.get("identity_profile")
        )
        
        response = ChatResponse(
            assistant_message=result.get("assistant_message", "Assessment complete."),
            assessment=assessment
        )
        
        return jsonify(response.model_dump()), 200
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e) if app.debug else None
        }), 500


@app.route('/v1/documents/classify', methods=['POST'])
def classify_document():
    """Endpoint for classifying a single document."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 415
        
        # Read file
        file_content = file.read()
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        
        # Import classifier agent
        from src.risk_analysis_workflow.agents.classifier.agent import ClassifierAgent
        
        # Classify document
        agent = ClassifierAgent()
        result = agent.classify_document({
            "content": file_content,
            "type": file_ext,
            "name": file.filename
        })
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error classifying document: {str(e)}")
        return jsonify({"error": "Classification failed"}), 500


if __name__ == '__main__':
    print(f"""
╔════════════════════════════════════════════════╗
║     LOAN RISK DOCUMENT AGENT                  ║
║     AI-Powered Document Analysis              ║
╚════════════════════════════════════════════════╝

Starting server on port {config.PORT}...
API endpoint: http://localhost:{config.PORT}/v1/chat/messages

Configuration:
- Max file size: {config.MAX_FILE_SIZE_MB}MB
- Max files per request: {config.MAX_FILES_PER_REQUEST}
- Allowed formats: {', '.join(config.ALLOWED_EXTENSIONS)}
    """)
    
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.FLASK_DEBUG
    )