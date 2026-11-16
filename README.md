# 🌌 MULTIVERSE — Frontier Multi-Model AI Platform

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

**Multiverse** is a multi-model AI comparison and exploration platform built strictly around **Next-Generation Frontier Intelligence**.

Instead of utilizing older-generation models, Multiverse puts the highest caliber frontier models side-by-side in real-time: **GPT-5**, **Claude Sonnet 5.5**, **Claude Opus 4.6**, **Gemini 3.8 Flash**, **4-Hydrogen**, **4-Argon**, and **Claude Sonnet 4.6**.

Powered by high-throughput enterprise engines on the **NVIDIA Build NIM API** and designed with an extensible multi-provider abstraction layer.

---

## 🎯 Frontier Model Roster & Specializations

| Model | Provider | Model ID | Primary Domain & Key Strength | Context Window |
| :--- | :--- | :--- | :--- | :--- |
| **Claude Sonnet 5.5** | Anthropic | `anthropic/claude-sonnet-5.5` | **Agentic Software Engineering & Code**: Recursive self-correction, refactoring, algorithms | 200k |
| **GPT-5** | OpenAI | `openai/gpt-5` | **Frontier Reasoning & Multi-step Planning**: Formal mathematical deduction, deep logic | 256k |
| **Gemini 3.8 Flash** | Google | `google/gemini-3.8-flash` | **Ultra-Fast Multimodal & High-Throughput**: Sub-second answers, massive context scaling | 1,000k (1M) |
| **Claude Opus 4.6** | Anthropic | `anthropic/claude-opus-4.6` | **Philosophy & Complex Systems Synthesis**: Nuanced academic thought, literature, humanities | 200k |
| **4-Hydrogen** | OpenAI Frontier | `openai/4-hydrogen` | **Empirical Science & Quantitative Research**: Physics, biochemistry, thermodynamic hypotheses | 256k |
| **4-Argon** | OpenAI Frontier | `openai/4-argon` | **Robotics, Hardware CAD & Dynamics**: Kinematics, ROS systems, PID control, schematics | 256k |
| **Claude Sonnet 4.6** | Anthropic | `anthropic/claude-sonnet-4.6` | **High-Precision Systems & Refactoring**: Strict algorithmic efficiency, clean architecture | 200k |

---

## ✨ Key Platform Features

- **Concurrent Multi-Model Execution**: Sends the same prompt simultaneously across up to 6 frontier models using `asyncio.gather(*tasks, return_exceptions=True)`.
- **Latency Benchmarking (ms)**: Real-time response duration measured down to the millisecond on each model card.
- **Smart Automatic Routing**: An integrated semantic classifier detects prompt intent (e.g. coding, math, science, robotics) and suggests or auto-targets the exact specialist model.
- **Partial Failure Resilience**: Independent timeout handling prevents a slow model from failing the comparison turn.
- **Single Model Retry**: One-click re-query for individual models without repeating the entire prompt.
- **SQLite Database Persistence**: Full conversation history, timestamps, prompts, and model responses stored locally via async SQLAlchemy 2.0.
- **Dark-First Modern UI**: Inspired by ChatGPT, Claude, and Perplexity with syntax-highlighted code blocks, one-click copying, and original orbital iconography.

---

## 🚀 Quickstart Guide

### Option 1: One-Click Launch Script
```bash
git clone https://github.com/zeynepiremakbulut/multiverse.git
cd multiverse

# Run the automated launcher
./start.sh
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure your API key
cp .env.example .env
# Insert your NVIDIA_API_KEY in backend/.env
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

The test suite validates the frontier registry, semantic routing, and API endpoints:

```bash
cd backend
source venv/bin/activate
pytest -v
```

Expected output:
```
============================== 12 passed in 3.12s ==============================
```

---

## 🔒 Security & Privacy

- **Zero API Key Leakage**: API keys remain strictly confined to `backend/.env` and are never exposed in frontend code.
- **Strict Gitignore**: `.gitignore` strictly protects `.env` files from being committed.
- **Sanitized Diagnostics**: Clear, user-friendly diagnostic guidance without exposing internal traces.

---

## 📄 License
MIT License. Built with ❤️ for the Multiverse platform.
