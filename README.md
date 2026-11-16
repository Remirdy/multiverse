# MULTIVERSE — One Question. Multiple Minds.

<div align="center">

<img src="./frontend/public/logo.svg" alt="Multiverse Orbital Logo" width="96" height="96" />

### Multi-Model Comparison, Council Collaboration, Visual Workflows, and Study Lab

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite_6-646CFF?style=for-the-badge&logo=vite&logoColor=FFD62E)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---

## Overview

Multiverse is a local-first FastAPI, React, TypeScript, and SQLite platform for querying, collaborating across, automating, and learning with multiple language and vision models. It preserves side-by-side model comparison while adding three integrated workspaces built over a shared model execution engine, job/event tracker, deterministic verification tools, and content-hashed artifact storage:

- **Compare**: Concurrent multi-model querying, intent routing, prompt enhancement, web search grounding, attachment parsing, single-model retry, and arbiter synthesis.
- **Council**: Multi-model deliberation with built-in roles (`Chair`, `Researcher`, `Critic`, `Developer`, `Reviewer`, `Mathematician`, `Teacher`, `Fact Checker`), presets, independent parallel proposals, anonymized peer critique, bounded revision rounds, deterministic verification (`SymPy`, Python AST static checks, citation checking), preserved disagreements, Chair synthesis, member retry, fork, and downloadable reports (`PDF`, `DOCX`, `Markdown`, `JSON`).
- **Workflows**: Interactive visual DAG editor and accessible list inspector with node palette, 7 built-in templates, Kahn topological cycle rejection, conditional branching, bounded loops, human approval gates, SSRF-validated outbound webhooks, secret-stripped JSON import/export, node retry, and artifact generation.
- **Study Lab**: Organized into four workspaces:
  - **Solve & Learn**: Shared document intake (`PDF`, `DOCX`, `PPTX`, `TXT`, `MD`, `PNG`, `JPG`), Assignment Solver (`Direct`, `Step-by-Step`, `Hint Only`, `Tutor`, `Council Solve`), Homework Verifier (with `SymPy` symbolic equivalence checks), Interactive Tutor / Professor Mode, Language Tutor, and interactive deterministic tools (Algorithm & Graph step traces, Pseudocode generator, 1D/2D Math plotter & numerical methods, analytical DC/AC Circuit solver, isolated Python Code Lab, and KaTeX LaTeX live editor).
  - **Practice**: SM-2 spaced-repetition Flashcards with CSV/JSON export, Question Bank, and deterministic Exam Simulator.
  - **Materials**: Course Notebooks, page-grounded PDF Chat & research comparison, Mind Maps, Formula Sheets, Lecture Assistant, and Presentation Maker (`.pptx` export).
  - **Progress**: Real attempt-based Exam Analytics, Weakness Detector, and rule-based Study Planner with `.ics` export.

---

## Architecture

```text
multiverse/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routers (models, compare, conversations, router, upload, jobs, artifacts, council, workflows, study)
│   │   ├── core/           # Configuration & storage paths
│   │   ├── council/        # Council roles, presets, execution protocol, and reports
│   │   ├── database/       # Async SQLAlchemy engine (SQLite NullPool) and ORM models
│   │   ├── execution/      # ExecutionEngine, ExecutionBudget, local-only policy, JobManager
│   │   ├── exports/        # ReportLab PDF (Unicode TTF), DOCX, PPTX, Markdown, JSON, CSV, ICS exporters
│   │   ├── providers/      # NVIDIA NIM provider, LocalOpenAIProvider (Ollama/LM Studio/llama.cpp/MLX), ModelRegistry
│   │   ├── services/       # Comparison, routing, prompt enhancement, web search, artifact storage
│   │   ├── study/          # Document intake, solver, verifier, PDF chat, flashcards, exams, analytics, planner
│   │   ├── tools/          # SymPy math/numerical methods, algorithm traces, circuit solver, Python sandbox, document parser
│   │   └── workflows/      # Typed node catalog, 7 templates, DAG validator, safe templating, execution engine
│   └── tests/              # Unit, integration, adversarial, and export round-trip tests
└── frontend/
    └── src/
        ├── components/     # Shared Header, Sidebar, ChatInput, ComparisonGrid, ModelSelector, ApiKeyModal, MarkdownRenderer
        ├── features/
        │   ├── council/    # CouncilWorkspace
        │   ├── workflows/  # WorkflowsWorkspace (interactive canvas + accessible list mode)
        │   └── study/      # StudyLabWorkspace & InteractiveLearningPanel
        ├── i18n/           # English and Turkish localization
        └── services/       # Typed API client
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- At least one inference option:
  - An API key from [NVIDIA Build](https://build.nvidia.com) (configured in `backend/.env`), or
  - A local OpenAI-compatible inference server such as Ollama (`http://127.0.0.1:11434/v1`), LM Studio (`http://127.0.0.1:1234/v1`), `llama.cpp` server (`http://127.0.0.1:8080/v1`), or `mlx-lm` server (`http://127.0.0.1:8081/v1`).

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Optionally set NVIDIA_API_KEY in backend/.env
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

---

## Optional Local Tools & Hardware Notes

- **Local Inference**: Ollama, LM Studio, `llama.cpp`, and `mlx-lm` run models locally on your hardware (memory and compute vary by model quantization). Enable **Local-Only Mode** in the Providers & Policy modal to block external model calls.
- **Tesseract OCR (`tesseract`)**: Optional system binary for extracting text from scanned PDFs and uploaded images. When absent, Study Lab reports that local OCR is unavailable rather than fabricating OCR results.
- **Audio Transcription (`faster-whisper` / `whisper`)**: Optional Python packages for offline audio transcription in Lecture Assistant. Without them, Lecture Assistant operates on pasted or uploaded text transcripts.
- **Circuit Simulation (`ngspice`)**: Optional system binary. Built-in DC/AC circuit topologies run via an exact analytical solver and report whether `ngspice` is present on the host.

---

## Automated Testing & Verification

Run the backend test suite (uses explicit test-only provider fakes for deterministic workflow/Council/Study Lab tests without consuming paid API quota):

```bash
cd backend
./venv/bin/pytest -v
```

Verify frontend TypeScript compilation and production bundling:

```bash
cd frontend
./node_modules/.bin/tsc --noEmit && ./node_modules/.bin/vite build
```

---

## Security & Limitations

- **Server-Side Keys & Secret Stripping**: API keys are loaded server-side from `backend/.env` and excluded from browser bundles, logs, and workflow exports. Imported workflows strip secret-like keys and disable imported `code` and `webhook` nodes until approved by the owner.
- **SSRF & Sandbox Protections**: Webhook URLs reject private, loopback, link-local, and metadata IP ranges and disable HTTP redirects. Python Code Lab checks AST imports/calls and executes inside an isolated temporary directory without network access.
- **Local-First Scope**: Designed as a single-user local workspace; if deployed on a shared host, add authentication and per-user tenant isolation before exposing endpoints beyond localhost.
- **Disabled Placeholder Nodes**: `MCP Tool` and `Delay / Schedule` workflow nodes are marked unavailable unless an external MCP server or persistent job scheduler is configured.

---

## License

This project is open-source under the [MIT License](LICENSE).
