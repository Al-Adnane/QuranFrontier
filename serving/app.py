"""FrontierQu Model Serving API.

FastAPI-based REST API for serving FrontierQu models.

Usage:
    uvicorn serving.app:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import torch
import time
import uuid
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'nomos'))

from architectures.unified_api import FrontierQuAPI

app = FastAPI(
    title="FrontierQu Model Serving API",
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
api = FrontierQuAPI()

# Model cache
model_cache: Dict[str, Any] = {}
inference_log: List[Dict] = []


# ==================== Pydantic Models ====================

class InferenceRequest(BaseModel):
    model_name: str
    input_data: List[List[float]]
    parameters: Optional[Dict[str, Any]] = None


class InferenceResponse(BaseModel):
    request_id: str
    model_name: str
    output: Dict[str, Any]
    inference_time_ms: float
    timestamp: str


class ModelInfo(BaseModel):
    name: str
    category: str
    input_dim: int
    embed_dim: int


class BenchmarkResult(BaseModel):
    model_name: str
    latency_ms: float
    params_millions: float
    throughput_samples_per_sec: float


# ==================== Endpoints ====================

@app.get("/")
async def root():
    """API root."""
    return {
        "name": "FrontierQu Model Serving API",
        "version": "1.0.0",
        "models_available": 195,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_cached": len(model_cache),
        "total_inferences": len(inference_log)
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


@app.post("/models/{model_name}/load")
async def load_model(model_name: str, input_dim: int = 64, embed_dim: int = 128):
    """Load a model into cache."""
    try:
        model = api.create_model(model_name, input_dim=input_dim, embed_dim=embed_dim)
        model_cache[model_name] = {
            'model': model,
            'input_dim': input_dim,
            'embed_dim': embed_dim,
            'loaded_at': time.time()
        }
        return {"status": "success", "model": model_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/models/{model_name}/unload")
async def unload_model(model_name: str):
    """Unload a model from cache."""
    if model_name in model_cache:
        del model_cache[model_name]
        return {"status": "success", "model": model_name}
    raise HTTPException(status_code=404, detail=f"Model {model_name} not loaded")


@app.post("/inference", response_model=InferenceResponse)
async def run_inference(request: InferenceRequest):
    """Run inference on a model."""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Load model if not cached
        if request.model_name not in model_cache:
            api.create_model(request.model_name, input_dim=64, embed_dim=128)
        
        # Convert input to tensor
        x = torch.tensor(request.input_data, dtype=torch.float32)
        
        # Run inference
        with torch.no_grad():
            output = api.run(request.model_name, x, **(request.parameters or {}))
        
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
        
        inference_time = (time.time() - start_time) * 1000
        
        # Log inference
        inference_log.append({
            'request_id': request_id,
            'model_name': request.model_name,
            'inference_time_ms': inference_time,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return InferenceResponse(
            request_id=request_id,
            model_name=request.model_name,
            output=to_serializable(output),
            inference_time_ms=inference_time,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/benchmark/{model_name}", response_model=BenchmarkResult)
async def benchmark_model(model_name: str, batch_size: int = 4, num_runs: int = 10):
    """Benchmark a model."""
    try:
        # Load model
        if model_name not in model_cache:
            api.create_model(model_name, input_dim=64, embed_dim=128)
        
        model = api.models[model_name]
        
        # Count parameters
        params = sum(p.numel() for p in model.parameters())
        
        # Benchmark
        x = torch.randn(batch_size, 64)
        
        # Warmup
        for _ in range(3):
            with torch.no_grad():
                model(x)
        
        # Benchmark runs
        torch.cuda.synchronize() if torch.cuda.is_available() else None
        start = time.time()
        
        for _ in range(num_runs):
            with torch.no_grad():
                model(x)
        
        torch.cuda.synchronize() if torch.cuda.is_available() else None
        elapsed = time.time() - start
        
        latency_ms = elapsed / num_runs * 1000
        throughput = batch_size / (latency_ms / 1000)
        
        return BenchmarkResult(
            model_name=model_name,
            latency_ms=latency_ms,
            params_millions=params / 1e6,
            throughput_samples_per_sec=throughput
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get API metrics."""
    if not inference_log:
        return {"total_inferences": 0}
    
    latencies = [log['inference_time_ms'] for log in inference_log]
    
    return {
        "total_inferences": len(inference_log),
        "avg_latency_ms": sum(latencies) / len(latencies),
        "min_latency_ms": min(latencies),
        "max_latency_ms": max(latencies),
        "models_cached": len(model_cache)
    }


@app.get("/logs")
async def get_logs(limit: int = 100):
    """Get recent inference logs."""
    return inference_log[-limit:]


# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Pre-load common models."""
    print("Starting FrontierQu Model Serving API...")
    
    # Pre-load popular models
    popular_models = ['memetic', 'dream', 'fractal', 'quantum_field']
    for model_name in popular_models:
        try:
            api.create_model(model_name, input_dim=64, embed_dim=128)
            print(f"  ✓ Pre-loaded: {model_name}")
        except Exception as e:
            print(f"  ✗ Failed to load {model_name}: {e}")
    
    print("Startup complete!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
