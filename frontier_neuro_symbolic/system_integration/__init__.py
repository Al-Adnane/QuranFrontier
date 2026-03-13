"""System Integration & Ray Orchestration Module.

Coordinates all 10 FrontierQu modules via Ray distributed computing:

1. RayClusterManager: Initialize cluster from YAML config
2. ModuleActor: Remote actor wrapping each module
3. SystemOrchestrator: Master orchestration layer
4. FrontierPipeline: End-to-end inference pipeline
5. FeedbackLoop: Three-world architecture refinement

Example usage:

    from frontier_neuro_symbolic.system_integration import (
        RayClusterManager, SystemOrchestrator, FrontierPipeline
    )
    from pathlib import Path

    # Initialize Ray cluster
    config = Path("ray_config.yaml")
    cluster_mgr = RayClusterManager(str(config))
    cluster_mgr.initialize_cluster()

    # Create orchestrator
    orchestrator = SystemOrchestrator(cluster_mgr)

    # Create pipeline
    pipeline = FrontierPipeline(orchestrator)

    # Process Quranic text
    result = pipeline.process("بسم الله الرحمن الرحيم")
    print(f"Interpretation: {result.interpretation}")
    print(f"Confidence: {result.confidence}")
    print(f"Execution time: {result.execution_time}s")
"""

from .ray_orchestrator import (
    RayClusterManager,
    ModuleActor,
    SystemOrchestrator,
    ModuleOutput,
    OrchestrationResult,
)

from .pipeline import (
    FrontierPipeline,
    FrontierOutput,
    DataPreprocessor,
    ParallelExecutor,
    ResultAggregator,
    FeedbackLoop,
    WorldLayer,
)

from .lean_interface import LeanProver, LeanProverError

__all__ = [
    # Ray Orchestration
    "RayClusterManager",
    "ModuleActor",
    "SystemOrchestrator",
    "ModuleOutput",
    "OrchestrationResult",
    # Pipeline
    "FrontierPipeline",
    "FrontierOutput",
    "DataPreprocessor",
    "ParallelExecutor",
    "ResultAggregator",
    "FeedbackLoop",
    "WorldLayer",
    # Lean Integration
    "LeanProver",
    "LeanProverError",
]

__version__ = "1.0.0"
__description__ = "System Integration & Ray Orchestration for FrontierQu v4"
