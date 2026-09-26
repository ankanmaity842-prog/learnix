
<div align="center">

# 🎓 Learnix

### AI-Powered Personalized Video Learning Platform

Turns YouTube into a structured, adaptive curriculum — search a topic, get ranked videos, auto-generated notes, quizzes, a knowledge graph of prerequisites, and a difficulty level tuned to *you*.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-SQLAlchemy-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=for-the-badge)

[Overview](#-overview) • [Features](#-features) • [Architecture](#-architecture) • [Tech Stack](#-tech-stack) • [Getting Started](#-getting-started) • [API](#-api-overview) • [Project Structure](#-project-structure)

</div>

---

## 📖 Overview

**Learnix** is a full-stack learning platform that transforms the open ocean of YouTube videos into a **personalized, structured learning path**.

Instead of manually hunting for the "right" tutorial, a learner types in what they want to learn (e.g. *"binary search trees"*), and Learnix runs it through an **AI pipeline** that:

1. Understands the **topic**, its **prerequisites**, and related subtopics
2. Builds/updates a **knowledge graph** connecting concepts
3. Pulls and ranks **YouTube videos** using transcript + visual analysis
4. Scores content **difficulty** and matches it to the learner's level
5. Generates **notes**, **quizzes**, and tracks **progress** over time

It supports **multiple languages** (English, Bengali, Hindi), works across **video, text, and quiz** modalities, and layers **computer vision** on top of video frames to detect slides, code, and diagrams — giving a much richer understanding of *what* a video actually teaches, not just its title and description.

> Think of it as a personal AI tutor that curates the internet's best videos into a syllabus made just for you.

---

## ✨ Features

### 🔍 Smart, Pipeline-Driven Search
- Natural language topic search (`"explain recursion"`, `"react hooks"`, etc.)
- Automatic **topic classification** with detected domain & difficulty
- Multi-language support: **English, Bengali (bn), Hindi (hi)**
- Learner-level aware ranking (`beginner` / `intermediate` / `advanced`)

### 🧠 AI & Machine Learning
- **Knowledge Graph** — auto-builds prerequisite → topic → subtopic relationships as users search
- **Difficulty Classifier** — ML model (with heuristic fallback) scores content difficulty from transcript text
- **Recommendation Engine** — RandomForest-based model ranks videos by relevance to the learner
- **Knowledge Gap Detection** — identifies what a learner is missing before recommending next steps
- **Semantic Search & Embeddings** — sentence-transformer embeddings for concept similarity
- **Gemini-powered** content understanding (Google `google-genai` SDK)

### 🎥 Video Intelligence (Computer Vision)
- Frame extraction & scene detection from YouTube videos
- Slide detection, diagram detection, and on-screen code detection
- Text detection (OCR via `pytesseract`) and visual complexity scoring
- Combined transcript + visual analysis per video

### 📝 Learning Tools
- **Auto-generated Notes** from video transcripts
- **Adaptive Quizzes** tied to topics/videos with scoring
- **Progress Tracking** with dashboards and completion history
- **Learning Paths** sequenced by the knowledge graph's prerequisite chain

### 🔐 Authentication & Accounts
- Email/username + password auth with **JWT** sessions
- **Google OAuth 2.0** sign-in
- Forgot / reset password flow (email-based tokens)
- Profile & settings management

### 🌐 Multilingual Support
- Language detection, language-aware routing
- Multilingual embeddings, quiz generation, and summarization

### 🎨 Frontend Experience
- Responsive **React 19** SPA with protected routes
- Light/dark theming via context
- Reusable component library: video cards/grids, progress charts, knowledge maps, difficulty badges, and more

---

## 🏗 Architecture

Learnix follows a **decoupled client–server architecture**: a React SPA talks to a FastAPI backend over a REST API; the backend orchestrates AI/ML models, a computer-vision pipeline, and external services (YouTube, Gemini, Google OAuth), backed by PostgreSQL.

```mermaid
flowchart TB
    subgraph Client["Frontend - React 19 + Vite"]
        UI[Pages and Components]
        CTX["Context: Auth / Theme / Language"]
        SVC[Service Layer - Axios]
        UI --> CTX
        UI --> SVC
    end

    subgraph API["Backend - FastAPI"]
        MW["Middleware: CORS, Logging, Rate Limiting"]
        ROUTES["API Routers: auth, search, videos, learning, notes, quiz, progress, knowledge, vision"]
        CORE["Core: Security, Cache, Exceptions"]
        MW --> ROUTES --> CORE
    end

    subgraph AI["AI / ML Layer"]
        TC[Topic Classifier]
        KG[(Knowledge Graph)]
        DIFF[Difficulty Model]
        REC[Recommendation Model]
        GAP[Knowledge Gap Model]
        EMB[Embeddings and Semantic Search]
        GEM[Gemini Client]
    end

    subgraph CV["Computer Vision Pipeline"]
        FE[Frame Extractor]
        SD[Scene / Slide Detector]
        CD[Code / Diagram Detector]
        TD["Text Detector (OCR)"]
    end

    subgraph EXT["External Services"]
        YT[YouTube Data and Transcript API]
        GAUTH[Google OAuth]
        GAI[Google Gemini API]
    end

    subgraph DATA["Data Layer"]
        PG[(PostgreSQL)]
        ML[/Trained .pkl Models/]
    end

    SVC <-- REST/JSON --> MW
    ROUTES --> AI
    ROUTES --> CV
    AI --> DATA
    ROUTES --> EXT
    CV --> EXT
    ROUTES -- SQLAlchemy --> PG
    DIFF --> ML
    REC --> ML
    GAP --> ML
```

### Request lifecycle — Search flow

The search endpoint is the heart of the system, chaining together language detection, topic understanding, the knowledge graph, YouTube retrieval, transcript extraction, and personalized ranking into one pipeline:

```mermaid
sequenceDiagram
    participant U as User
    participant F as React Frontend
    participant B as FastAPI Backend
    participant AI as Topic Classifier
    participant KG as Knowledge Graph
    participant YT as YouTube Service
    participant R as Recommendation Model

    U->>F: Type search query + level + language
    F->>B: GET /api/search?q=...&level=...&language=...
    B->>AI: classify(query, language)
    AI-->>B: topic, prerequisites, subtopics, difficulty
    B->>KG: add_topic(topic, prerequisites, subtopics)
    KG-->>B: updated learning_path
    B->>YT: search_videos(query variants)
    YT-->>B: candidate videos
    B->>B: fetch transcripts and dedupe
    B->>R: rank_videos(videos, topic, level)
    R-->>B: ranked recommendations
    B-->>F: topic, difficulty, learning_path, recommendations
    F-->>U: Render ranked video results
```

### Architectural principles

| Principle | How Learnix applies it |
|---|---|
| **Separation of concerns** | Frontend (presentation), Backend API (orchestration), AI layer (intelligence), CV pipeline (perception), Database (persistence) are all independently swappable |
| **Layered backend** | `api/` (routes) → `services/` (business logic) → `ai` / `computer_vision` (models) → `database/` (persistence) |
| **Stateless API** | JWT-based auth means any backend instance can serve any request — horizontally scalable |
| **Graceful ML degradation** | Every ML model (difficulty, recommendation) has a rule-based fallback if the trained `.pkl` model isn't available |
| **Async-first** | FastAPI + `httpx` async calls for non-blocking I/O to YouTube/Gemini APIs |

---

## 🛠 Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| **React 19** | Core UI library |
| **React Router 7** | Client-side routing & protected routes |
| **Vite 6** | Dev server & build tooling |
| **Axios** | HTTP client / API service layer |
| **Context API** | Auth, Theme (light/dark), and Language state |
| **CSS** | Component-scoped styling |

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | Async REST API framework |
| **Uvicorn** | ASGI server |
| **Pydantic / pydantic-settings** | Request validation & typed config/env management |
| **SQLAlchemy 2.0** | ORM for PostgreSQL |
| **Alembic** | Database migrations |
| **python-jose** | JWT creation & verification |
| **passlib + bcrypt** | Password hashing |
| **httpx** | Async HTTP calls to external APIs |

### AI / Machine Learning
| Technology | Purpose |
|---|---|
| **google-genai (Gemini)** | LLM-powered topic & content understanding |
| **sentence-transformers** | Text embeddings for semantic search |
| **scikit-learn** | Difficulty classifier & recommendation model (RandomForest, etc.) |
| **joblib** | Model serialization (`.pkl`) |
| **langdetect** | Automatic language detection |
| **youtube-transcript-api** | Transcript extraction from YouTube videos |

### Computer Vision
| Technology | Purpose |
|---|---|
| **OpenCV (headless)** | Frame extraction, scene/slide/diagram detection |
| **pytesseract** | OCR — text detection in video frames |
| **Pillow** | Image processing utilities |

### Database
| Technology | Purpose |
|---|---|
| **PostgreSQL** | Primary relational datastore |
| **psycopg2-binary** | PostgreSQL driver |

### DevOps / Tooling
| Technology | Purpose |
|---|---|
| **pytest / pytest-asyncio** | Backend testing |
| **Alembic** | Schema version control |
| **Apache License 2.0** | Project license |

---

## 📁 Project Structure

```
learnix/
├── backend/
│   ├── app/
│   │   ├── ai/                 # Topic classifier, difficulty & recommendation models, knowledge graph
│   │   ├── api/                # FastAPI routers (auth, search, videos, quiz, notes, progress, etc.)
│   │   ├── computer_vision/    # Frame extraction, slide/code/diagram/text detectors
│   │   ├── core/                # Security, caching, logging, middleware, rate limiting
│   │   ├── database/            # DB connection, CRUD helpers, migrations
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── multilingual/        # Language detection, routing, multilingual NLP
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/             # Business logic layer (glue between API and AI/DB)
│   │   ├── utils/                 # Helpers, validators, scoring, text processing
│   │   ├── config.py             # Environment-based settings
│   │   └── main.py                # FastAPI app entrypoint
│   ├── alembic/                  # DB migration scripts
│   ├── tests/                     # Backend test suite
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/            # Reusable UI components (Navbar, Quiz, VideoCard, etc.)
│   │   ├── context/                # Auth / Theme / Language React contexts
│   │   ├── hooks/                   # Custom hooks (useAuth, useLearning, useTheme, etc.)
│   │   ├── pages/                    # Route-level pages (Home, Dashboard, Search, VideoLearning...)
│   │   ├── services/                  # Axios-based API service modules
│   │   ├── utils/                      # Constants, formatters, validators
│   │   └── App.jsx                     # Route definitions
│   └── package.json
│
├── data/datasets/                 # Training data for ML models
├── scripts/                         # Model training scripts (difficulty, recommendation, knowledge-gap)
└── LICENSE                           # Apache 2.0
```

---

## 🚀 Getting Started

### Prerequisites
- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** (running instance + connection URL)
- API keys: **YouTube Data API**, **Google Gemini API**, **Google OAuth Client**

### 1. Clone the repo
```bash
git clone https://github.com/ankanmaity842-prog/learnix.git
cd learnix
```

### 2. Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/` with:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/learnix
JWT_SECRET_KEY=your-secret-key
YOUTUBE_API_KEY=your-youtube-api-key
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
FRONTEND_URL=http://localhost:5173
```

Run migrations and start the server:
```bash
alembic upgrade head
uvicorn app.main:app --reload
```
Backend runs at **http://localhost:8000** (interactive docs at `/docs`).

### 3. Frontend setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at **http://localhost:5173**.

### 4. (Optional) Train ML models
```bash
cd scripts
python train_difficulty_model.py
python train_recommendation_model.py
python train_knowledge_gap_model.py
```

---

## 📡 API Overview

All routes are prefixed with `/api`. Full interactive docs are available at `/docs` (Swagger UI) once the backend is running.

| Router | Prefix | Responsibility |
|---|---|---|
| `auth` | `/api/auth` | Register, login, JWT, password reset |
| `google` | `/api/google` | Google OAuth flow |
| `search` | `/api/search` | Core AI search & recommendation pipeline |
| `videoes` | `/api/videos` | Video details, transcripts, video analysis |
| `recommendations` | `/api/recommendations` | Personalized content recommendations |
| `learning` | `/api/learning` | Learning session management |
| `notes` | `/api/notes` | Auto-generated & saved notes |
| `quiz` | `/api/quiz` | Quiz creation & attempts |
| `progress` | `/api/progress` | User progress tracking |
| `knowledge` | `/api/knowledge` | Knowledge graph & gap analysis |
| `vision` | `/api/vision` | Computer-vision video analysis |
| `language` | `/api/language` | Language detection & routing |

---

## 🗺 Data Model (Core Entities)

```mermaid
erDiagram
    USER ||--o{ PROGRESS : tracks
    USER ||--o{ LEARNING_SESSION : has
    USER ||--o{ KNOWLEDGE : owns
    USER ||--o{ RECOMMENDATION : receives
    TOPIC ||--o{ QUIZ : has
    TOPIC ||--o{ KNOWLEDGE_RELATIONSHIP : relates_to
    QUIZ ||--o{ QUIZ_QUESTION : contains
    VIDEO ||--o{ LEARNING_SESSION : used_in
```

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo, create a feature branch, and open a pull request describing your changes.

## 📄 License

Licensed under the **Apache License 2.0** — see [LICENSE](./LICENSE) for details.

---

<div align="center">
Made with ❤️ for learners everywhere — <strong>Learnix</strong>
</div>
