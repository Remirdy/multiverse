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

**Multiverse** is a multi-model AI exploration and comparison platform. Instead of relying on a single generalist model for every task, Multiverse is designed around **Domain Specialization**: each AI model is mapped strictly to its verified area of benchmark excellence.

When you send a prompt, Multiverse queries the specialized models concurrently, evaluates their divergent reasoning paths, and benchmarks their latencies side-by-side in real time.

---

## 🎯 Domain-Specialized Model Registry

> **Core Philosophy**: *"No single model for everything."* Models are chosen strictly based on verified stability, free API availability on NVIDIA Build NIM, and proven domain competence.

| Domain / Field | Specialist Model | Model ID | Latency | Key Strengths & Use Cases | Context |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **💻 Programming & Software** | **Poolside Laguna XS** | `poolside/laguna-xs-2.1` | **~550 ms** | Codebases, algorithms, debugging, syntax, systems architecture | 64k |
| **📐 Mathematics & Formal Logic** | **Nemotron 3.5 Lightning** | `nvidia/nemotron-3.5-lightning-30b-a3b` | **~1.3 s** | Calculus, eigenvalues, algebraic proofs, statistical deduction | 128k |
| **🔬 Scientific Hypotheses & STEM** | **Nemotron Nano Omni** | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | **~640 ms** | Step-by-step thinking traces for physics, chemistry, thermodynamics | 128k |
| **🌌 Frontier 550B Synthesis** | **Nemotron 3 Ultra 550B** | `nvidia/nemotron-3-ultra-550b-a55b` | **~1.1 s** | 550 Billion parameter deep academic synthesis, history, cosmology | 128k |
| **🤖 Robotics & Hardware CAD** | **Nemotron Super VL 120B** | `nvidia/nemotron-3.5-super-vl-120b-a12b` | **~910 ms** | Robotics kinematics, ROS, PID controllers, circuits & sensors | 128k |
| **🌍 Multilingual Linguistics** | **Riva Translate 4B** | `nvidia/riva-translate-4b-instruct-v2` | **~155 ms** | Sub-second high-accuracy translation, localization, cultural nuance | 32k |
| **✍️ Creative Writing & Fiction** | **MiniMax M3.1 Flash** | `minimaxai/minimax-m3.1-flash` | **~3.2 s** | Literary fiction, atmospheric worldbuilding, dialogue & poetry | 128k |
| **⚡ Instant Turnaround & Summaries** | **Nemotron 3.5 Bolt** | `nvidia/nemotron-3.5-bolt-e4b` | **~260 ms** | Sub-second conversational responses, executive summaries, rapid triage | 64k |

---

## ✨ Key Platform Features

### 🚀 1. Simultaneous Multi-Model Comparison
- **Parallel Dispatch**: Concurrently query up to 6 models using `asyncio.gather(*tasks, return_exceptions=True)`.
- **Latency Benchmarking**: Precise millisecond duration measured and displayed on every card.
- **Partial Failure Resilience**: If one endpoint experiences rate-limits or cold-starts, successful models are never lost.
- **Single Model Retry**: Failed or timed-out models can be re-queried individually with a single click.
- **Independent Loading States**: Smooth animated skeleton feedback for every model.

### 🧭 2. Automatic Smart Routing
Multiverse features a semantic intent classifier that analyzes your query and suggests or targets the best specialized models:
- When you type a coding problem (e.g., Python `asyncio`), it recommends **Poolside Laguna XS**.
- When you type a calculus problem (e.g., matrix eigenvalues), it recommends **Nemotron 3.5 Lightning**.
- When you ask for translation (e.g., into Turkish/English), it recommends **Riva Translate 4B**.
- When you ask about thermodynamics or physics, it recommends **Nemotron Nano Omni**.

### 💾 3. Persistent SQLite History
- Built with **SQLAlchemy 2.0** and **aiosqlite**.
- Stores complete multi-model turns, timestamps, prompts, responses, and latencies.
- Full sidebar conversation management (Create, Switch, Delete).

### 🎨 4. Design & Typography
- **Dark-First Modern UI**: Inspired by ChatGPT, Claude, and Perplexity with deep space tones and cyan/violet accents.
- **GitHub Flavored Markdown**: Full markdown rendering with tables, quotes, lists, and syntax-highlighted code blocks with copy buttons.
- **Original Identity**: Orbital logo symbolizing multiple specialized minds.

---

## 🛠️ Tech Stack

```
Frontend:
  - React 18 & TypeScript
  - Vite 6
  - Tailwind CSS 3
  - Lucide React Icons
  - React Markdown + Remark GFM

Backend:
  - Python 3.10+ (Tested on Python 3.14)
  - FastAPI
  - OpenAI Async Python SDK
  - SQLAlchemy 2.0 (aiosqlite)
  - Pydantic v2
  - Pytest & Pytest-Asyncio
```

---

## 🚀 Quickstart Guide

### 1. One-Click Launch Script
```bash
git clone https://github.com/zeynepiremakbulut/multiverse.git
cd multiverse

# Start both backend and frontend automatically
./start.sh
```

### 2. Manual Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure your NVIDIA API Key
cp .env.example .env
# Edit backend/.env and insert your NVIDIA_API_KEY from build.nvidia.com
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## 🧪 Automated Tests

The test suite validates model registry integrity, semantic domain routing, CRUD conversation history, and API resilience:

```bash
cd backend
source venv/bin/activate
pytest -v
```

Expected output:
```
============================== 12 passed in 2.69s ==============================
```

---

## 🔒 Security & Safe Credentials

- **API Key Isolation**: The NVIDIA API Key is read exclusively on the backend (`backend/.env`) and is never sent to the browser.
- **Git Shield**: `.env` and all credential variants are strictly ignored by `.gitignore`.
- **Sanitized Errors**: Safe diagnostic error messages prevent leakage of internal stack traces.

---

## 📄 License
MIT License. Built with ❤️ for the Multiverse platform.
