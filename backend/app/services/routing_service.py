import re
from typing import Dict, List
from app.schemas.router import RouteResponse

CATEGORY_CONFIG = {
    "programming": {
        "label": "Programming & Code",
        "keywords": [
            "code", "function", "debug", "bug", "python", "javascript", "typescript", "react", "fastapi",
            "sql", "database", "api", "class", "algorithm", "git", "syntax", "array", "compiler",
            "regex", "async", "await", "docker", "json", "html", "css", "interface", "pointer", "variable"
        ],
        "regex": [r"\bdef\s+\w+\(", r"\bfunction\s+\w+\(", r"\bconst\s+\w+\s*=", r"\bimport\s+[\w\.]+", r"```[\w]*\n"],
        "recommended_models": [
            "poolside/laguna-xs-2.1",
            "nvidia/nemotron-3.5-lightning-30b-a3b"
        ],
        "description": "Specialized code intelligence & architecture query targeted to Poolside Laguna XS."
    },
    "mathematics": {
        "label": "Mathematics & Logic",
        "keywords": [
            "calculate", "equation", "derivative", "integral", "matrix", "algebra", "probability",
            "statistics", "theorem", "proof", "geometric", "calculus", "polynomial", "eigenvalue",
            "combinatorics", "logarithm", "prime", "fraction", "formula", "arithmetic", "math"
        ],
        "regex": [r"\b\d+[\+\-\*\/\^]\d+\b", r"[∫∑∏√πθλ]", r"\bx\s*[\+\-\=]\s*y\b", r"\bf\(x\)\s*="],
        "recommended_models": [
            "nvidia/nemotron-3.5-lightning-30b-a3b",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
        ],
        "description": "Formal mathematical calculation & logic targeted to Nemotron 3.5 Lightning."
    },
    "scientific_reasoning": {
        "label": "Scientific Reasoning & Hypotheses",
        "keywords": [
            "hypothesis", "quantum", "physics", "chemistry", "biology", "molecule", "genetics",
            "thermodynamics", "astrophysics", "experiment", "entropy", "relativity", "particle",
            "evolution", "neuroscience", "reaction", "laboratory", "simulation", "cellular"
        ],
        "regex": [r"\bH2O\b", r"\bCO2\b", r"\bE\s*=\s*mc\^?2\b"],
        "recommended_models": [
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
            "nvidia/nemotron-3-ultra-550b-a55b"
        ],
        "description": "Empirical scientific deduction & theory targeted to Nemotron Nano Omni Reasoning."
    },
    "frontier_synthesis": {
        "label": "Frontier Synthesis & Deep Knowledge",
        "keywords": [
            "philosophy", "cosmology", "civilization", "epistemology", "paradox", "existential",
            "macroeconomics", "historical", "deep dive", "comprehensive analysis", "meta-analysis"
        ],
        "regex": [],
        "recommended_models": [
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
        ],
        "description": "Large-scale interdisciplinary synthesis targeted to 550B Parameter Nemotron Ultra."
    },
    "robotics_engineering": {
        "label": "Robotics & Hardware Systems",
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
        "description": "Hardware engineering & robotics dynamics targeted to Nemotron Super VL 120B."
    },
    "translation_linguistics": {
        "label": "Translation & Multilingual Linguistics",
        "keywords": [
            "translate", "çevir", "çeviri", "translation", "turkish", "english", "spanish", "german",
            "french", "japanese", "grammar", "idiom", "localization", "meaning in", "how do you say"
        ],
        "regex": [r"\btranslate\b", r"\bçevir\b", r"\binto english\b", r"\btürkçe'ye\b"],
        "recommended_models": [
            "nvidia/riva-translate-4b-instruct-v2",
            "nvidia/nemotron-3.5-bolt-e4b"
        ],
        "description": "High-accuracy cross-language translation targeted to NVIDIA Riva Translate."
    },
    "creative_writing": {
        "label": "Creative Writing & Literature",
        "keywords": [
            "story", "poem", "essay", "dialogue", "metaphor", "character", "plot", "screenplay",
            "narrative", "fiction", "novel", "rhyme", "haiku", "song", "creative", "prose", "şiir", "hikaye"
        ],
        "regex": [r"\bonce upon a time\b", r"\bchapter \d+\b", r"\bbir varmış bir yokmuş\b"],
        "recommended_models": [
            "minimaxai/minimax-m3.1-flash",
            "nvidia/nemotron-3-ultra-550b-a55b"
        ],
        "description": "Literary stylistics, worldbuilding & prose targeted to MiniMax M3.1 Flash."
    },
    "general_speed": {
        "label": "Fast General Inquiries & Summaries",
        "keywords": [
            "quick", "fast", "summary", "summarize", "bullet points", "briefly", "short", "overview", "tldr"
        ],
        "regex": [],
        "recommended_models": [
            "nvidia/nemotron-3.5-bolt-e4b",
            "poolside/laguna-xs-2.1"
        ],
        "description": "Sub-second instant turnaround & concise responses targeted to Nemotron 3.5 Bolt."
    }
}

class RoutingService:
    def classify(self, prompt: str) -> RouteResponse:
        cleaned_prompt = prompt.lower()
        scores: Dict[str, float] = {}

        for category, config in CATEGORY_CONFIG.items():
            score = 0.0
            # Keyword matches
            for kw in config["keywords"]:
                if kw in cleaned_prompt:
                    score += 1.5

            # Regex matches
            for pattern in config.get("regex", []):
                if re.search(pattern, prompt, re.IGNORECASE):
                    score += 3.0

            scores[category] = score

        # Determine winner
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]

        # Fallback to general speed if no specific domain marker detected
        if max_score < 1.0:
            best_category = "general_speed"
            confidence = 0.65
        else:
            confidence = min(round(0.60 + (max_score * 0.08), 2), 0.98)

        cfg = CATEGORY_CONFIG[best_category]
        return RouteResponse(
            category=best_category,
            category_label=cfg["label"],
            confidence=confidence,
            reasoning=f"Identified as {cfg['label']}: {cfg['description']}",
            recommended_model_ids=cfg["recommended_models"]
        )

routing_service = RoutingService()
