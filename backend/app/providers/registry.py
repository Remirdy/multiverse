from typing import Dict, List, Optional
from app.schemas.model import ModelInfo

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._register_default_models()

    def _register_default_models(self):
        models = [
            ModelInfo(
                id="nvidia/nemotron-3.5-lightning-30b-a3b",
                name="Nemotron 3.5 Lightning",
                provider="NVIDIA NIM",
                description="High-speed NVIDIA reasoning engine optimized for complex mathematical logic and precision analysis.",
                category="Mathematics & Logic",
                context_length=128000,
                is_available=True,
                is_default=True,
                tags=["math", "reasoning", "default"]
            ),
            ModelInfo(
                id="mistralai/mistral-large-4-1t-a52b",
                name="Mistral Large 4",
                provider="NVIDIA NIM",
                description="Mistral AI next-generation flagship model with exceptional creative writing and multilingual mastery.",
                category="Creative & Multilingual",
                context_length=128000,
                is_available=True,
                is_default=True,
                tags=["creative", "writing", "general", "default"]
            ),
            ModelInfo(
                id="poolside/laguna-xs-2.1",
                name="Poolside Laguna XS",
                provider="NVIDIA NIM",
                description="Specialized code and software engineering model designed for algorithms, debugging, and systems architecture.",
                category="Programming",
                context_length=64000,
                is_available=True,
                is_default=True,
                tags=["programming", "code", "algorithms", "default"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3.5-bolt-e4b",
                name="Nemotron 3.5 Bolt",
                provider="NVIDIA NIM",
                description="Ultra-fast, low-latency NIM endpoint for instantaneous queries, rapid comparisons, and general assistance.",
                category="Fast & Lightweight",
                context_length=64000,
                is_available=True,
                is_default=False,
                tags=["fast", "lightweight", "general"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
                name="Nemotron Nano Omni",
                provider="NVIDIA NIM",
                description="Deep reasoning model with step-by-step thinking traces for scientific queries, empirical hypotheses, and proofs.",
                category="Scientific Reasoning",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["scientific_reasoning", "reasoning", "stem"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3.5-super-vl-120b-a12b",
                name="Nemotron Super VL 120B",
                provider="NVIDIA NIM",
                description="High-capacity 120B multimodal model capable of deep engineering analysis, robotics logic, and technical systems.",
                category="Engineering & Robotics",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["robotics_engineering", "engineering", "multimodal"]
            ),
            ModelInfo(
                id="meta/muse-glimmer-30b",
                name="Meta Muse Glimmer 30B",
                provider="NVIDIA NIM",
                description="Creative intelligence model excelling in stylistic variety, metaphor, narrative fiction, and nuanced dialogue.",
                category="Creative Synthesis",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["creative", "synthesis", "knowledge"]
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
