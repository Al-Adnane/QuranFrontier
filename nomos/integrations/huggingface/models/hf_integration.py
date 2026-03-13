"""Hugging Face Integration for FrontierQu Models.

Publish and load models from Hugging Face Hub.
"""

from huggingface_hub import HfApi, HfFolder, upload_folder, snapshot_download
from transformers import PreTrainedModel, PretrainedConfig
import torch
import json
import os
from typing import Dict, List, Any, Optional


class FrontierQuConfig(PretrainedConfig):
    """Configuration for FrontierQu models."""
    
    model_type = "frontierqu"
    
    def __init__(
        self,
        model_name: str = "memetic",
        input_dim: int = 128,
        embed_dim: int = 256,
        category: str = "wild",
        **kwargs
    ):
        self.model_name = model_name
        self.input_dim = input_dim
        self.embed_dim = embed_dim
        self.category = category
        super().__init__(**kwargs)


class FrontierQuModel(PreTrainedModel):
    """Hugging Face wrapper for FrontierQu models."""
    
    config_class = FrontierQuConfig
    base_model_prefix = "frontierqu"
    
    def __init__(self, config: FrontierQuConfig):
        super().__init__(config)
        
        # Import the actual model
        from frontier_models.unified_api import create_api
        self.api = create_api()
        
        # Create the model
        self.model = self.api.create_model(
            config.model_name,
            input_dim=config.input_dim,
            embed_dim=config.embed_dim
        )
    
    def forward(self, input_ids: torch.Tensor, **kwargs):
        """Forward pass."""
        output = self.model(input_ids, **kwargs)
        
        # Convert to tensor output for HF compatibility
        if isinstance(output, dict):
            # Return first tensor output
            for k, v in output.items():
                if isinstance(v, torch.Tensor):
                    return {'output': v, 'metadata': {k: v for k, v in output.items() if not isinstance(v, torch.Tensor)}}
        
        return {'output': output}


class HuggingFaceIntegration:
    """Hugging Face Hub integration utilities."""
    
    def __init__(self, token: Optional[str] = None):
        self.api = HfApi()
        self.token = token or HfFolder.get_token()
        self.organization = "frontierqu"
    
    def upload_model(
        self,
        model_name: str,
        category: str,
        repo_id: Optional[str] = None,
        **model_kwargs
    ):
        """Upload a model to Hugging Face Hub."""
        from frontier_models.unified_api import create_api
        
        # Create model
        api = create_api()
        model = api.create_model(model_name, **model_kwargs)
        
        # Create config
        config = FrontierQuConfig(
            model_name=model_name,
            category=category,
            **model_kwargs
        )
        
        # Create repo
        if repo_id is None:
            repo_id = f"{self.organization}/{model_name}"
        
        # Create temporary directory
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Save model
            model_path = os.path.join(tmp_dir, "pytorch_model.bin")
            torch.save(model.state_dict(), model_path)
            
            # Save config
            config_path = os.path.join(tmp_dir, "config.json")
            config.to_json_file(config_path)
            
            # Create README
            readme_path = os.path.join(tmp_dir, "README.md")
            with open(readme_path, 'w') as f:
                f.write(f"""---
tags:
- frontierqu
- {category}
- {model_name}
license: mit
---

# {model_name.capitalize()} Model

A {category} model from the FrontierQu collection.

## Usage

```python
from transformers import AutoModel

model = AutoModel.from_pretrained("{repo_id}")
```

## FrontierQu

Part of the FrontierQu collection of 195+ AI model architectures.

See: https://github.com/frontierqu/frontier-qu
""")
            
            # Upload
            self.api.upload_folder(
                folder_path=tmp_dir,
                repo_id=repo_id,
                token=self.token,
                repo_type="model"
            )
        
        return repo_id
    
    def download_model(
        self,
        repo_id: str,
        cache_dir: Optional[str] = None
    ) -> FrontierQuModel:
        """Download a model from Hugging Face Hub."""
        # Download
        model_path = snapshot_download(
            repo_id=repo_id,
            cache_dir=cache_dir
        )
        
        # Load config
        config = FrontierQuConfig.from_pretrained(model_path)
        
        # Load model
        model = FrontierQuModel.from_pretrained(model_path, config=config)
        
        return model
    
    def list_models(self) -> List[Dict]:
        """List all FrontierQu models on HF Hub."""
        models = self.api.list_models(author=self.organization)
        return [
            {
                "id": model.id,
                "downloads": model.downloads,
                "likes": model.likes,
                "tags": model.tags
            }
            for model in models
        ]
    
    def create_pipeline(
        self,
        model_name: str,
        task: str = "feature-extraction"
    ):
        """Create a Hugging Face pipeline for a FrontierQu model."""
        from transformers import pipeline
        
        # Load model
        model = self.download_model(f"{self.organization}/{model_name}")
        
        # Create pipeline
        pipe = pipeline(
            task=task,
            model=model,
            framework="pt"
        )
        
        return pipe


# ==================== Convenience Functions ====================

def upload_to_hf(
    model_name: str,
    category: str,
    token: Optional[str] = None,
    **model_kwargs
) -> str:
    """Upload a FrontierQu model to Hugging Face."""
    integration = HuggingFaceIntegration(token)
    return integration.upload_model(model_name, category, **model_kwargs)


def download_from_hf(
    repo_id: str,
    cache_dir: Optional[str] = None
) -> FrontierQuModel:
    """Download a FrontierQu model from Hugging Face."""
    integration = HuggingFaceIntegration()
    return integration.download_model(repo_id, cache_dir)


if __name__ == "__main__":
    # Example usage
    print("FrontierQu Hugging Face Integration")
    print("=" * 50)
    
    # List available models
    integration = HuggingFaceIntegration()
    models = integration.list_models()
    print(f"Models on HF Hub: {len(models)}")
    
    for model in models[:5]:
        print(f"  - {model['id']} ({model['downloads']} downloads)")
