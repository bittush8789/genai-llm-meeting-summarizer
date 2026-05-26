# 📝 AI Meeting Notes Summarizer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.100.0%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/LangChain-1.3.1%2B-1C3C3A?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain" />
  <img src="https://img.shields.io/badge/MySQL-8.0%2B-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/ChromaDB-Vector-orange?style=for-the-badge&logo=databricks&logoColor=white" alt="ChromaDB" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <strong>An enterprise-grade, asynchronous full-stack application designed to transcribe conversational audio, perform parallel analytical summarization, extract structured deliverables, and index meetings into relational and high-dimensional vector databases.</strong>
</p>

---

## 📖 Table of Contents

- [1. Executive Summary & Value Proposition](#1-executive-summary--value-proposition)
- [2. Core Features](#2-core-features)
- [3. Architectural Design & System Flow](#3-architectural-design--system-flow)
- [4. Processing Pipeline Workflow](#4-processing-pipeline-workflow)
- [5. Technical Stack Specifications](#5-technical-stack-specifications)
- [6. Directory Architecture](#6-directory-architecture)
- [7. Functional Modules Overview](#7-functional-modules-overview)
- [8. API Specifications](#8-api-specifications)
- [9. Database Schema Design](#9-database-schema-design)
- [10. Frontend UI Design Systems](#10-frontend-ui-design-systems)
- [11. Quick-Start & Installation Guide](#11-quick-start--installation-guide)
- [12. Environmental Configurations](#12-environmental-configurations)
- [13. Future Roadmap](#13-future-roadmap)
- [14. Application Visual Previews](#14-application-visual-previews)
- [15. License](#15-license)

---

## 1. Executive Summary & Value Proposition

In modern corporate operational structures, post-meeting administrative tasks introduce significant friction. The **AI Meeting Notes Summarizer** is designed to address this inefficiency by automating the lifecycle of conversational data.

### 🚨 The Problem Statement
During typical business operational cycles, organizations encounter three primary bottlenecks:
1. **High Administrative Overhead**: Valuable engineering and managerial hours are lost manually compiling, editing, and formatting meeting minutes and distributing task notes.
2. **Action Item Decay & Ambiguity**: Deliverables, deadlines, and ownership assignments agreed upon verbally are frequently forgotten, misremembered, or lost, creating execution gaps.
3. **Siloed & Unsearchable Conversational Assets**: Historical decision contexts and meeting recordings remain locked in flat files or unindexed audio binaries, rendering organizational knowledge unsearchable.

### 💡 The Solution
This application introduces a unified **Asynchronous Processing Pipeline** that immediately converts verbal files or text transcripts into organized corporate database structures:
*   **Automatic Transcription & Parallel Analysis**: Instantly transcribes voice streams or processes text inputs, deploying parallel LLM chains to extract summaries, checklists, and decisions in seconds.
*   **Relational Action Checklist (MySQL)**: Commits meetings and structures tasks into an active checklist to ensure absolute delivery accountability.
*   **Semantic Retrieval Storage (ChromaDB)**: Chunks, encodes, and indexes transcripts into a persistent vector index, enabling instantaneous context retrieval for future semantic question-answering.

### Key Business Advantages
- **Elimination of Admin Friction**: Removes manual note-taking entirely, instantly converting conversation audio files or pasted notes into actionable insights.
- **Accurate Action Tracking**: Uses deep linguistic structure extraction to guarantee that all tasks, due dates, and assigned owners are categorized dynamically.
- **Corporate Knowledge Retrieval**: Leverages a dual-database pattern (relational transactional entries and high-dimensional semantic vectors) to create searchable archives of organizational intelligence.

---

## 2. Core Features

*   **Dual-Track Processing Modes**:
    *   *Option 1 (Audio Stream)*: Transcribe raw speech files (`WAV`, `MP3`, `M4A`, `OGG`, `FLAC` up to 50MB) using Whisper STT.
    *   *Option 2 (Direct Transcript)*: Paste raw meeting text directly to bypass speech-to-text, providing immediate test capability and raw analytical processing.
*   **Speech-to-Text Layer**: Run local, offline OpenAI Whisper (`base`/`tiny` weights running efficiently on CPU) or configure Groq cloud-based Whisper APIs.
*   **Modern AI Analysis (LCEL)**: Built on parallel LangChain Expression Language (LCEL) chains connected to high-performance inference models via Groq API.
*   **Action & Decision Engines**: Intelligent regex parsing and named-entity extraction to structure deliverables, complete with assignees and checkboxes.
*   **Transactional MySQL Layer**: Automatic database and relational schema setup to hold structural meeting metadata and checklists.
*   **Semantic ChromaDB Index**: Text splitting, paragraph normalization, and local vector generation using `sentence-transformers` (`all-MiniLM-L6-v2`) for vector indexing.
*   **Premium CSS Light-Theme UI**: A highly responsive single-page client interface built with micro-shadows, modern type hierarchies, responsive cards, and dynamic status bars.

---

## 3. Architectural Design & System Flow

The system employs a clean, modular full-stack architecture separating the client interface from the backend RESTful service layer:

```text
                                  +---------------------------------------+
                                  |            CLIENT INTERFACE           |
                                  |     (HTML5, CSS3, ES6 JavaScript)     |
                                  +---------+-------------------+---------+
                                            |                   |
                               Audio Stream | Form-Data         | Pasted Text
                                            v                   v
                                  +---------------------------------------+
                                  |         FASTAPI APP GATEWAY           |
                                  |           (REST Router, CORS)         |
                                  +---------+-------------------+---------+
                                            |                   |
                                   If Audio |                   | If Text / Direct
                                            v                   v
+-------------------------------------------+---+   +-----------+-----------------------+
|          SPEECH-TO-TEXT MACHINE           |   |       LANGCHAIN INFERENCE PIPES       |
|    (OpenAI Whisper Local / Cloud Engine)  |   |  (Parallel LCEL Extraction Chains)    |
+-------------------------------------------+---+   +-----------+-----------------------+
                                            |                   |
                                            +-------------------+
                                                                |
                                                                v
                                              [ Highly Structured JSON Outcome ]
                                                                |
                                  +-----------------------------+-----------------------------+
                                  |                                                           |
                                  v                                                           v
                     +----------------------------+                              +----------------------------+
                     |    MYSQL TRANSACTION DB    |                              |     CHROMADB VECTOR DB     |
                     | (Relational Checklist Core)|                              |  (Sentence-Transformer L6) |
                     +----------------------------+                              +----------------------------+
```

---

## 4. Processing Pipeline Workflow

The execution pipeline transforms input data through eight distinct processing states:

```text
[1. Submission] ==> [2. Validation] ==> [3. STT Engine] ==> [4. LCEL Pipeline]
   (Audio/Text)      (Headers/Sizes)      (Whisper CPU)      (Parallel Chains)
                                                                     |
                                                                     v
[8. DOM Render] <== [7. Chroma Index] <== [6. MySQL Save] <== [5. Inference]
  (Dynamic UI)       (Dense Vectors)      (Transactional)     (Structured JSON)
```

1.  **Ingestion**: Client initiates request by sending an audio binary or plain text payload via multipart form-data.
2.  **Gatekeeping**: FastAPI middleware validates format extensions, boundaries, and safety configurations.
3.  **Transcription (Audio track only)**: Whisper converts audio data into structured raw sentences. Paster track bypasses this state instantly.
4.  **Prompt Routing**: Raw text is converted into prompt records and routed to parallel LangChain Expression Language pipelines.
5.  **LLM Analytical Inference**: Parallel chains execute to produce summaries, extract decisions, and compile deliverables.
6.  **Transactional Commit**: PyMySQL processes records and updates table spaces with transactional meeting IDs.
7.  **Vector Embedding**: Sentence-Transformers vectorizes paragraph-chunks into 384-dimensional dense semantic representations and updates the Chroma collection.
8.  **DOM Rehydration**: JavaScript rehydrates the DOM, rendering active checklist elements and expanding sections.

---

## 5. Technical Stack Specifications

### Technology Core
| Tier | Technology | Selected Version | Rationale |
| :--- | :--- | :--- | :--- |
| **Frontend** | Pure HTML5 / CSS3 / ES6 | Native standards | Zero-dependency build footprint, maximized rendering speeds. |
| **Backend** | Python FastAPI / Uvicorn | `FastAPI 0.100+` | Asynchronous speed, Pydantic type safety, autogenerated Swagger. |
| **Orchestration** | LangChain Core / LCEL | `LangChain 1.3.1` | Modular pipe configurations (`|` operator), parallel runtime chains. |
| **Inference Core** | Groq Cloud API Client | `Groq 0.37+` | High-frequency inference execution speeds on LPU hardware. |
| **Speech-to-Text** | OpenAI Whisper (Local) | `Whisper 202506` | Offline CPU compliance, local cache capability. |
| **Relational DB** | MySQL Server | `MySQL 8.0` | Secure schemas, strict primary foreign key compliance, quick index reads. |
| **Vector DB** | ChromaDB Persistent Client | `ChromaDB 1.5.9` | In-process DB footprint, integrated sentence-transformer indexes. |

### Neural Models Utilized
*   **LLM Core**: `llama-3.3-70b-versatile` (Primary analytical parser) / `llama-3.1-8b-instant` (High-speed summarization fallback)
*   **STT Engine**: Local Whisper `base` (Offline, balanced CPU runtime) / Whisper `tiny` (Rapid execution CPU runtime)
*   **Embeddings**: Sentence-Transformers `all-MiniLM-L6-v2` (Local 384-dimensional dense retriever)

---

## 6. Directory Architecture

```text
ai-meeting-summarizer/
├── frontend/
│   ├── index.html        # Clean DOM architecture and typography interfaces
│   ├── style.css         # Minimalist, polished light-theme CSS variables
│   └── script.js         # RESTful integrations, DOM rehydration, & UX handlers
├── backend/
│   ├── main.py           # REST gateway, lifespan bindings, and CORS filters
│   ├── requirements.txt  # Explicitly locked library dependencies
│   ├── .env              # Critical environment values (Keys & SQL settings)
│   ├── database/
│   │   ├── mysql_db.py   # Transactional schemas, connection pool, and mutations
│   │   └── chroma_db.py  # Paragraph segmenters, transformers, and vector persistence
│   ├── services/
│   │   ├── transcription.py  # Local Whisper engines and cloud APIs wrappers
│   │   └── summarization.py  # Structured LangChain LCEL pipeline compilation
│   ├── uploads/          # Temporary directory for uploaded audio cache (Auto-created)
│   └── vectorstore/      # Persistent local database storage for vector nodes (Auto-created)
└── README.md
```

---

## 7. Functional Modules Overview

### Audio Processing Module
Handles transactional file writes to `backend/uploads/` with size safety limits (50MB). Auto-detects codecs and routes wave binaries to either the local machine CPU Whisper engine or cloud engines. Instantly initiates local cleaning tasks to flush temp arrays on finalization.

### AI Summarization Module
Built upon modular LangChain LCEL pipe orchestration. Coordinates executive summary templates, pipelines conversational meeting streams to ChatGroq servers, and returns structured markdown files.

### Action Extraction Module
Uses localized NLP logic and detailed prompting to convert unstructured meeting records into operational tasks. Parses sentences to isolate assigned owners and formats action points into checkable lists.

### Decision Extraction Module
Scans transcripts for agreements, approvals, and formal choices. Converts verbose statements into brief bulleted sentences and handles fallback logic if no decisions are explicitly stated.

### Vector Storage Module
Utilizes Sentence-Transformers to segment transcripts into unified paragraph blocks. Generates vector representations and inserts elements along with metadata references directly into the ChromaDB index.

---

## 8. API Specifications

### `POST /upload`
Triggers the full processing pipeline. Supports both audio upload and raw transcript text submissions.

#### Request Parameters (Multipart Form-Data)
*   `file` (*Optional Binary*): Conversational meeting recording audio.
*   `transcript_text` (*Optional String*): Pre-written or pasted transcript text notes.
*   `llm_model` (*String, default: "llama-3.3-70b-versatile"*): Selected analytical LLM model.
*   `transcription_model` (*String, default: "local-whisper-base"*): Selected speech-to-text model.

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "id": 42,
  "title": "Project Sync Notes",
  "transcript": "Today we discussed Kubernetes deployment...",
  "summary": "The team aligned on transitioning to AWS EKS...",
  "decisions": "AWS EKS approved for production deployment.",
  "action_items": [
    "Configure SSL by Friday (Rahul)",
    "Complete Terraform setup before Monday (Priya)"
  ]
}
```

---

## 9. Database Schema Design

Structured relational model generated inside the `meeting_summarizer` table space:

```sql
CREATE TABLE meetings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    transcript LONGTEXT,
    summary TEXT,
    decisions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE action_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    meeting_id INT NOT NULL,
    item TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 10. Frontend UI Design Systems

The client interface has been carefully styled to adhere to premium web product designs:
- **Clean Space Aesthetics**: Clean margins (`gap: 24px`), large white cards, and structured layouts reduce visual noise.
- **Harmony Color Palettes**: Leverages functional, refined CSS variables instead of stock colors:
  *   Primary Brand Accent: `#2563eb` (Deep Royal Blue)
  *   Subtle Borders: `#e2e8f0` (Clean Light Slate)
  *   Success States: `#10b981` (Premium Emerald Green)
- **Variable Typography**: Deeply integrated `Inter` typeface with variable thickness weights (`300` to `700`) for balanced content formatting.
- **UI Transitions & Glows**: Active text inputs receive clean focus glows (`3px outline with 15% opacity`) and buttons support micro-transitions (`0.2s cubic-bezier`).
- **Interactive Checklists**: Relational action item arrays render as premium checkable lists that apply visual strikethroughs instantly.

---

## 11. Quick-Start & Installation Guide

Ensure you have **Python 3.10+** and a running **MySQL Server** instance before starting.

### 1. Initialize Relational Storage
Create the transactional database inside your MySQL client:
```sql
CREATE DATABASE meeting_summarizer;
```

### 2. Configure Environment Configurations
Create a `.env` file in the `backend/` directory:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=meeting_summarizer
```

### 3. Establish Virtual Environment & Dependencies
```bash
# Navigate to the backend directory
cd backend

# Initialize Python virtual environment
python -m venv venv

# Activate venv (Windows PowerShell)
venv\Scripts\Activate.ps1

# Activate venv (Unix/macOS Bash)
source venv/bin/activate

# Install locked dependencies
pip install -r requirements.txt
```

### 4. Boot Application Server
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Navigate to: **`http://localhost:8000`**

---

## 12. Environmental Configurations

The system looks for key variables to bootstrap critical pipelines:
- `GROQ_API_KEY`: Groq API authorization token.
- `DB_HOST` / `DB_PORT`: Destination address and port space of the MySQL server.
- `DB_USER` / `DB_PASSWORD`: SQL server credential validation records.
- `DB_NAME`: Working database workspace (Defaults to `meeting_summarizer`).

---

## 13. Future Roadmap

- [ ] **Conversational RAG Panel**: Ask historical meeting questions directly from a slide-out sidebar interface.
- [ ] **Speaker Diarization**: Multi-speaker clustering using neural frequency weights to label participants.
- [ ] **WebSockets Audio Streaming**: Stream mic inputs directly from the browser window in real-time.
- [ ] **Multi-Language Support**: Real-time translations to Spanish, German, French, and Japanese.
- [ ] **Direct Platform Syncs**: Integrated webhooks to sync meetings to Jira, Slack, or Notion.

---

## 14. Application Visual Previews

### Application Dashboard & Manual Transcript Interface
![Application Dashboard](photo/image.png)

---

## 15. License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  <strong>AI Meeting Notes Summarizer</strong> — Transforming corporate speech data into structured organizational assets.
</p>
