"""FrontierQu Model Registry.

Version control and metadata management for models.
"""

import os
import json
import hashlib
import torch
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'nomos'))


@dataclass
class ModelVersion:
    """Model version metadata."""
    model_name: str
    version: str
    hash: str
    created_at: str
    input_dim: int
    embed_dim: int
    params_count: int
    tags: List[str]
    description: str
    metrics: Dict[str, float]


class ModelRegistry:
    """Registry for model versions and metadata."""
    
    def __init__(self, registry_path: str = "./model_registry"):
        self.registry_path = registry_path
        os.makedirs(registry_path, exist_ok=True)
        
        self.index_path = os.path.join(registry_path, "index.json")
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """Load registry index."""
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r') as f:
                return json.load(f)
        return {"models": {}}
    
    def _save_index(self):
        """Save registry index."""
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _compute_hash(self, model: torch.nn.Module) -> str:
        """Compute model hash."""
        state_dict = model.state_dict()
        hash_obj = hashlib.sha256()
        
        for key, value in sorted(state_dict.items()):
            hash_obj.update(key.encode())
            hash_obj.update(value.cpu().numpy().tobytes())
        
        return hash_obj.hexdigest()[:16]
    
    def register(
        self,
        model: torch.nn.Module,
        model_name: str,
        version: str = "1.0.0",
        tags: List[str] = None,
        description: str = "",
        metrics: Dict[str, float] = None
    ) -> ModelVersion:
        """Register a model version."""
        # Compute hash
        model_hash = self._compute_hash(model)
        
        # Count parameters
        params_count = sum(p.numel() for p in model.parameters())
        
        # Get model dimensions (if available)
        input_dim = getattr(model, 'input_dim', 0)
        embed_dim = getattr(model, 'embed_dim', 0)
        
        # Create version record
        version_record = ModelVersion(
            model_name=model_name,
            version=version,
            hash=model_hash,
            created_at=datetime.now().isoformat(),
            input_dim=input_dim,
            embed_dim=embed_dim,
            params_count=params_count,
            tags=tags or [],
            description=description,
            metrics=metrics or {}
        )
        
        # Update index
        if model_name not in self.index["models"]:
            self.index["models"][model_name] = {
                "versions": [],
                "latest": None
            }
        
        self.index["models"][model_name]["versions"].append(asdict(version_record))
        self.index["models"][model_name]["latest"] = version
        
        # Save model weights
        model_dir = os.path.join(self.registry_path, model_name, version)
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, "model.pt")
        torch.save(model.state_dict(), model_path)
        
        # Save metadata
        metadata_path = os.path.join(model_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(asdict(version_record), f, indent=2)
        
        # Save index
        self._save_index()
        
        return version_record
    
    def get(self, model_name: str, version: str = None) -> Optional[ModelVersion]:
        """Get model version metadata."""
        if model_name not in self.index["models"]:
            return None
        
        model_info = self.index["models"][model_name]
        
        if version is None:
            version = model_info["latest"]
        
        for v in model_info["versions"]:
            if v["version"] == version:
                return ModelVersion(**v)
        
        return None
    
    def list_models(self) -> List[str]:
        """List all registered models."""
        return list(self.index["models"].keys())
    
    def list_versions(self, model_name: str) -> List[str]:
        """List all versions of a model."""
        if model_name not in self.index["models"]:
            return []
        
        return [v["version"] for v in self.index["models"][model_name]["versions"]]
    
    def load_model(self, model_name: str, version: str = None) -> Optional[torch.nn.Module]:
        """Load a model from registry."""
        metadata = self.get(model_name, version)
        if metadata is None:
            return None
        
        model_path = os.path.join(self.registry_path, model_name, metadata.version, "model.pt")
        
        if not os.path.exists(model_path):
            return None
        
        # Import model class dynamically
        from architectures.unified_api import FrontierQuAPI
        api = FrontierQuAPI()
        
        try:
            model = api.create_model(model_name, input_dim=metadata.input_dim, embed_dim=metadata.embed_dim)
            model.load_state_dict(torch.load(model_path))
            return model
        except Exception:
            return None
    
    def delete_version(self, model_name: str, version: str) -> bool:
        """Delete a model version."""
        if model_name not in self.index["models"]:
            return False
        
        model_info = self.index["models"][model_name]
        
        # Remove from index
        model_info["versions"] = [v for v in model_info["versions"] if v["version"] != version]
        
        if model_info["latest"] == version:
            model_info["latest"] = model_info["versions"][-1]["version"] if model_info["versions"] else None
        
        # Remove files
        model_dir = os.path.join(self.registry_path, model_name, version)
        if os.path.exists(model_dir):
            import shutil
            shutil.rmtree(model_dir)
        
        # Save index
        if not model_info["versions"]:
            del self.index["models"][model_name]
        
        self._save_index()
        return True
    
    def get_stats(self) -> Dict:
        """Get registry statistics."""
        total_models = len(self.index["models"])
        total_versions = sum(len(m["versions"]) for m in self.index["models"].values())
        total_params = sum(
            v["params_count"]
            for m in self.index["models"].values()
            for v in m["versions"]
        )
        
        return {
            "total_models": total_models,
            "total_versions": total_versions,
            "total_parameters": total_params,
            "registry_size_gb": self._get_registry_size()
        }
    
    def _get_registry_size(self) -> float:
        """Get registry size in GB."""
        total_size = 0
        for root, dirs, files in os.walk(self.registry_path):
            for f in files:
                fp = os.path.join(root, f)
                total_size += os.path.getsize(fp)
        return total_size / (1024 ** 3)


# ==================== CLI Interface ====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="FrontierQu Model Registry")
    subparsers = parser.add_subparsers(dest="command")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List models")
    list_parser.set_defaults(func=lambda args: print(Registry.list_models()))
    
    # Register command
    reg_parser = subparsers.add_parser("register", help="Register a model")
    reg_parser.add_argument("model_name", help="Model name")
    reg_parser.add_argument("--version", default="1.0.0", help="Version")
    reg_parser.set_defaults(func=lambda args: print("Use Python API to register models"))
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Registry statistics")
    stats_parser.set_defaults(func=lambda args: print(Registry.get_stats()))
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    Registry = ModelRegistry()
    main()
