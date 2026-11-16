# 🌌 MULTIVERSE — Multi-Model AI Platform

<div align="center">

<img src="./frontend/public/logo.svg" alt="Multiverse Orbital Logo" width="96" height="96" />

### *"One question. Multiple minds."*

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite_6-646CFF?style=for-the-badge&logo=vite&logoColor=FFD62E)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA_NIM-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://build.nvidia.com)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 Overview

**Multiverse** is an advanced multi-model AI exploration and comparison platform. Instead of asking one model at a time, Multiverse dispatches a single prompt simultaneously across multiple frontier AI models and displays their reasoning steps, diverse viewpoints, and response latencies in an elegant, responsive side-by-side comparison grid.

Powered by the **NVIDIA Build (NVIDIA NIM API)** cloud infrastructure and built on a high-throughput asychronous **FastAPI** backend paired with a dark-first **React + TypeScript** interface.

---

## ✨ Key Features

### 🚀 1. Simultaneous Multi-Model Comparison
- **Parallel Dispatch**: Queries between 1 and 6 models concurrently using `asyncio.gather(*tasks, return_exceptions=True)`.
- **Latency Benchmarking**: Measures and displays exact response duration per model in milliseconds (`ms`).
- **Independent Loading States**: Each card features its own reactive skeleton loader while processing.
- **Partial Failure Resilience**: A timeout or rate-limit on one model never drops the successful responses of the others.
- **Single Model Retry**: Failed or timed-out models can be re-queried individually with a single click without resending the entire prompt to all models.
- **One-Click Copy**: Copy formatted answers and code snippets instantly.

### 🧠 2. AI Model Registry & Verified Endpoints
Centralized model registry managing verified, production-ready NVIDIA NIM models:
| Model Name | Model ID | Category | Primary Strength | Context Window |
| :--- | :--- | :--- | :--- | :--- |
| **Nemotron 3.5 Lightning** | `nvidia/nemotron-3.5-lightning-30b-a3b` | Mathematics & Logic | High-speed mathematical reasoning & logic | 128k |
| **Mistral Large 4** | `mistralai/mistral-large-4-1t-a52b` | Creative & Multilingual | Literary writing, nuanced style & translation | 128k |
| **Poolside Laguna XS** | `poolside/laguna-xs-2.1` | Programming & Code | Algorithms, debugging & systems architecture | 64k |
| **Nemotron 3.5 Bolt** | `nvidia/nemotron-3.5-bolt-e4b` | Fast & Lightweight | Sub-second latency & quick answers | 64k |
| **Nemotron Nano Omni** | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | Scientific Reasoning | Deep empirical analysis & step-by-step thinking | 128k |
| **Nemotron Super VL 120B** | `nvidia/nemotron-3.5-super-vl-120b-a12b` | Engineering & Multimodal | Large-scale STEM & robotics systems analysis | 128k |
| **Meta Muse Glimmer 30B** | `meta/muse-glimmer-30b` | Creative Synthesis | Conceptual synthesis & storytelling | 128k |

### 🎯 3. Smart Semantic Routing (Automatic Model Routing)
Includes an integrated semantic intent classifier analyzing prompts across 8 distinct domains:
1. **Programming & Code** (Python, SQL, React, APIs, algorithms, debugging)
2. **Mathematics & Logic** (Algebra, calculus, proofs, linear equations)
3. **Scientific Reasoning** (Physics, quantum mechanics, chemistry, biology)
4. **Robotics & Engineering** (Control systems, ROS, kinematics, circuits)
5. **Creative Writing** (Narratives, poetry, screenplays, worldbuilding)
6. **Image & Vision Understanding** (Multimodal analysis, visual reasoning)
7. **General Knowledge & Concept Synthesis** (Broad inquiries, summaries)

*Toggle the **"Smart Route"** mode in the chat interface to have Multiverse automatically target the best models for your query.*

### 💾 4. Persistent SQLite Conversation History
- Asynchronous database layer using **SQLAlchemy 2.0** and **aiosqlite**.
- Stores every conversation, prompt, system instruction, and model response with full metadata (status, latency, timestamps).
- Clean conversation sidebar: create new comparisons, browse past sessions, or delete them anytime.

### 🎨 5. Premium UI/UX Design
- **Dark-First Aesthetic**: Deep charcoal (`#070A10`), subtle slate borders (`#1E293B`), and cyan/violet accents (`#38BDF8`, `#818CF8`).
- **Markdown & Syntax Highlighting**: Full GitHub Flavored Markdown (GFM) support with tables, quotes, lists, and syntax-styled code blocks with copy buttons.
- **Original Orbital Logo**: Custom-crafted SVG identity symbolizing multiple planetary minds orbiting a central singularity.

---

## 🏗️ Architecture & Project Structure

