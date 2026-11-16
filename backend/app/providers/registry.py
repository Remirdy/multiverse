from typing import Dict, List, Optional
from app.schemas.model import ModelInfo

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._register_specialized_models()

    def _register_specialized_models(self):
        models = [
            ModelInfo(
                id="poolside/laguna-xs-2.1",
                name="Poolside Laguna XS",
                provider="NVIDIA NIM",
                description="Specialized software engineering model trained on codebases, algorithms, debugging, and systems architecture.",
                category="Programming & Code",
                context_length=64000,
                is_available=True,
                is_default=True,
                tags=["programming", "code", "algorithms", "debugging", "default"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3.5-lightning-30b-a3b",
                name="Nemotron 3.5 Lightning",
                provider="NVIDIA NIM",
                description="NVIDIA mathematical engine optimized specifically for formal proofs, calculus, algebra, and high-speed logic.",
                category="Mathematics & Logic",
                context_length=128000,
                is_available=True,
                is_default=True,
                tags=["math", "logic", "calculation", "default"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3-ultra-550b-a55b",
                name="Nemotron 3 Ultra 550B",
                provider="NVIDIA NIM",
                description="Massive 550B parameter frontier model engineered for deep academic synthesis, history, cosmology, and complex conceptual analysis.",
                category="Frontier Synthesis",
                context_length=128000,
                is_available=True,
                is_default=True,
                tags=["frontier", "synthesis", "knowledge", "deep-thought", "default"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
                name="Nemotron Nano Omni",
                provider="NVIDIA NIM",
                description="Deep scientific deduction model that exposes step-by-step thinking traces for physics, chemistry, biology, and hypothesis testing.",
                category="Scientific Reasoning",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["science", "physics", "chemistry", "reasoning"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3.5-super-vl-120b-a12b",
                name="Nemotron Super VL 120B",
                provider="NVIDIA NIM",
                description="Specialized 120B model for robotics control systems, electrical engineering, mechatronics, sensor fusion, and hardware CAD.",
                category="Robotics & Engineering",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["robotics", "engineering", "hardware", "cad"]
            ),
            ModelInfo(
                id="nvidia/riva-translate-4b-instruct-v2",
                name="Riva Translate 4B",
                provider="NVIDIA NIM",
                description="NVIDIA Riva dedicated translation engine for high-precision cross-lingual translation, localization, and linguistic analysis.",
                category="Translation & Linguistics",
                context_length=32000,
                is_available=True,
                is_default=False,
                tags=["translation", "languages", "multilingual", "linguistics"]
            ),
            ModelInfo(
                id="minimaxai/minimax-m3.1-flash",
                name="MiniMax M3.1 Flash",
                provider="NVIDIA NIM",
                description="Creative intelligence model tailored for literary prose, character dialogues, poetic metaphors, narrative fiction, and copywriting.",
                category="Creative Writing",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["creative", "writing", "story", "poem", "fiction"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3.5-bolt-e4b",
                name="Nemotron 3.5 Bolt",
                provider="NVIDIA NIM",
                description="Sub-second low-latency engine built for rapid conversation, executive summaries, quick factual lookups, and fast turnaround.",
                category="Fast & Lightweight",
                context_length=64000,
                is_available=True,
                is_default=False,
                tags=["fast", "speed", "summary", "general"]
            ),
        ]
        for m in models:
            self._models[m.id] = m

    def register(self, model: ModelInfo):
        self._models[model.id] = model

    def get(self, model_id: str) -> Optional[ModelInfo]:
        return self._models.get(model_id)

    def list_all(self) -> List[ModelInfo]:
        return list(self._models.values())

    def get_default_model_ids(self) -> List[str]:
        return [m.id for m in self._models.values() if m.is_default]

    def exists(self, model_id: str) -> bool:
        return model_id in self._models

model_registry = ModelRegistry()
