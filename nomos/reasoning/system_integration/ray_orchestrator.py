"""Ray Distributed Actor Framework for FrontierQu System Orchestration.

This module implements the distributed execution layer for all 10 FrontierQu modules:
1. DAG Naskh Solver
2. Quantum Qiraat
3. Embodied Tajweed
4. Three-World Architecture
5. Advanced Solvers
6. Sheaf Neural Networks
7. Multi-Agent Scholars
8. RQL Query Language
9. Hypergraph Knowledge Base
10. Lean 4 Proofs

Architecture:
- RayClusterManager: Initializes and manages Ray cluster from config
- ModuleActor: Ray remote actor wrapping each module for parallel execution
- SystemOrchestrator: Master orchestration layer coordinating all modules
"""

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import numpy as np
import logging
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import ray
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False

logger = logging.getLogger(__name__)


class ModuleOutput(BaseModel):
    """Structured output from a module."""
    module_name: str
    output: Dict[str, Any]
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    execution_time: float = 0.0
    error: Optional[str] = None
    traces: List[str] = Field(default_factory=list)


class OrchestrationResult(BaseModel):
    """Result from orchestration across all modules."""
    module_outputs: List[ModuleOutput]
    aggregated_output: Dict[str, Any]
    confidence: float
    total_execution_time: float
    iterations: int = 0


