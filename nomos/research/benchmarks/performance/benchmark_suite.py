"""Comprehensive Benchmarking Suite for FrontierQu Models.

Benchmark performance, memory, and accuracy across all 195+ models.
"""

import torch
import time
import psutil
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import os


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""
    model_name: str
    category: str
    input_size: tuple
    inference_time_ms: float
    memory_mb: float
    throughput_samples_per_sec: float
    gpu_memory_mb: Optional[float] = None
    timestamp: str = ""


class BenchmarkSuite:
    """Comprehensive benchmarking suite."""
    
    def __init__(self, results_dir: str = "benchmark_results"):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        self.results: List[BenchmarkResult] = []
    
    def benchmark_inference(
        self,
        model: torch.nn.Module,
        model_name: str,
        category: str,
        input_size: tuple = (4, 128),
        num_runs: int = 10,
        warmup_runs: int = 3
    ) -> BenchmarkResult:
        """Benchmark inference speed."""
        device = next(model.parameters()).device
        
        # Create input
        x = torch.randn(*input_size, device=device)
        
        # Warmup
        for _ in range(warmup_runs):
            with torch.no_grad():
                model(x)
        
        # Benchmark
        torch.cuda.synchronize() if device.type == 'cuda' else None
        start_time = time.time()
        
        for _ in range(num_runs):
            with torch.no_grad():
                model(x)
        
        torch.cuda.synchronize() if device.type == 'cuda' else None
        end_time = time.time()
        
        # Calculate metrics
        inference_time_ms = (end_time - start_time) / num_runs * 1000
        throughput = input_size[0] / (inference_time_ms / 1000)
        
        # Memory usage
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        # GPU memory if available
        gpu_memory_mb = None
        if device.type == 'cuda':
            gpu_memory_mb = torch.cuda.memory_allocated() / 1024 / 1024
        
        result = BenchmarkResult(
            model_name=model_name,
            category=category,
            input_size=input_size,
            inference_time_ms=inference_time_ms,
            memory_mb=memory_mb,
            throughput_samples_per_sec=throughput,
            gpu_memory_mb=gpu_memory_mb,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.results.append(result)
        return result
    
    def benchmark_memory(
        self,
        model: torch.nn.Module,
        model_name: str,
        category: str
    ) -> Dict[str, float]:
        """Benchmark memory usage."""
        device = next(model.parameters()).device
        
        # Model parameters
        param_count = sum(p.numel() for p in model.parameters())
        param_size_mb = param_count * 4 / 1024 / 1024  # FP32
        
        # Activation memory
        x = torch.randn(1, 128, device=device)
        
        # Forward hook to measure activations
        activation_memory = []
        
        def hook_fn(module, input, output):
            if isinstance(output, torch.Tensor):
                activation_memory.append(output.numel() * 4)
            elif isinstance(output, dict):
                for v in output.values():
                    if isinstance(v, torch.Tensor):
                        activation_memory.append(v.numel() * 4)
        
        # Register hooks
        hooks = []
        for module in model.modules():
            hooks.append(module.register_forward_hook(hook_fn))
        
        # Forward pass
        with torch.no_grad():
            model(x)
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        activation_size_mb = sum(activation_memory) / 1024 / 1024
        
        return {
            "model_name": model_name,
            "category": category,
            "param_count": param_count,
            "param_size_mb": param_size_mb,
            "activation_size_mb": activation_size_mb,
            "total_memory_mb": param_size_mb + activation_size_mb
        }
    
    def benchmark_accuracy(
        self,
        model: torch.nn.Module,
        test_data: torch.Tensor,
        test_labels: torch.Tensor,
        model_name: str,
        category: str
    ) -> Dict[str, float]:
        """Benchmark accuracy on test data."""
        device = next(model.parameters()).device
        
        model.eval()
        with torch.no_grad():
            output = model(test_data.to(device))
            
            # Handle different output formats
            if isinstance(output, dict):
                if 'output' in output:
                    pred = output['output']
                else:
                    # Find first tensor
                    pred = next(v for v in output.values() if isinstance(v, torch.Tensor))
            else:
                pred = output
        
        # Calculate accuracy
        if pred.shape == test_labels.shape:
            # Regression
            mse = ((pred - test_labels.to(device)) ** 2).mean().item()
            return {
                "model_name": model_name,
                "category": category,
                "metric": "mse",
                "value": mse
            }
        else:
            # Classification
            pred_class = pred.argmax(dim=-1)
            accuracy = (pred_class == test_labels.to(device)).float().mean().item()
            return {
                "model_name": model_name,
                "category": category,
                "metric": "accuracy",
                "value": accuracy
            }
    
    def run_full_benchmark(
        self,
        models: List[tuple],  # (model, name, category)
        input_size: tuple = (4, 128)
    ) -> Dict[str, List[BenchmarkResult]]:
        """Run full benchmark suite on all models."""
        results_by_category = {}
        
        for model, name, category in models:
            print(f"Benchmarking {name}...")
            
            # Inference benchmark
            result = self.benchmark_inference(model, name, category, input_size)
            
            if category not in results_by_category:
                results_by_category[category] = []
            results_by_category[category].append(result)
        
        return results_by_category
    
    def save_results(self, filename: str = "benchmark_results.json"):
        """Save benchmark results to JSON."""
        results_data = [asdict(r) for r in self.results]
        
        filepath = os.path.join(self.results_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"Results saved to {filepath}")
    
    def generate_report(self) -> str:
        """Generate benchmark report."""
        if not self.results:
            return "No benchmark results available."
        
        report = []
        report.append("# FrontierQu Benchmark Report")
        report.append("")
        report.append(f"**Total Models Benchmarked:** {len(self.results)}")
        report.append("")
        
        # Group by category
        by_category = {}
        for r in self.results:
            if r.category not in by_category:
                by_category[r.category] = []
            by_category[r.category].append(r)
        
        for category, results in by_category.items():
            report.append(f"## {category.capitalize()}")
            report.append("")
            report.append("| Model | Inference (ms) | Memory (MB) | Throughput |")
            report.append("|-------|----------------|-------------|------------|")
            
            for r in results:
                report.append(
                    f"| {r.model_name} | {r.inference_time_ms:.2f} | "
                    f"{r.memory_mb:.1f} | {r.throughput_samples_per_sec:.1f} |"
                )
            
            report.append("")
        
        return "\n".join(report)


# ==================== Convenience Functions ====================

def benchmark_model(
    model: torch.nn.Module,
    model_name: str,
    category: str,
    **kwargs
) -> BenchmarkResult:
    """Quick benchmark for a single model."""
    suite = BenchmarkSuite()
    return suite.benchmark_inference(model, model_name, category, **kwargs)


def benchmark_all_models() -> Dict[str, List[BenchmarkResult]]:
    """Benchmark all FrontierQu models."""
    from frontier_models.unified_api import create_api
    
    api = create_api()
    suite = BenchmarkSuite()
    
    models_to_benchmark = []
    
    # Sample models from each category
    sample_models = [
        ('memetic', 'wild', {'input_dim': 64, 'meme_dim': 128}),
        ('dream', 'wild', {'input_dim': 64, 'latent_dim': 128}),
        ('quantum_field', 'physics', {'input_dim': 64, 'embed_dim': 128}),
        ('dna', 'bio', {'input_dim': 64, 'embed_dim': 128}),
        ('molecular', 'chem', {'input_dim': 64, 'embed_dim': 128}),
        ('graph_theory', 'math', {'input_dim': 64, 'embed_dim': 128}),
        ('quantum_computing', 'tech', {'input_dim': 64, 'embed_dim': 128}),
    ]
    
    for name, category, params in sample_models:
        try:
            model = api.create_model(name, **params)
            models_to_benchmark.append((model, name, category))
        except Exception as e:
            print(f"Failed to create {name}: {e}")
    
    results = suite.run_full_benchmark(models_to_benchmark)
    suite.save_results()
    
    return results


if __name__ == "__main__":
    print("Running FrontierQu Benchmark Suite")
    print("=" * 50)
    
    results = benchmark_all_models()
    
    # Print summary
    suite = BenchmarkSuite()
    print(suite.generate_report())
