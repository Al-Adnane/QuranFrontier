"""FrontierQu Dashboard - Backend API.

Provides REST API for all 195+ model architectures.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import torch
import json

# Import all models
from frontier_models.unified_api import create_api

app = FastAPI(
    title="FrontierQu Model API",
    description="REST API for 195+ AI model architectures",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API
api = create_api()


# ==================== Pydantic Models ====================

class ModelInput(BaseModel):
    model_name: str
    input_data: List[List[float]]
    parameters: Optional[Dict[str, Any]] = None


class ModelInfo(BaseModel):
    name: str
    category: str
    description: str
    input_dim: int
    output_dim: int


class InferenceResult(BaseModel):
    output: Dict[str, Any]
    model_name: str
    inference_time_ms: float


# ==================== Endpoints ====================

@app.get("/")
async def root():
    """API root."""
    return {
        "message": "FrontierQu Model API",
        "version": "1.0.0",
        "models_available": 195,
        "docs": "/docs"
    }


@app.get("/models")
async def list_models():
    """List all available models."""
    return api.list_models()


@app.get("/models/{category}")
async def list_models_by_category(category: str):
    """List models by category."""
    all_models = api.list_models()
    if category in all_models:
        return {"category": category, "models": all_models[category]}
    raise HTTPException(status_code=404, detail=f"Category {category} not found")


@app.post("/models/{model_name}/create")
async def create_model(model_name: str, parameters: Dict[str, Any] = None):
    """Create a model instance."""
    if parameters is None:
        parameters = {}
    
    try:
        model = api.create_model(model_name, **parameters)
        return {
            "status": "success",
            "model_name": model_name,
            "parameters": parameters
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/inference")
async def run_inference(input_data: ModelInput):
    """Run inference on a model."""
    import time
    
    try:
        # Create model if not exists
        if input_data.model_name not in api.models:
            api.create_model(input_data.model_name)
        
        # Convert input to tensor
        x = torch.tensor(input_data.input_data, dtype=torch.float32)
        
        # Run inference
        start_time = time.time()
        output = api.run(input_data.model_name, x, **(input_data.parameters or {}))
        inference_time = (time.time() - start_time) * 1000
        
        # Convert output to JSON-serializable
        def to_serializable(obj):
            if isinstance(obj, torch.Tensor):
                return obj.detach().cpu().numpy().tolist()
            elif isinstance(obj, dict):
                return {k: to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [to_serializable(v) for v in obj]
            else:
                return obj
        
        return InferenceResult(
            output=to_serializable(output),
            model_name=input_data.model_name,
            inference_time_ms=inference_time
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/hardware/{backend_type}/create")
async def create_hardware(backend_type: str):
    """Create hardware backend."""
    try:
        backend = api.create_hardware(backend_type)
        return {
            "status": "success",
            "backend_type": backend_type
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/combine")
async def combine_models(
    model_names: List[str],
    combination_type: str = "sequential"
):
    """Combine multiple models."""
    try:
        models = []
        for name in model_names:
            if name not in api.models:
                api.create_model(name)
            models.append(api.models[name])
        
        combined = api.combine_models(models, combination_type)
        return {
            "status": "success",
            "combination_type": combination_type,
            "models": model_names
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": len(api.models),
        "device": api.device
    }


# ==================== Demo Endpoints ====================

@app.get("/demo/memetic")
async def demo_memetic():
    """Demo: Memetic Evolution."""
    model = api.create_model('memetic', input_dim=64, meme_dim=128)
    x = torch.randn(4, 64)
    output = model(x)
    return {"demo": "memetic", "output": "success"}


@app.get("/demo/dream")
async def demo_dream():
    """Demo: Dream Network."""
    model = api.create_model('dream', input_dim=64, latent_dim=128)
    x = torch.randn(4, 64)
    output = model(x)
    return {"demo": "dream", "output": "success"}


@app.get("/demo/quantum")
async def demo_quantum():
    """Demo: Quantum Computing."""
    model = api.create_model('quantum_computing', input_dim=64, embed_dim=128)
    x = torch.randn(4, 64)
    output = model(x)
    return {"demo": "quantum", "output": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
