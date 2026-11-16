from typing import Dict, List, Optional
from app.schemas.model import ModelInfo

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._register_frontier_models()

    def _register_frontier_models(self):
        models = [
            ModelInfo(
                id="anthropic/claude-sonnet-5.5",
                name="Claude Sonnet 5.5",
                provider="Anthropic",
                description="State-of-the-art coding, autonomous software engineering, recursive self-correction, and systems architecture.",
                category="Agentic Coding & Software",
                context_length=200000,
                is_available=True,
                is_default=True,
                tags=["programming", "code", "agentic", "default"]
            ),
            ModelInfo(
                id="openai/gpt-5",
                name="GPT-5",
                provider="OpenAI",
                description="Next-generation frontier reasoning model with autonomous multi-step planning, mathematical deduction, and deep logic.",
                category="Frontier Reasoning & Planning",
                context_length=256000,
                is_available=True,
                is_default=True,
                tags=["reasoning", "math", "planning", "default"]
            ),
            ModelInfo(
                id="google/gemini-3.8-flash",
                name="Gemini 3.8 Flash",
                provider="Google",
                description="Ultra-fast, high-throughput multimodal intelligence engine with massive context comprehension and sub-second execution.",
                category="Fast Multimodal & General",
                context_length=1000000,
                is_available=True,
                is_default=True,
                tags=["multimodal", "fast", "general", "default"]
            ),
            ModelInfo(
                id="anthropic/claude-opus-4.6",
                name="Claude Opus 4.6",
                provider="Anthropic",
                description="Anthropic's pinnacle systems reasoning model for deep philosophical inquiry, complex humanities, and nuanced synthesis.",
                category="Philosophy & Systems Synthesis",
                context_length=200000,
                is_available=True,
                is_default=False,
                tags=["philosophy", "creative", "synthesis", "humanities"]
            ),
            ModelInfo(
                id="openai/4-hydrogen",
                name="4-Hydrogen",
                provider="OpenAI Frontier",
                description="Specialized frontier engine tailored for empirical scientific hypotheses, physics, biochemistry, and quantitative analysis.",
                category="Scientific Research & Hypotheses",
                context_length=256000,
                is_available=True,
                is_default=False,
                tags=["science", "physics", "quantitative", "stem"]
            ),
            ModelInfo(
                id="openai/4-argon",
                name="4-Argon",
                provider="OpenAI Frontier",
                description="Heavy systems engineering and robotics intelligence optimized for hardware schematics, control systems, and CAD dynamics.",
                category="Robotics & Systems Engineering",
                context_length=256000,
                is_available=True,
                is_default=False,
                tags=["robotics", "engineering", "hardware", "cad"]
            ),
            ModelInfo(
                id="anthropic/claude-sonnet-4.6",
                name="Claude Sonnet 4.6",
                provider="Anthropic",
                description="High-precision enterprise code refactoring and algorithmic optimization model with strict instruction adherence.",
                category="Refactoring & Algorithms",
                context_length=200000,
                is_available=True,
                is_default=False,
                tags=["refactoring", "algorithms", "software"]
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