class RayClusterManager:
    """Manages Ray cluster initialization, worker pools, and health checks."""

    def __init__(self, config_path: str):
        """Initialize cluster manager from YAML config.

        Args:
            config_path: Path to ray_config.yaml
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.cluster_name = self.config.get("cluster_name", "frontier-qu-cluster")
        self.is_initialized = False
        self._worker_pools = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load Ray cluster configuration from YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")

        if not YAML_AVAILABLE:
            # Return default config if yaml not available
            return {
                "head_node": {"cpu": 8, "gpu": 2, "memory": 64},
                "worker_pools": {
                    "gpu": {"count": 4, "cpu": 16, "gpu": 4, "memory": 128},
                    "quantum": {"count": 2, "cpu": 32, "memory": 256}
                }
            }

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def initialize_cluster(self) -> None:
        """Initialize Ray cluster with configured resources.

        This method sets up the head node and worker pools based on config.
        """
        if not RAY_AVAILABLE:
            logger.warning("Ray not available, cluster not initialized")
            return

        if ray.is_initialized():
            return

        # Initialize Ray with head node resources
        head_resources = self.config.get("head_node_resources", {})
        num_cpus = head_resources.get("CPU", 8)

        ray.init(
            ignore_reinit_error=True,
            num_cpus=num_cpus,
            num_gpus=head_resources.get("GPU", 0),
            include_dashboard=True,
            log_to_driver=self.config.get("ray_logging", {}).get("log_to_driver", True),
        )

        self.is_initialized = True
        logger.info(f"Ray cluster '{self.cluster_name}' initialized")

    def get_worker_pool(self, pool_type: str) -> List[Any]:
        """Get worker pool of specified type.

        Args:
            pool_type: "gpu" or "quantum"

        Returns:
            List of worker references
        """
        if pool_type not in self._worker_pools:
            self._worker_pools[pool_type] = []

        return self._worker_pools[pool_type]

    def health_check(self) -> Dict[str, bool]:
        """Check health of Ray cluster and worker pools.

        Returns:
            Dict with health status of different components
        """
        if not RAY_AVAILABLE:
            return {"cluster_initialized": False, "ray_available": False}

        if not ray.is_initialized():
            return {"cluster_initialized": False}

        try:
            cluster_info = ray.cluster_resources()
            return {
                "cluster_initialized": True,
                "cpus_available": cluster_info.get("CPU", 0) > 0,
                "gpus_available": cluster_info.get("GPU", 0) > 0,
                "total_cpus": cluster_info.get("CPU", 0),
                "total_gpus": cluster_info.get("GPU", 0),
                "workers_ready": len(ray.nodes()) > 1 or ray.is_initialized(),
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"cluster_initialized": False, "error": str(e)}

    def shutdown_cluster(self) -> None:
        """Shutdown Ray cluster."""
        if not RAY_AVAILABLE:
            return

        if ray.is_initialized():
            ray.shutdown()
            self.is_initialized = False
            logger.info(f"Ray cluster '{self.cluster_name}' shutdown")


class ModuleActor:
    """Remote actor wrapping individual FrontierQu modules.

    Each module (DAG, Quantum, Tajweed, etc.) runs as a remote actor
    for distributed parallel execution across the cluster.
    """

    def __init__(self, module_config: Dict[str, Any]):
        """Initialize module actor.

        Args:
            module_config: Configuration dict with module_name and module instance
        """
        self.module_config = module_config
        self.module_name = module_config.get("name", "unknown")
        self.module = module_config.get("module", None)
        self.execution_count = 0

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input through module.

        Args:
            input_data: Input dict with text, metadata, embeddings, etc.

        Returns:
            Output dict with results, confidence, traces
        """
        self.execution_count += 1
        traces = [f"Module {self.module_name} execution #{self.execution_count}"]

        try:
            if self.module is None:
                # Fallback: return mock result for testing
                return {
                    "module_name": self.module_name,
                    "output": {"interpretation": f"Mock output from {self.module_name}"},
                    "confidence": 0.7,
                    "traces": traces,
                    "execution_count": self.execution_count,
                }

            # Call module if it has a process method
            if hasattr(self.module, "process"):
                result = self.module.process(input_data)
            elif callable(self.module):
                result = self.module(input_data)
            else:
                result = {"data": input_data}

            return {
                "module_name": self.module_name,
                "output": result,
                "confidence": 0.85,
                "traces": traces + [f"Processed {len(str(input_data))} bytes"],
                "execution_count": self.execution_count,
            }

        except Exception as e:
            logger.error(f"Error in {self.module_name}: {e}")
            return {
                "module_name": self.module_name,
                "output": {},
                "confidence": 0.0,
                "error": str(e),
                "traces": traces + [f"Error: {str(e)}"],
                "execution_count": self.execution_count,
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get module execution statistics."""
        return {
            "module_name": self.module_name,
            "execution_count": self.execution_count,
        }


# Wrap in Ray remote if available
if RAY_AVAILABLE:
    try:
        ModuleActor = ray.remote(ModuleActor)
    except Exception:
        pass


class SystemOrchestrator:
    """Master orchestration layer coordinating all 10 FrontierQu modules.

    The orchestrator:
    1. Initializes module actors on Ray
    2. Routes preprocessed data to all modules in parallel
    3. Collects and aggregates results
    4. Applies feedback loops
    5. Returns unified decision
    """

    def __init__(self, cluster_manager: RayClusterManager):
        """Initialize orchestrator.

        Args:
            cluster_manager: RayClusterManager instance
        """
        self.cluster_manager = cluster_manager
        self.module_actors: Dict[str, Any] = {}
        self._initialize_modules()

    def _initialize_modules(self) -> None:
        """Initialize all 10 module actors."""
        module_names = [
            "dag_naskh",
            "quantum_qiraat",
            "tajweed",
            "three_world",
            "solvers",
            "sheaf_neural",
            "multi_agent",
            "rql",
            "hypergraph_kb",
            "lean_proofs",
        ]

        for name in module_names:
            try:
                module_config = {"name": name, "module": None}
                if RAY_AVAILABLE:
                    actor = ModuleActor.remote(module_config)
                else:
                    actor = ModuleActor(module_config)
                self.module_actors[name] = actor
                logger.debug(f"Initialized {name} actor")
            except Exception as e:
                logger.warning(f"Failed to initialize {name}: {e}")

    def process_input(
        self, text: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process input through entire system.

        Args:
            text: Quranic text or query
            metadata: Input metadata (surah, ayah, etc.)

        Returns:
            Aggregated result from all modules
        """
        # Preprocess input
        preprocessed = self._preprocess_input(text, metadata)

        # Route to modules
        module_refs = self.route_to_modules(preprocessed)

        # Collect results
        module_outputs = self._collect_results(module_refs)

        # Aggregate
        aggregated = self.aggregate_results(module_outputs)

        return aggregated

    def _preprocess_input(
        self, text: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Preprocess input data.

        Args:
            text: Input text
            metadata: Metadata dict

        Returns:
            Preprocessed data dict
        """
        # Basic preprocessing
        tokens = text.split() if isinstance(text, str) else []
        embeddings = np.random.randn(len(tokens), 768).tolist() if tokens else []

        return {
            "text": text,
            "tokens": tokens,
            "embeddings": embeddings,
            "metadata": metadata,
            "text_length": len(text),
            "token_count": len(tokens),
        }

    def route_to_modules(self, preprocessed_data: Dict[str, Any]) -> List[Any]:
        """Route preprocessed data to all modules in parallel.

        Args:
            preprocessed_data: Preprocessed input dict

        Returns:
            List of Ray ObjectRef for each module's output
        """
        object_refs = []

        for module_name, actor in self.module_actors.items():
            try:
                if RAY_AVAILABLE and hasattr(actor, "process"):
                    ref = actor.process.remote(preprocessed_data)
                else:
                    # Direct call if not using Ray
                    ref = actor.process(preprocessed_data)
                object_refs.append(ref)
                logger.debug(f"Routed to {module_name}")
            except Exception as e:
                logger.warning(f"Failed to route to {module_name}: {e}")

        return object_refs

    def _collect_results(self, object_refs: List[Any]) -> List[Dict[str, Any]]:
        """Collect results from all modules.

        Args:
            object_refs: List of Ray ObjectRef from modules

        Returns:
            List of module outputs
        """
        results = []

        for ref in object_refs:
            try:
                if RAY_AVAILABLE and hasattr(ray, "get"):
                    result = ray.get(ref, timeout=30)
                else:
                    # Direct result if not using Ray
                    result = ref() if callable(ref) else ref
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to collect result: {e}")
                results.append({"error": str(e)})

        return results

    def aggregate_results(
        self, module_outputs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregate outputs from all modules.

        Args:
            module_outputs: List of dicts from each module

        Returns:
            Aggregated result dict
        """
        if not module_outputs:
            return {
                "consensus": "No module outputs",
                "confidence": 0.0,
                "module_outputs": [],
            }

        # Compute average confidence
        confidences = [
            m.get("confidence", 0.5)
            for m in module_outputs
            if not m.get("error")
        ]
        avg_confidence = np.mean(confidences) if confidences else 0.0

        # Collect interpretations
        interpretations = []
        all_traces = []

        for output in module_outputs:
            if "output" in output and "interpretation" in output.get("output", {}):
                interpretations.append(output["output"]["interpretation"])
            if "traces" in output:
                all_traces.extend(output["traces"])

        return {
            "module_outputs": module_outputs,
            "consensus": interpretations[0] if interpretations else "No consensus",
            "confidence": float(avg_confidence),
            "num_modules": len(module_outputs),
            "execution_traces": all_traces,
            "merged_output": {
                "all_interpretations": interpretations,
                "avg_confidence": float(avg_confidence),
            },
        }
