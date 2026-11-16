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
                description="Claude Sonnet 5.5 muadili. Özel kod tabanları, algoritmalar, refactoring ve derin yazılım mimarisi uzmanı.",
                category="Kod & Yazılım (Sonnet 5.5 Muadili)",
                context_length=64000,
                is_available=True,
                is_default=True,
                tags=["programming", "code", "sonnet-tier", "default"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3.5-lightning-30b-a3b",
                name="Nemotron 3.5 Lightning",
                provider="NVIDIA NIM",
                description="GPT-5 Reasoning muadili. Yüksek hızlı matematiksel ispatlar, kalkülüs, cebir ve formel mantık çıkarımı.",
                category="Matematik & Mantık (GPT-5 Muadili)",
                context_length=128000,
                is_available=True,
                is_default=True,
                tags=["math", "logic", "gpt5-tier", "default"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3-ultra-550b-a55b",
                name="Nemotron 3 Ultra 550B",
                provider="NVIDIA NIM",
                description="Claude Opus 4.6 muadili. 550 Milyar parametreli devasa akademik sentez, felsefe, kozmoloji ve derin beşeri bilimler.",
                category="Frontier Sentez (Claude Opus Muadili)",
                context_length=128000,
                is_available=True,
                is_default=True,
                tags=["frontier", "opus-tier", "synthesis", "default"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3.5-bolt-e4b",
                name="Nemotron 3.5 Bolt",
                provider="NVIDIA NIM",
                description="Gemini 3.8 Flash muadili. 200 milisaniyelik sub-second yanıt hızı, çok yönlü hızlı özetleme ve dinamik diyalog.",
                category="Ultra Hızlı & Özet (Gemini Flash Muadili)",
                context_length=64000,
                is_available=True,
                is_default=False,
                tags=["fast", "gemini-flash-tier", "speed"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
                name="Nemotron Nano Omni",
                provider="NVIDIA NIM",
                description="4-Hydrogen muadili. Fizik, kimya, termodinamik ve nicel STEM hipotezlerinde adım adım şeffaf çıkarım.",
                category="Bilimsel Araştırma (4-Hydrogen Muadili)",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["science", "hydrogen-tier", "stem"]
            ),
            ModelInfo(
                id="nvidia/nemotron-3.5-super-vl-120b-a12b",
                name="Nemotron Super VL 120B",
                provider="NVIDIA NIM",
                description="4-Argon muadili. 120B çok modlu kapasite; devre şemaları, robotik kinematiği, ROS sistemleri, PID kontrol ve teknik çizimler.",
                category="Görsel & Devre Şeması (4-Argon Vision)",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["vision", "multimodal", "robotics", "argon-tier", "engineering"]
            ),

            ModelInfo(
                id="mistralai/mistral-large-4-1t-a52b",
                name="Mistral Large 4 1T",
                provider="NVIDIA NIM",
                description="Claude Sonnet 4.6 muadili. 1 Trilyon token bağlamlı derin muhakeme, analitik ve çok dilli genel zekâ.",
                category="İleri Düzey Akıl Yürütme (Sonnet 4.6 Muadili)",
                context_length=128000,
                is_available=True,
                is_default=False,
                tags=["reasoning", "general", "mistral-tier"]
            ),
            ModelInfo(
                id="nvidia/riva-translate-4b-instruct-v2",
                name="Riva Translate 4B",
                provider="NVIDIA NIM",
                description="Yüksek doğruluklu nöral çeviri ve dilbilim motoru; 150 ms rekor gecikmeyle kusursuz çok dilli yerelleştirme.",
                category="Çeviri & Dilbilim (NVIDIA Riva)",
                context_length=32000,
                is_available=True,
                is_default=False,
                tags=["translation", "linguistics", "multilingual"]
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
