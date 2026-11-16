from typing import Dict, List, Optional
from app.schemas.model import ModelInfo


class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._register_nvidia_models()

    def _register_nvidia_models(self):
        models = [
            ModelInfo(
                id="poolside/laguna-xs-2.1",
                name="Poolside Laguna XS",
                provider="NVIDIA NIM",
                provider_id="nvidia",
                is_local=False,
                is_free_tier=True,
                description="Software engineering, algorithms, refactoring, and system architecture model.",
                category="Kod & Yazılım (Sonnet 5.5 Muadili)",
                context_length=64000,
                is_available=True,
                is_default=True,
                tags=["programming", "code", "sonnet-tier", "default"],
                capabilities={
                    "chat": True,
                    "vision": False,
                    "structured_output": True,
                    "tool_calling": True,
                    "streaming": True,
                    "context_length": 64000,
                    "modalities": ["text", "code"],
                },
            ),
            ModelInfo(
                id="nvidia/nemotron-3.5-lightning-30b-a3b",
                name="Nemotron 3.5 Lightning",
                provider="NVIDIA NIM",
                provider_id="nvidia",
                is_local=False,
                is_free_tier=True,
                description="Fast mathematical reasoning, calculus, linear algebra, and formal logic model.",
                category="Matematik & Mantık (GPT-5 Muadili)",
                context_length=128000,
                is_available=True,
                is_default=True,
                tags=["math", "logic", "gpt5-tier", "default"],
                capabilities={
                    "chat": True,
                    "vision": False,
                    "structured_output": True,
                    "tool_calling": True,
                    "streaming": True,
                    "context_length": 128000,
                    "modalities": ["text", "math"],
                },
            ),
            ModelInfo(
                id="nvidia/nemotron-3-ultra-550b-a55b",
                name="Nemotron 3 Ultra 550B",
                provider="NVIDIA NIM",
                provider_id="nvidia",
                is_local=False,
                is_free_tier=True,
                description="Large synthesis and deep conceptual reasoning model for multi-perspective evaluation.",
                category="Frontier Sentez (Claude Opus Muadili)",
                context_length=128000,
                is_available=True,
                is_default=True,
                tags=["frontier", "opus-tier", "synthesis", "default"],
                capabilities={
                    "chat": True,
                    "vision": False,
                    "structured_output": True,
                    "tool_calling": True,
                    "streaming": True,
                    "context_length": 128000,
                    "modalities": ["text"],
                },
            ),
            ModelInfo(
                id="nvidia/nemotron-3.5-bolt-e4b",
                name="Nemotron 3.5 Bolt",
                provider="NVIDIA NIM",
                provider_id="nvidia",
                is_local=False,
                is_free_tier=True,
                description="Low-latency model suited for fast summarization, triage, and short responses.",
                category="Ultra Hızlı & Özet (Gemini Flash Muadili)",
                context_length=64000,
                is_available=True,
                is_default=False,
                tags=["fast", "gemini-flash-tier", "speed"],
                capabilities={
                    "chat": True,
                    "vision": False,
                    "structured_output": True,
                    "tool_calling": True,
                    "streaming": True,
                    "context_length": 64000,
                    "modalities": ["text"],
                },
            ),
            ModelInfo(
                id="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
                name="Nemotron Nano Omni",
                provider="NVIDIA NIM",
                provider_id="nvidia",
                is_local=False,
                is_free_tier=True,
                description="Physics, chemistry, thermodynamics, and quantitative STEM reasoning model.",
                category="Bilimsel Araştırma (4-Hydrogen Muadili)",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["science", "hydrogen-tier", "stem"],
                capabilities={
                    "chat": True,
                    "vision": False,
                    "structured_output": True,
                    "tool_calling": True,
                    "streaming": True,
                    "context_length": 128000,
                    "modalities": ["text"],
                },
            ),
            ModelInfo(
                id="nvidia/nemotron-3.5-super-vl-120b-a12b",
                name="Nemotron Super VL 120B",
                provider="NVIDIA NIM",
                provider_id="nvidia",
                is_local=False,
                is_free_tier=True,
                description="Multimodal vision model for circuit schematics, technical diagrams, and robotics.",
                category="Görsel & Devre Şeması (4-Argon Vision)",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["vision", "multimodal", "robotics", "argon-tier", "engineering"],
                capabilities={
                    "chat": True,
                    "vision": True,
                    "structured_output": True,
                    "tool_calling": True,
                    "streaming": True,
                    "context_length": 128000,
                    "modalities": ["text", "image"],
                },
            ),
            ModelInfo(
                id="mistralai/mistral-large-4-1t-a52b",
                name="Mistral Large 4 1T",
                provider="NVIDIA NIM",
                provider_id="nvidia",
                is_local=False,
                is_free_tier=True,
                description="Multilingual general reasoning and analytical model.",
                category="İleri Düzey Akıl Yürütme (Sonnet 4.6 Muadili)",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["reasoning", "general", "mistral-tier"],
                capabilities={
                    "chat": True,
                    "vision": False,
                    "structured_output": True,
                    "tool_calling": True,
                    "streaming": True,
                    "context_length": 128000,
                    "modalities": ["text"],
                },
            ),
            ModelInfo(
                id="nvidia/riva-translate-4b-instruct-v2",
                name="Riva Translate 4B",
                provider="NVIDIA NIM",
                provider_id="nvidia",
                is_local=False,
                is_free_tier=True,
                description="Low-latency neural translation and localization model.",
                category="Çeviri & Dilbilim (NVIDIA Riva)",
                context_length=32000,
                is_available=True,
                is_default=False,
                tags=["translation", "linguistics", "multilingual"],
                capabilities={
                    "chat": True,
                    "vision": False,
                    "structured_output": False,
                    "tool_calling": False,
                    "streaming": True,
                    "context_length": 32000,
                    "modalities": ["text"],
                },
            ),
        ]
        for m in models:
            self._models[m.id] = m

    def register(self, model: ModelInfo):
        self._models[model.id] = model

    def register_local_models(self, provider_id: str, provider_name: str, model_ids: List[str], is_local: bool = True):
        to_remove = [mid for mid, info in self._models.items() if info.provider_id == provider_id]
        for mid in to_remove:
            del self._models[mid]

        for raw_id in model_ids:
            full_id = f"{provider_id}::{raw_id}"
            self._models[full_id] = ModelInfo(
                id=full_id,
                name=f"{raw_id} ({provider_name})",
                provider=provider_name,
                provider_id=provider_id,
                is_local=is_local,
                is_free_tier=True,
                description=f"Discovered model served via {provider_name}.",
                category="Local Inference" if is_local else "Custom Endpoint",
                context_length=32768,
                is_available=True,
                is_default=False,
                tags=["local" if is_local else "custom", provider_id],
                capabilities={
                    "chat": True,
                    "vision": "vl" in raw_id.lower() or "vision" in raw_id.lower() or "llava" in raw_id.lower(),
                    "structured_output": True,
                    "tool_calling": False,
                    "streaming": False,
                    "context_length": 32768,
                    "modalities": ["text"],
                },
            )

    def get(self, model_id: str) -> Optional[ModelInfo]:
        return self._models.get(model_id)

    def list_all(self) -> List[ModelInfo]:
        return list(self._models.values())

    def get_default_model_ids(self) -> List[str]:
        return [m.id for m in self._models.values() if m.is_default]

    def exists(self, model_id: str) -> bool:
        return model_id in self._models


model_registry = ModelRegistry()
