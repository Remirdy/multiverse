import re
from typing import Dict, List, Tuple
from app.schemas.router import RouteResponse

CATEGORY_CONFIG = {
    "programming": {
        "label": "Programming & Code",
        "keywords": [
            "code", "function", "debug", "bug", "python", "javascript", "typescript", "react", "fastapi",
            "sql", "database", "api", "class", "algorithm", "git", "syntax", "array", "compiler",
            "regex", "async", "await", "docker", "json", "html", "css", "interface", "pointer"
        ],
        "regex": [r"\bdef\s+\w+\(", r"\bfunction\s+\w+\(", r"\bconst\s+\w+\s*=", r"\bimport\s+[\w\.]+", r"```[\w]*\n"],
        "recommended_models": [
            "poolside/laguna-xs-2.1",
            "nvidia/nemotron-3.5-lightning-30b-a3b"
        ],
        "description": "Software architecture, coding, and debugging query."
    },
    "mathematics": {
        "label": "Mathematics & Logic",
        "keywords": [
            "calculate", "equation", "derivative", "integral", "matrix", "algebra", "probability",
            "statistics", "theorem", "proof", "geometric", "calculus", "polynomial", "eigenvalue",
            "combinatorics", "logarithm", "prime", "fraction", "formula", "arithmetic"
        ],
        "regex": [r"\b\d+[\+\-\*\/\^]\d+\b", r"[∫∑∏√πθλ]", r"\bx\s*[\+\-\=]\s*y\b", r"\bf\(x\)\s*="],
        "recommended_models": [
            "nvidia/nemotron-3.5-lightning-30b-a3b",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
        ],
        "description": "Mathematical calculation, algebraic reasoning, or formal proof."
    },
    "scientific_reasoning": {
        "label": "Scientific Reasoning",
        "keywords": [
            "hypothesis", "quantum", "physics", "chemistry", "biology", "molecule", "genetics",
            "thermodynamics", "astrophysics", "experiment", "entropy", "relativity", "particle",
            "evolution", "neuroscience", "reaction", "laboratory", "simulation", "cellular"
        ],
        "regex": [r"\bH2O\b", r"\bCO2\b", r"\bE\s*=\s*mc\^?2\b"],
        "recommended_models": [
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
            "nvidia/nemotron-3.5-lightning-30b-a3b"
        ],
        "description": "Complex empirical science, theory, or advanced academic analysis."
    },
    "robotics_engineering": {
        "label": "Robotics & Engineering",
        "keywords": [
            "robotics", "robot", "kinematics", "actuator", "servo", "sensor", "motor", "pid",
            "control system", "microcontroller", "arduino", "raspberry pi", "torque", "cad",
            "circuit", "voltage", "current", "embedded", "ros", "lidar", "odometry"
        ],
        "regex": [r"\bROS\b", r"\bPWM\b", r"\bGPIO\b"],
        "recommended_models": [
            "nvidia/nemotron-3.5-super-vl-120b-a12b",
            "nvidia/nemotron-3.5-bolt-e4b"
        ],
        "description": "Mechanical, electrical, mechatronics, or robotic systems."
    },
    "creative_writing": {
        "label": "Creative Writing",
        "keywords": [
            "story", "poem", "essay", "dialogue", "metaphor", "character", "plot", "screenplay",
            "narrative", "fiction", "novel", "rhyme", "haiku", "song", "creative", "prose"
        ],
        "regex": [r"\bonce upon a time\b", r"\bchapter \d+\b"],
        "recommended_models": [
            "mistralai/mistral-large-4-1t-a52b",
            "meta/muse-glimmer-30b"
        ],
        "description": "Literary, stylistic, or imaginative composition."
    },
    "image_understanding": {
        "label": "Image & Vision Understanding",
        "keywords": [
            "image", "picture", "photo", "diagram", "visual", "look at", "ocr", "detect", "bounding box",
            "segmentation", "pixels", "infographic", "chart", "graph"
        ],
        "regex": [r"\b\[image\]\b", r"\.png\b|\.jpg\b|\.jpeg\b"],
        "recommended_models": [
            "nvidia/nemotron-3.5-super-vl-120b-a12b",
            "nvidia/nemotron-3.5-lightning-30b-a3b"
        ],
        "description": "Visual reasoning, perception, and multimodal analysis."
    },
    "general_knowledge": {
        "label": "General Knowledge & Reasoning",
        "keywords": [
            "what", "why", "how", "explain", "history", "compare", "summary", "summarize",
            "recommend", "overview", "definition", "who", "when", "where"
        ],
        "regex": [],
        "recommended_models": [
            "mistralai/mistral-large-4-1t-a52b",
            "nvidia/nemotron-3.5-bolt-e4b"
        ],
        "description": "Broad factual, informational, or conceptual inquiry."
    }
}

class RoutingService:
    def classify(self, prompt: str) -> RouteResponse:
        cleaned_prompt = prompt.lower()
        scores: Dict[str, float] = {}

        for category, config in CATEGORY_CONFIG.items():
            score = 0.0
            # Keyword match
            for kw in config["keywords"]:
                if kw in cleaned_prompt:
                    score += 1.5

            # Regex match
            for pattern in config.get("regex", []):
                if re.search(pattern, prompt, re.IGNORECASE):
                    score += 3.0

            scores[category] = score

        # Determine winner
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]

        # If no specific patterns detected, fallback to general knowledge
        if max_score < 1.0:
            best_category = "general_knowledge"
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
