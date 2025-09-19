#!/usr/bin/env python3
"""
AI Engine API Server
Provides REST API endpoints for the AI engine functionality
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import asdict
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
import tempfile

# Import our AI engine
from ai_engine import AIEngineServer, CodeRequest, Language, RequestType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI Engine API",
    description="Real AI Engine for Code Generation and Analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global AI engine instance
ai_engine = AIEngineServer()

# Pydantic models for API
class GenerateCodeRequest(BaseModel):
    prompt: str
    language: str = "python"
    context: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7

class AnalyzeCodeRequest(BaseModel):
    code: str
    language: str = "python"

class ExecuteCodeRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = 30

class APIResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the AI engine on startup"""
    logger.info("Starting AI Engine API Server...")
    logger.info("AI Engine initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Engine API Server...")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Engine API Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate": "/api/generate",
            "analyze": "/api/analyze",
            "execute": "/api/execute",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_engine": "ready",
        "timestamp": asyncio.get_event_loop().time()
    }

@app.post("/api/generate", response_model=APIResponse)
async def generate_code(request: GenerateCodeRequest):
    """Generate code based on prompt"""
    try:
        # Convert string language to enum
        try:
            language = Language(request.language.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {request.language}")
        
        # Create code request
        code_request = CodeRequest(
            prompt=request.prompt,
            language=language,
            context=request.context,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Process request
        api_request = {
            'type': 'generate',
            'prompt': request.prompt,
            'language': request.language,
            'context': request.context,
            'max_tokens': request.max_tokens,
            'temperature': request.temperature
        }
        
        result = ai_engine.process_request(api_request)
        
        return APIResponse(
            success=True,
            data=result,
            processing_time=result.get('processing_time', 0)
        )
        
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/analyze", response_model=APIResponse)
async def analyze_code(request: AnalyzeCodeRequest):
    """Analyze code structure and quality"""
    try:
        api_request = {
            'type': 'analyze',
            'code': request.code,
            'language': request.language
        }
        
        result = ai_engine.process_request(api_request)
        
        return APIResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        logger.error(f"Code analysis failed: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/execute", response_model=APIResponse)
async def execute_code(request: ExecuteCodeRequest, background_tasks: BackgroundTasks):
    """Execute code safely"""
    try:
        if request.language.lower() != 'python':
            raise HTTPException(status_code=400, detail="Only Python execution is currently supported")
        
        api_request = {
            'type': 'execute',
            'code': request.code,
            'language': request.language
        }
        
        result = ai_engine.process_request(api_request)
        
        return APIResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        logger.error(f"Code execution failed: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/cpp-generate")
async def cpp_generate_code(request: GenerateCodeRequest):
    """Generate code using C++ AI engine"""
    try:
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            input_data = {
                'prompt': request.prompt,
                'language': request.language,
                'context': request.context or '',
                'max_tokens': request.max_tokens,
                'temperature': request.temperature
            }
            json.dump(input_data, f)
            input_file = f.name
        
        try:
            # Run C++ AI engine
            result = subprocess.run(
                ['./build/ai_engine', input_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse output
                output_lines = result.stdout.strip().split('\n')
                generated_code = '\n'.join(output_lines[2:])  # Skip header lines
                
                return APIResponse(
                    success=True,
                    data={
                        'code': generated_code,
                        'explanation': 'Generated using C++ AI engine',
                        'confidence': 0.85
                    }
                )
            else:
                return APIResponse(
                    success=False,
                    error=f"C++ engine failed: {result.stderr}"
                )
                
        finally:
            # Cleanup temp file
            os.unlink(input_file)
            
    except subprocess.TimeoutExpired:
        return APIResponse(
            success=False,
            error="C++ engine timeout"
        )
    except Exception as e:
        logger.error(f"C++ engine execution failed: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )

@app.get("/api/models")
async def list_models():
    """List available AI models"""
    return {
        "python_models": [
            "microsoft/CodeGPT-small-py",
            "gpt2",
            "codegen-350M-mono"
        ],
        "cpp_models": [
            "custom-transformer",
            "template-based"
        ],
        "capabilities": [
            "code_generation",
            "code_analysis",
            "code_execution",
            "syntax_checking"
        ]
    }

@app.get("/api/languages")
async def supported_languages():
    """List supported programming languages"""
    return {
        "supported": [
            "python",
            "cpp",
            "javascript",
            "html",
            "css"
        ],
        "execution_support": [
            "python"
        ],
        "analysis_support": [
            "python",
            "cpp",
            "javascript"
        ]
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    try:
        while True:
            # Receive request
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # Process request
            result = ai_engine.process_request(request_data)
            
            # Send response
            await websocket.send_text(json.dumps(result))
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server"""
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Engine API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print("Starting AI Engine API Server...")
    print(f"Server will be available at http://{args.host}:{args.port}")
    print("API documentation at http://{args.host}:{args.port}/docs")
    
    run_server(args.host, args.port, args.reload)