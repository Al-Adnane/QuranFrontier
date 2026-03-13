#!/usr/bin/env python3
"""FrontierQu CLI - Command Line Interface.

Usage:
    frontierqu --help
    frontierqu models list
    frontierqu models create <model_name> --input-dim=64 --embed-dim=128
    frontierqu models infer <model_name> --input=<data>
    frontierqu benchmark run --model=<model_name>
    frontierqu docs open
"""

import sys
import os
import argparse
import json
import torch

# Add nomos to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'nomos'))

from typing import Optional, List


def cmd_models_list(args):
    """List all available models."""
    from architectures.unified_api import FrontierQuAPI
    api = FrontierQuAPI()
    
    models = api.list_models()
    
    print("\n" + "="*60)
    print("FRONTIERQU MODELS")
    print("="*60)
    
    for category, model_list in models.items():
        print(f"\n{category.upper()} ({len(model_list)} models):")
        print("-" * 40)
        for model in model_list[:10]:
            print(f"  • {model}")
        if len(model_list) > 10:
            print(f"  ... and {len(model_list) - 10} more")
    
    print("\n" + "="*60)


def cmd_models_create(args):
    """Create a model instance."""
    from architectures.unified_api import FrontierQuAPI
    api = FrontierQuAPI()
    
    try:
        model = api.create_model(
            args.model_name,
            input_dim=args.input_dim,
            embed_dim=args.embed_dim
        )
        print(f"✓ Created model: {args.model_name}")
        print(f"  Input dim: {args.input_dim}")
        print(f"  Embed dim: {args.embed_dim}")
    except Exception as e:
        print(f"✗ Error creating model: {e}")


def cmd_models_infer(args):
    """Run inference on a model."""
    from architectures.unified_api import FrontierQuAPI
    api = FrontierQuAPI()
    
    try:
        model = api.create_model(args.model_name, input_dim=64, embed_dim=128)
        
        # Create sample input
        if args.input:
            x = torch.tensor(json.loads(args.input))
        else:
            x = torch.randn(1, 64)
        
        # Run inference
        import time
        start = time.time()
        with torch.no_grad():
            output = model(x)
        elapsed = (time.time() - start) * 1000
        
        print(f"\n✓ Inference complete: {args.model_name}")
        print(f"  Time: {elapsed:.2f}ms")
        print(f"  Output keys: {list(output.keys())}")
        
    except Exception as e:
        print(f"✗ Error running inference: {e}")


def cmd_benchmark_run(args):
    """Run benchmarks on a model."""
    from architectures.unified_api import FrontierQuAPI
    api = FrontierQuAPI()
    
    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    
    models_to_test = [
        'memetic', 'dream', 'fractal', 'quantum_field',
        'dna', 'molecular', 'quantum_computing', 'blockchain'
    ]
    
    results = []
    for model_name in models_to_test:
        try:
            model = api.create_model(model_name, input_dim=64, embed_dim=128)
            x = torch.randn(4, 64)
            
            import time
            start = time.time()
            with torch.no_grad():
                model(x)
            elapsed = (time.time() - start) * 1000
            
            # Count parameters
            params = sum(p.numel() for p in model.parameters())
            
            results.append({
                'model': model_name,
                'latency_ms': elapsed,
                'params_m': params / 1e6
            })
            
            print(f"  {model_name:20s} {elapsed:8.2f}ms  {params/1e6:6.2f}M params")
            
        except Exception as e:
            print(f"  {model_name:20s} ERROR: {e}")
    
    print("="*60)


def cmd_docs_open(args):
    """Open documentation."""
    import webbrowser
    import os
    
    doc_path = os.path.join(os.path.dirname(__file__), 'docs', 'README.md')
    
    if os.path.exists(doc_path):
        print(f"Opening documentation: {doc_path}")
        webbrowser.open(f'file://{doc_path}')
    else:
        print("Documentation not found. Run: frontierqu docs generate")


def cmd_docs_generate(args):
    """Generate documentation."""
    from architectures.unified_api import FrontierQuAPI
    api = FrontierQuAPI()
    
    models = api.list_models()
    
    doc_content = """# FrontierQu Documentation

## Available Models

"""
    
    for category, model_list in models.items():
        doc_content += f"\n## {category.upper()}\n\n"
        for model in model_list:
            doc_content += f"- {model}\n"
    
    doc_path = os.path.join(os.path.dirname(__file__), 'docs', 'README.md')
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    
    with open(doc_path, 'w') as f:
        f.write(doc_content)
    
    print(f"✓ Documentation generated: {doc_path}")


def main():
    parser = argparse.ArgumentParser(
        prog='frontierqu',
        description='FrontierQu CLI - 195+ AI Model Architectures'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Models command
    models_parser = subparsers.add_parser('models', help='Model management')
    models_subparsers = models_parser.add_subparsers()
    
    # models list
    list_parser = models_subparsers.add_parser('list', help='List all models')
    list_parser.set_defaults(func=cmd_models_list)
    
    # models create
    create_parser = models_subparsers.add_parser('create', help='Create a model')
    create_parser.add_argument('model_name', help='Model name')
    create_parser.add_argument('--input-dim', type=int, default=64)
    create_parser.add_argument('--embed-dim', type=int, default=128)
    create_parser.set_defaults(func=cmd_models_create)
    
    # models infer
    infer_parser = models_subparsers.add_parser('infer', help='Run inference')
    infer_parser.add_argument('model_name', help='Model name')
    infer_parser.add_argument('--input', help='JSON input data')
    infer_parser.set_defaults(func=cmd_models_infer)
    
    # Benchmark command
    bench_parser = subparsers.add_parser('benchmark', help='Run benchmarks')
    bench_subparsers = bench_parser.add_subparsers()
    
    run_parser = bench_subparsers.add_parser('run', help='Run benchmarks')
    run_parser.set_defaults(func=cmd_benchmark_run)
    
    # Docs command
    docs_parser = subparsers.add_parser('docs', help='Documentation')
    docs_subparsers = docs_parser.add_subparsers()
    
    open_parser = docs_subparsers.add_parser('open', help='Open docs')
    open_parser.set_defaults(func=cmd_docs_open)
    
    gen_parser = docs_subparsers.add_parser('generate', help='Generate docs')
    gen_parser.set_defaults(func=cmd_docs_generate)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
