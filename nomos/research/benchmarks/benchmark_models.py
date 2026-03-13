#!/usr/bin/env python3
"""
FrontierQu Model Benchmark Suite
Times all 181 neural architectures and outputs a Markdown report.
Usage: python3 benchmark_models.py [--quick] [--domain DOMAIN]
"""
import importlib
import pkgutil
import sys
import os
import time
import argparse
import json
from dataclasses import dataclass, asdict
from typing import List, Optional

import torch
import torch.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@dataclass
class BenchmarkResult:
    domain: str
    model_name: str
    factory: str
    param_count: int
    avg_ms: float
    min_ms: float
    max_ms: float
    status: str  # "ok" | "error" | "skip"
    error: Optional[str] = None


def discover_all_factories():
    import frontier_models
    results = []
    for finder, modname, ispkg in pkgutil.walk_packages(
        path=frontier_models.__path__,
        prefix=frontier_models.__name__ + ".",
        onerror=lambda x: None,
    ):
        if ispkg:
            continue
        try:
            mod = importlib.import_module(modname)
        except Exception:
            continue
        for attr in dir(mod):
            if attr.startswith("create_") and attr.endswith("_network"):
                fn = getattr(mod, attr)
                if callable(fn):
                    domain = modname.split(".")[-2] if len(modname.split(".")) > 2 else "unknown"
                    results.append((domain, modname, attr, fn))
    return results


def benchmark_one(factory_fn, n_runs: int = 10) -> tuple:
    """Returns (avg_ms, min_ms, max_ms, param_count) or raises."""
    try:
        model = factory_fn(input_dim=128, embed_dim=256)
    except TypeError:
        model = factory_fn()

    model.eval()
    x = torch.randn(2, 10, 128)
    param_count = sum(p.numel() for p in model.parameters())

    # Warmup
    with torch.no_grad():
        model(x)

    times = []
    with torch.no_grad():
        for _ in range(n_runs):
            t0 = time.perf_counter()
            model(x)
            times.append((time.perf_counter() - t0) * 1000)

    return sum(times) / len(times), min(times), max(times), param_count


def run_benchmarks(n_runs: int = 10, domain_filter: Optional[str] = None) -> List[BenchmarkResult]:
    factories = discover_all_factories()
    if domain_filter:
        factories = [(d, m, a, f) for d, m, a, f in factories if d == domain_filter]

    results = []
    total = len(factories)

    for i, (domain, modpath, attr, fn) in enumerate(factories):
        model_name = attr.replace("create_", "").replace("_network", "")
        print(f"[{i+1:3d}/{total}] {domain}.{model_name}", end=" ... ", flush=True)

        try:
            avg, mn, mx, params = benchmark_one(fn, n_runs)
            results.append(BenchmarkResult(
                domain=domain,
                model_name=model_name,
                factory=attr,
                param_count=params,
                avg_ms=round(avg, 4),
                min_ms=round(mn, 4),
                max_ms=round(mx, 4),
                status="ok",
            ))
            print(f"{avg:.2f}ms | {params:,} params")
        except Exception as e:
            results.append(BenchmarkResult(
                domain=domain,
                model_name=model_name,
                factory=attr,
                param_count=0,
                avg_ms=0.0,
                min_ms=0.0,
                max_ms=0.0,
                status="error",
                error=str(e)[:80],
            ))
            print(f"ERROR: {e}")

    return sorted(results, key=lambda r: r.avg_ms)


def render_markdown(results: List[BenchmarkResult]) -> str:
    ok = [r for r in results if r.status == "ok"]
    errors = [r for r in results if r.status == "error"]

    lines = [
        "# FrontierQu Model Benchmark Results",
        f"\n**Total models:** {len(results)} | **OK:** {len(ok)} | **Errors:** {len(errors)}\n",
        "## Performance Table (sorted by speed)\n",
        "| Rank | Domain | Model | Avg (ms) | Min (ms) | Max (ms) | Params |",
        "|------|--------|-------|----------|----------|----------|--------|",
    ]

    for rank, r in enumerate(ok, 1):
        lines.append(
            f"| {rank} | {r.domain} | {r.model_name} | {r.avg_ms:.3f} | "
            f"{r.min_ms:.3f} | {r.max_ms:.3f} | {r.param_count:,} |"
        )

    if errors:
        lines += ["\n## Failed Models\n", "| Domain | Model | Error |", "|--------|-------|-------|"]
        for r in errors:
            lines.append(f"| {r.domain} | {r.model_name} | `{r.error}` |")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Run 3 instead of 10 iterations")
    parser.add_argument("--domain", help="Filter to specific domain")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown")
    args = parser.parse_args()

    n_runs = 3 if args.quick else 10
    print(f"FrontierQu Benchmark — {n_runs} runs per model\n")

    results = run_benchmarks(n_runs=n_runs, domain_filter=args.domain)
    md = render_markdown(results)

    output_path = "benchmark_results.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)

    if args.json:
        with open("benchmark_results.json", "w") as f:
            json.dump([asdict(r) for r in results], f, indent=2)

    print(f"\n✅ Benchmark complete. Results saved to {output_path}")
    print(f"   {len([r for r in results if r.status == 'ok'])}/{len(results)} models succeeded")
