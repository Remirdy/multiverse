import re
from typing import Dict, List
from app.schemas.router import RouteResponse

CATEGORY_CONFIG = {
    "vision_circuit": {
        "label": "Görsel & Devre Şeması Analizi (Vision Modelleri)",
        "keywords": [
            "görsel", "görselde", "devre", "şema", "şeması", "resim", "fotoğraf", "çizim", "diyagram",
            "diyot", "transistör", "şekil", "şekildeki", "circuit", "diagram", "schematic", "diode",
            "transistor", "voltage", "current", "resistor", "image", "photo", "pdf", "direnç", "akım", "gerilim", "zener"
        ],
        "regex": [r"\b(?:Vo|Vin|Vout|Vcc|Vee|GND|I[1-9]|V[1-9]|I_[a-zA-Z0-9]+|V_[a-zA-Z0-9]+)\b", r"\bgörsel\w*\b", r"\bşema\w*\b", r"\bdevre\w*\b"],
        "recommended_models": [
            "nvidia/nemotron-3.5-super-vl-120b-a12b",
            "meta/llama-3.2-90b-vision-instruct"
        ],
        "description": "Devre şemalarını ve çizimleri piksel düzeyinde inceleyen Vision modelleri (Nemotron Super VL & Llama 3.2 Vision) hedeflendi."
    },
    "programming": {
        "label": "Yazılım & Kod Geliştirme (Claude Sonnet Muadili)",
        "keywords": [
            "code", "function", "debug", "bug", "python", "javascript", "typescript", "react", "fastapi",
            "sql", "database", "api", "class", "algorithm", "git", "syntax", "array", "compiler",
            "regex", "async", "await", "docker", "json", "html", "css", "interface", "pointer", "kod"
        ],
        "regex": [r"\bdef\s+\w+\(", r"\bfunction\s+\w+\(", r"\bconst\s+\w+\s*=", r"\bimport\s+[\w\.]+", r"```[\w]*\n"],
        "recommended_models": [
            "poolside/laguna-xs-2.1",
            "nvidia/nemotron-3.5-lightning-30b-a3b"
        ],
        "description": "Sonnet 5.5 kalibresinde saf kodlama ve algoritma uzmanı Poolside Laguna XS hedeflendi."
    },
    "mathematics": {
        "label": "Matematik & Formel Mantık (GPT-5 Reasoning Muadili)",
        "keywords": [
            "calculate", "equation", "derivative", "integral", "matrix", "algebra", "probability",
            "statistics", "theorem", "proof", "geometric", "calculus", "polynomial", "eigenvalue",
            "combinatorics", "logarithm", "prime", "fraction", "formula", "arithmetic", "matematik", "denklem"
        ],
        "regex": [r"\b\d+[\+\-\*\/\^]\d+\b", r"[∫∑∏√πθλ]", r"\bx\s*[\+\-\=]\s*y\b", r"\bf\(x\)\s*="],
        "recommended_models": [
            "nvidia/nemotron-3.5-lightning-30b-a3b",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
        ],
        "description": "GPT-5 Reasoning kalibresinde hızlı matematik motoru Nemotron 3.5 Lightning hedeflendi."
    },
    "scientific_reasoning": {
        "label": "Deneysel Bilim & STEM (4-Hydrogen Muadili)",
        "keywords": [
            "hypothesis", "quantum", "physics", "chemistry", "biology", "molecule", "genetics",
            "thermodynamics", "astrophysics", "experiment", "entropy", "relativity", "particle",
            "evolution", "neuroscience", "reaction", "laboratory", "simulation", "cellular", "fizik", "kimya"
        ],
        "regex": [r"\bH2O\b", r"\bCO2\b", r"\bE\s*=\s*mc\^?2\b"],
        "recommended_models": [
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
            "nvidia/nemotron-3-ultra-550b-a55b"
        ],
        "description": "4-Hydrogen kalibresinde adım adım bilimsel çıkarım yapan Nemotron Nano Omni hedeflendi."
    },
    "frontier_synthesis": {
        "label": "Derin Sentez & Felsefe (Claude Opus Muadili)",
        "keywords": [
            "philosophy", "cosmology", "civilization", "epistemology", "paradox", "existential",
            "macroeconomics", "historical", "deep dive", "felsefe", "tarih", "kavramsal"
        ],
        "regex": [],
        "recommended_models": [
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
        ],
        "description": "Claude Opus kalibresinde 550 Milyar parametreli Nemotron 3 Ultra hedeflendi."
    },
    "robotics_engineering": {
        "label": "Robotik & Sistem Mühendisliği (4-Argon Muadili)",
        "keywords": [
            "robotics", "robot", "kinematics", "actuator", "servo", "sensor", "motor", "pid",
            "control system", "microcontroller", "arduino", "raspberry pi", "torque", "cad",
            "circuit", "voltage", "current", "embedded", "ros", "lidar", "odometry", "schematic"
        ],
        "regex": [r"\bROS\b", r"\bPWM\b", r"\bGPIO\b", r"\bPCB\b"],
        "recommended_models": [
            "nvidia/nemotron-3.5-super-vl-120b-a12b",
            "nvidia/nemotron-3.5-bolt-e4b"
        ],
        "description": "4-Argon kalibresinde 120B robotik ve donanım motoru Nemotron Super VL hedeflendi."
    },
    "translation_linguistics": {
        "label": "Çeviri & Nöral Dilbilim (Riva)",
        "keywords": [
            "translate", "çevir", "çeviri", "translation", "turkish", "english", "spanish", "german",
            "french", "japanese", "grammar", "idiom", "localization", "meaning in"
        ],
        "regex": [r"\btranslate\b", r"\bçevir\b", r"\binto english\b", r"\btürkçe'ye\b"],
        "recommended_models": [
            "nvidia/riva-translate-4b-instruct-v2",
            "nvidia/nemotron-3.5-bolt-e4b"
        ],
        "description": "150 ms ultra hızlı nöral dil çevirmeni NVIDIA Riva Translate hedeflendi."
    },
    "fast_flash": {
        "label": "Ultra Hızlı & Özet (Gemini Flash Muadili)",
        "keywords": [
            "quick", "fast", "summary", "summarize", "bullet points", "briefly", "short", "overview", "hızlı", "özet"
        ],
        "regex": [],
        "recommended_models": [
            "nvidia/nemotron-3.5-bolt-e4b",
            "poolside/laguna-xs-2.1"
        ],
        "description": "Gemini 3.8 Flash kalibresinde 200 ms sub-second motoru Nemotron 3.5 Bolt hedeflendi."
    }
}

class RoutingService:
    def classify(self, prompt: str) -> RouteResponse:
        cleaned_prompt = prompt.lower()
        scores: Dict[str, float] = {}

        for category, config in CATEGORY_CONFIG.items():
            score = 0.0
            for kw in config["keywords"]:
                if kw in cleaned_prompt:
                    score += 1.5

            for pattern in config.get("regex", []):
                if re.search(pattern, prompt, re.IGNORECASE):
                    score += 3.0

            scores[category] = score

        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]

        if max_score < 1.0:
            best_category = "fast_flash"
            confidence = 0.65
        else:
            confidence = min(round(0.60 + (max_score * 0.08), 2), 0.98)

        cfg = CATEGORY_CONFIG[best_category]
        return RouteResponse(
            category=best_category,
            category_label=cfg["label"],
            confidence=confidence,
            reasoning=f"{cfg['label']}: {cfg['description']}",
            recommended_model_ids=cfg["recommended_models"]
        )

routing_service = RoutingService()
