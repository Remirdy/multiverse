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

## 📖 Genel Bakış (Overview)

**Multiverse**, tek bir soruyu aynı anda birden fazla uzman yapay zeka modeline sorarak yanıtlarını, akıl yürütme adımlarını ve yanıt sürelerini yan yana karşılaştıran yeni nesil bir platformdur.

Multiverse, **resmi NVIDIA Build (NVIDIA NIM API)** altyapısını kullanır. Kapalı kaynaklı ve maliyetli modellere (Claude Sonnet, GPT-5, Claude Opus, Gemini Flash, 4-Hydrogen, 4-Argon) servet ödemek yerine, **NVIDIA NIM altyapısındaki gerçek ve yüksek performanslı muadillerini** devreye sokar:

---

## 🎯 NVIDIA NIM Frontier Muadilleri Tablosu

| Gerçek Model Adı (NVIDIA NIM) | Model ID | Frontier Kalibre & Muadili | Yanıt Süresi | Uzmanlık ve Odak Alanı |
| :--- | :--- | :--- | :--- | :--- |
| **Poolside Laguna XS** | `poolside/laguna-xs-2.1` | **Claude Sonnet 5.5 Muadili** | **~550 ms** | Saf kodlama, algoritmalar, hata ayıklama (debug) ve yazılım mimarisi. |
| **Nemotron 3.5 Lightning** | `nvidia/nemotron-3.5-lightning-30b-a3b` | **GPT-5 Reasoning Muadili** | **~1.3 sn** | Yüksek hızlı matematiksel ispatlar, kalkülüs, cebir ve formel mantık. |
| **Nemotron 3 Ultra 550B** | `nvidia/nemotron-3-ultra-550b-a55b` | **Claude Opus 4.6 Muadili** | **~1.1 sn** | 550 Milyar parametrelik devasa bilgi tabanı, felsefe, kozmoloji ve derin sentez. |
| **Nemotron 3.5 Bolt** | `nvidia/nemotron-3.5-bolt-e4b` | **Gemini 3.8 Flash Muadili** | **~260 ms** | 200 ms sub-second yanıt hızı, çok yönlü hızlı özetleme ve dinamik diyalog. |
| **Nemotron Nano Omni** | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | **4-Hydrogen Muadili** | **~640 ms** | Adım adım şeffaf çıkarım izleriyle fizik, kimya, termodinamik ve STEM hipotezleri. |
| **Nemotron Super VL 120B** | `nvidia/nemotron-3.5-super-vl-120b-a12b` | **4-Argon Muadili** | **~910 ms** | 120B çok modlu kapasite; robotik kinematiği, ROS sistemleri, PID kontrol ve CAD. |
| **Riva Translate 4B** | `nvidia/riva-translate-4b-instruct-v2` | **Nöral Çeviri & Dilbilim** | **~155 ms** | NVIDIA Riva yüksek doğruluklu nöral dil çevirmeni ve kültürel yerelleştirme. |

---

## ✨ Öne Çıkan Yetenekler

- **Eşzamanlı Karşılaştırma**: Tek soruyu 6 modele kadar aynı anda `asyncio.gather(*tasks, return_exceptions=True)` ile gönderir.
- **Milisaniye Cinsinden Gecikme Ölçümü (Latency ms)**: Her modelin yanıt süresi canlı olarak kart üzerinde görüntülenir.
- **Akıllı Semantik Yönlendirme (Smart Route)**: Sorunun niyetini (Kod, Matematik, Bilim, Robotik, Çeviri, Hızlı Özet) tespit eder ve uygun uzman modeli otomatik hedefler.
- **Tekil Model Tekrarı (Retry)**: Hata alan veya zaman aşımına uğrayan model için diğer yanıtlar bozulmadan tek tıkla tekrar çalıştırma.
- **Kalıcı SQLite Geçmişi**: SQLAlchemy 2.0 asenkron veritabanı ile tüm geçmiş turlar ve yanıtlar saklanır.
- **Koyu Tema & Modern Arayüz**: ChatGPT, Claude ve Perplexity kalitesinde şık karanlık arayüz, sözdizimi vurgulamalı kod blokları ve tek tıkla kopyalama.

---

## 🚀 Hızlı Başlangıç

### 1. Tek Komutla Başlatma
```bash
git clone https://github.com/zeynepiremakbulut/multiverse.git
cd multiverse

./start.sh
```

### 2. Manuel Kurulum

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env dosyasını oluşturup build.nvidia.com'dan aldığınız NVIDIA_API_KEY'i ekleyin:
cp .env.example .env

uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Tarayıcınızda **[http://localhost:5173](http://localhost:5173)** adresini açın.

---

## 🧪 Otomatik Testler

```bash
cd backend
source venv/bin/activate
pytest -v
```

Çıktı:
```
============================== 12 passed in 1.15s ==============================
```

---

## 📄 Lisans
MIT License. Multiverse platformu için geliştirilmiştir.
