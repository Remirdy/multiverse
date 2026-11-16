import re
from typing import Dict, List
from app.schemas.router import RouteResponse

CATEGORY_CONFIG = {
    "programming": {
        "label": "Software Engineering & Agentic Coding",
        "keywords": [
            "code", "function", "debug", "bug", "python", "javascript", "typescript", "react", "fastapi",
            "sql", "database", "api", "class", "algorithm", "git", "syntax", "array", "compiler",
            "regex", "async", "await", "docker", "json", "html", "css", "interface", "pointer", "refactor"
        ],
        "regex": [r"\bdef\s+\w+\(", r"\bfunction\s+\w+\(", r"\bconst\s+\w+\s*=", r"\bimport\s+[\w\.]+", r"```[\w]*\n"],
        "recommended_models": [
            "anthropic/claude-sonnet-5.5",
            "anthropic/claude-sonnet-4.6"
        ],
        "description": "Targeted to Claude Sonnet 5.5 for agentic software engineering and clean algorithmic architecture."
    },
    "mathematics": {
        "label": "Frontier Mathematics & Formal Logic",
        "keywords": [
            "calculate", "equation", "derivative", "integral", "matrix", "algebra", "probability",
            "statistics", "theorem", "proof", "geometric", "calculus", "polynomial", "eigenvalue",
            "combinatorics", "logarithm", "prime", "fraction", "formula", "arithmetic", "math"
        ],
        "regex": [r"\b\d+[\+\-\*\/\^]\d+\b", r"[∫∑∏√πθλ]", r"\bx\s*[\+\-\=]\s*y\b", r"\bf\(x\)\s*="],
        "recommended_models": [
            "openai/gpt-5",
            "openai/4-hydrogen"
        ],
        "description": "Targeted to GPT-5 for frontier mathematical proofs and multi-step deduction."
    },
    "scientific_reasoning": {
        "label": "Empirical Science & Quantitative Hypotheses",
        "keywords": [
            "hypothesis", "quantum", "physics", "chemistry", "biology", "molecule", "genetics",
            "thermodynamics", "astrophysics", "experiment", "entropy", "relativity", "particle",
            "evolution", "neuroscience", "reaction", "laboratory", "simulation", "cellular"
        ],
        "regex": [r"\bH2O\b", r"\bCO2\b", r"\bE\s*=\s*mc\^?2\b"],
        "recommended_models": [
            "openai/4-hydrogen",
            "openai/gpt-5"
        ],
        "description": "Targeted to 4-Hydrogen for empirical research, quantum mechanics, and physics."
    },
    "frontier_synthesis": {
        "label": "Philosophy & Deep Systems Synthesis",
        "keywords": [
            "philosophy", "cosmology", "civilization", "epistemology", "paradox", "existential",
            "macroeconomics", "historical", "deep dive", "comprehensive analysis", "meta-analysis"
        ],
        "regex": [],
        "recommended_models": [
            "anthropic/claude-opus-4.6",
            "openai/gpt-5"
        ],
        "description": "Targeted to Claude Opus 4.6 for pinnacle systems reasoning and philosophical depth."
    },
    "robotics_engineering": {
        "label": "Robotics & Hardware Systems Engineering",
        "keywords": [
            "robotics", "robot", "kinematics", "actuator", "servo", "sensor", "motor", "pid",
            "control system", "microcontroller", "arduino", "raspberry pi", "torque", "cad",
            "circuit", "voltage", "current", "embedded", "ros", "lidar", "odometry", "schematic"
        ],
        "regex": [r"\bROS\b", r"\bPWM\b", r"\bGPIO\b", r"\bPCB\b"],
        "recommended_models": [
            "openai/4-argon",
            "anthropic/claude-sonnet-5.5"
        ],
        "description": "Targeted to 4-Argon for systems engineering, robotics kinematics, and hardware dynamics."
    },
    "creative_writing": {
        "label": "Creative Writing & Humanities",
        "keywords": [
            "story", "poem", "essay", "dialogue", "metaphor", "character", "plot", "screenplay",
            "narrative", "fiction", "novel", "rhyme", "haiku", "song", "creative", "prose", "şiir", "hikaye"
        ],
        "regex": [r"\bonce upon a time\b", r"\bchapter \d+\b", r"\bbir varmış bir yokmuş\b"],
        "recommended_models": [
            "anthropic/claude-opus-4.6",
            "google/gemini-3.8-flash"
        ],
        "description": "Targeted to Claude Opus 4.6 for literary prose, character dialogues, and rich worldbuilding."
    },
    "fast_multimodal": {
        "label": "Fast Multimodal & High-Throughput General",
        "keywords": [
            "quick", "fast", "summary", "summarize", "bullet points", "briefly", "short", "overview",
            "translate", "çevir", "multimodal", "image", "compare"
        ],
        "regex": [],
        "recommended_models": [
            "google/gemini-3.8-flash",
            "openai/gpt-5"
        ],
        "description": "Targeted to Gemini 3.8 Flash for sub-second multimodal comprehension and fast answers."
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
            best_category = "fast_multimodal"
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