```
multiverse/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints
│   │   │   ├── compare.py   # Multi-model concurrent comparison & retry
│   │   │   ├── conversations.py # Conversation CRUD operations
│   │   │   ├── models.py    # Model registry & provider health
│   │   │   └── router.py    # Semantic automatic routing
│   │   ├── core/            # Configuration & Settings (Pydantic, .env)
│   │   ├── database/        # Async SQLAlchemy session & SQLite ORM models
│   │   ├── providers/       # BaseProvider abstraction, NVIDIA NIM client, registry
│   │   ├── schemas/         # Pydantic schemas (CompareRequest, TurnDetail, etc.)
│   │   ├── services/        # Comparison execution engine & routing classifier
│   │   └── main.py          # Application entrypoint & CORS middleware
│   ├── tests/               # Pytest test suite (12 passed tests)
│   ├── requirements.txt     # Backend Python dependencies
│   ├── pytest.ini           # Asynchronous pytest configuration
│   └── .env.example         # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components (Header, Sidebar, ComparisonCard, etc.)
│   │   ├── services/        # Typed API service
│   │   ├── types/           # TypeScript definitions
│   │   ├── App.tsx          # Main application coordinator
│   │   ├── index.css        # Tailwind styling & custom scrollbars
│   │   └── main.tsx         # React root
│   ├── public/              # Static assets (logo.svg)
│   ├── index.html           # HTML5 template
│   ├── package.json         # Frontend packages
│   ├── tailwind.config.js   # Tailored theme colors
│   └── vite.config.ts       # Vite configuration with API reverse proxy
│
├── start.sh                 # One-click launcher script
├── README.md                # Project documentation
└── .gitignore               # Strict gitignore excluding API keys & environments
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** (Tested on Python 3.14)
- **Node.js 18+** & **npm**
- An **NVIDIA NIM API Key** (Free developer trial available at [build.nvidia.com](https://build.nvidia.com/))

---

### Option 1: Quickstart (One-Click Script)

Clone the repository and run the launch script:

```bash
git clone https://github.com/zeynepiremakbulut/multiverse.git
cd multiverse

# Run the automated launcher
./start.sh
```

---

### Option 2: Manual Setup

#### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your NVIDIA API Key
cp .env.example .env
```

Edit `backend/.env` with your API key:
```env
NVIDIA_API_KEY=nvapi-your-key-here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
DEFAULT_TIMEOUT_SECONDS=45.0
MAX_CONCURRENT_MODELS=6
DATABASE_URL=sqlite+aiosqlite:///./multiverse.db
```

Start the FastAPI server:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend Swagger interactive docs will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).*

#### 2. Frontend Setup
In a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Open your browser at **[http://localhost:5173](http://localhost:5173)**.

---

## 🧪 Automated Testing

Multiverse includes automated tests covering registry validation, semantic routing, API endpoints, and error handling:

```bash
cd backend
source venv/bin/activate
pytest -v
```

Expected output:
```
tests/test_api.py::test_root_endpoint PASSED
tests/test_api.py::test_list_models PASSED
tests/test_api.py::test_route_endpoint PASSED
tests/test_api.py::test_create_and_list_conversations PASSED
tests/test_api.py::test_compare_prompt PASSED
tests/test_registry.py::test_registry_has_models PASSED
tests/test_registry.py::test_default_models PASSED
tests/test_registry.py::test_model_metadata PASSED
tests/test_routing.py::test_route_programming PASSED
tests/test_routing.py::test_route_mathematics PASSED
tests/test_routing.py::test_route_creative PASSED
tests/test_routing.py::test_route_robotics PASSED

============================== 12 passed in 2.98s ==============================
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/models` | List all available models and default selections |
| `GET` | `/api/models/health` | Check NVIDIA NIM connectivity & key configuration |
| `POST` | `/api/compare` | Send prompt to multiple models concurrently |
| `POST` | `/api/compare/retry` | Retry an individual failed model for a given turn |
| `POST` | `/api/route` | Classify query intent and return recommended models |
| `GET` | `/api/conversations` | List saved conversation history |
| `POST` | `/api/conversations` | Create a new conversation |
| `GET` | `/api/conversations/{id}`| Retrieve full comparison turns and responses |
| `DELETE`| `/api/conversations/{id}`| Delete a conversation and its turns |

---

## 🔒 Security & Privacy

- **Zero Key Exposure**: API keys are strictly confined to `backend/.env` and are never sent to or visible in client-side code.
- **Git Shield**: `.gitignore` strictly protects `.env` files from accidental commits.
- **Sanitized Diagnostics**: If an API error, rate limit, or invalid key occurs, sanitized user-friendly guidance is returned without leaking internal stack traces.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
Built with ❤️ for the Multiverse platform.
