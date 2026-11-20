# UdyamSathi — Project Progress & Deliverables Tracker

All 12 daily engineering milestones, evaluation requirements, and final capstone deliverables are **100% Complete and Closed**.

---

## 📋 Course Milestone Checklist (D01 – D12)

- [x] **Day 01: Python Foundations & Terminal CLI Menu**
  - [x] 200+ line Python & CLI Guide explaining syntax, variables, dictionaries, and error handling (`docs/day01_guide.md`, `day01/README.md`, `day01/day01_guide.md`).
  - [x] Interactive terminal scripts (`day01/day01_intro.py`, `day01/day01_menu.py`).
  - [x] Root project card in `README.md`.

- [x] **Day 02: Structured Records & Tabular Search**
  - [x] 20 normalized Bank of Maharashtra policy records in `data/records.json`.
  - [x] Enhanced tabular CLI in `app/cli.py` with search, category filtering, and statutory limit checks.
  - [x] 10 unit test suites in `tests/test_day2.py`.

- [x] **Day 03: Data Ingestion & Sanitization**
  - [x] Raw policy documents in `data/raw/` (Bank of Maharashtra PMEGP and CMEGP guidelines).
  - [x] Automated text extraction, statutory limit parsing, and metadata cleaning in `app/ingest.py`.

- [x] **Day 04: Hybrid Search & Vector Indexing**
  - [x] TF-IDF search implementation in `app/records.py` with cosine ranking.
  - [x] Persistent ChromaDB vector store in `app/vectorstore.py` with `all-MiniLM-L6-v2` embeddings.
  - [x] Multi-field schema indexing with `scheme_name` metadata isolation.

- [x] **Day 05: Transformer Architecture & Trilingual User Questions (Checkpoint 1)**
  - [x] Comprehensive LLM guide in `docs/how_llms_work.md` with Transformer encoder-decoder vs decoder-only Mermaid diagrams.
  - [x] 10 authentic entrepreneur questions in English, Marathi (मराठी), and Hindi (हिंदी) in `docs/user_questions.md` and `eval/user_questions.md`.
  - [x] Defensive refusal guardrail for Question 6 (live loan tracking) to prevent hallucination.
  - [x] Git tag `checkpoint-1` created and pushed.

- [x] **Day 06: Prompt Engineering & Systematic Evaluation**
  - [x] System Prompt comparison matrix in `eval/prompt_compare.md` evaluating Prompt A vs. Prompt B across 10 benchmark queries.
  - [x] 4-dimension, 8-point rubric (Groundedness, Completeness, Refusal Honesty, Numerical Accuracy).
  - [x] Search results audit documented in `eval/search_results.md`.

- [x] **Day 07: FastAPI REST API & Production Observability**
  - [x] FastAPI web service in `app/main.py` with `/health`, `/records`, `/ask`, and `/agent` endpoints.
  - [x] In-memory TTL query caching in `app/cache.py` with `X-Cache` headers and `/cache/stats` endpoint.
  - [x] High-precision latency timing and token accounting in `app/observability.py`.
  - [x] Strict 500-character input limits and prompt-injection regex guards in `app/security.py`.

- [x] **Day 08: RAG Benchmark & Chunking Optimization**
  - [x] Automated evaluation harness in `eval/run_eval.py` benchmarking Config A vs Config B across 15 test queries.
  - [x] Benchmark results recorded in `eval/eval_results.json` and `README.md` (Config B winner: 120 chars, top-5, 71.4% hit rate, 100% Q6 accuracy, 28ms latency).
  - [x] Deterministic rate calculator in `app/tools.py`.
  - [x] Fallback error handling tests in `tests/test_day8.py`.

- [x] **Day 09: LangGraph Agent & Human-in-the-Loop Workflow**
  - [x] Multi-agent orchestration in `app/graph.py` with `MemorySaver` checkpointing and approval interrupt node (`approval_required`).
  - [x] Intent routing in `app/agent_loop.py` switching between RAG retrieval and deterministic calculation tools.
  - [x] Specialized tools in `app/tools.py` (`margin_money_subsidy_calculator`, `msme_classification_checker`, `eligibility_criteria_checker`).
  - [x] Dedicated router in `app/agent_api.py`.
  - [x] 12 unit tests in `tests/test_day9.py`.

- [x] **Day 10: Streamlit Frontend & Checkpoint 2**
  - [x] 558-line interactive UI in `ui/app.py` with live scheme comparison cards, server switcher, telemetry pills, and citation cards.
  - [x] User thumbs up/down feedback logging to `data/feedback.json`.
  - [x] 15 comprehensive UI test cases (58 asserts) in `tests/test_day10.py`.
  - [x] Embedded UI screenshot in `README.md` (`docs/ui_screenshot.png`).
  - [x] Git tag `checkpoint-2` created and pushed.

- [x] **Day 11: Pytest Test Suite & Dockerization**
  - [x] 54 automated pytest tests with 163 assertions passing with 100% success rate across 5 test files.
  - [x] Multi-stage `Dockerfile` with CPU-only PyTorch optimization.
  - [x] Complete `docker-compose.yml` orchestrating FastAPI (port 8000) and Streamlit (port 8501).
  - [x] **Earned Tracker Star (`★ OK`) on Day 11**.

- [x] **Day 12: Cloud Deployment & CI/CD**
  - [x] Automated GitHub Actions CI workflow in `.github/workflows/ci.yml`.
  - [x] Live cloud deployment on Render: `https://udyamsaathi-14cw.onrender.com`.
  - [x] Zero-downtime health endpoint: `/health` returning `{"status":"ok"}`.
  - [x] Interactive OpenAPI / Swagger documentation: `/docs`.

---

## 🎓 Capstone & Interview Readiness

- [x] **Resume Highlights**: 3 production-grade bullets in `docs/resume.md`.
- [x] **Interview Preparation**: `docs/interview.md` containing:
  - 60-second elevator pitch.
  - Deep-dive technical narrative: *"The Hardest Problem — Multi-Scheme Isolation & Disambiguation between PMEGP & CMEGP"*.
  - 10 comprehensive answers to likely technical interview questions.
- [x] **Demo Rehearsals Conducted**:
  - **Rehearsal Run 1 (Local Full-Stack Flow)**:
    - FastAPI launched at `http://127.0.0.1:8000`.
    - Tested `/health`, `/records`, `/ask` with PMEGP manufacturing query, `/agent` approval request and calculation execution.
    - Result: Pass (100% accuracy, clean latency headers).
  - **Rehearsal Run 2 (Live Cloud & Streamlit Flow)**:
    - Tested live Render endpoint `https://udyamsaathi-14cw.onrender.com/health` (HTTP 200).
    - Executed comparative query (PMEGP vs CMEGP service sector caps).
    - Executed Q6 unanswerable loan status query (verified 100% defensive refusal: *"I don't know..."*).
    - Verified feedback recording to `data/feedback.json`.
    - Result: Pass (Zero errors, seamless user experience).
- [x] **Git Final Tag**: Tag `final` created and pushed to GitHub remote.

---
**Status**: All deliverables closed. Project is fully production-ready.
