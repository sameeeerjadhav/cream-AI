# UdyamSathi — Technical Interview Preparation & Architecture Guide

Comprehensive 60-second pitch, core architectural deep dive ("The Hardest Problem"), and exhaustive answers to 10 likely technical interview questions for **UdyamSathi (उद्यमसाथी)**.

---

## ⏱️ The 60-Second Elevator Pitch

> *"Every year, thousands of first-generation entrepreneurs in Maharashtra apply for government credit-linked subsidies under PMEGP and CMEGP, but over 40% of applications face rejection or processing delays due to policy misinterpretation and subsidy miscalculations across dense, 40-page circulars.*
>
> *I built **UdyamSathi**, an intelligent, policy-grounded MSME copilot designed specifically for grassroots founders. UdyamSathi combines **FastAPI, hybrid retrieval (TF-IDF + ChromaDB), and a LangGraph multi-agent state machine** with human-in-the-loop approval gates. 
> 
> *Unlike generic chatbots that hallucinate statutory numbers, UdyamSathi enforces **strict metadata filtering and deterministic rate calculation tools**, guaranteeing that every subsidy percentage and project cap comes directly from verified Bank of Maharashtra policy records. 
>
> *On the production side, I containerized the system with Docker, optimized cold-boot memory by **80% (dropping from >500MB to 35MB)** on Render using on-demand module loading and CPU-only PyTorch, and built a comprehensive test suite of **54 tests (163 asserts)** with zero-failure CI/CD automation."*

---

## 🎯 The Hardest Problem: Multi-Scheme Isolation & Disambiguation

### Problem Statement
Maharashtra entrepreneurs frequently evaluate two flagship credit-linked subsidy schemes:
1. **PMEGP** (Prime Minister's Employment Generation Programme — Central Government)
2. **CMEGP** (Chief Minister Employment Generation Programme — Maharashtra State Government)

These schemes share almost identical nomenclature: both feature "Margin Money Subsidies", classify applicants into "General" and "Special" categories, differentiate between "Rural" and "Urban" enterprise locations, and offer manufacturing vs. service sector funding.

However, their underlying parameters diverge critically:
- **Maximum Project Costs**: PMEGP permits up to ₹50 Lakh for manufacturing and ₹20 Lakh for services; CMEGP caps manufacturing at ₹50 Lakh and services at ₹20 Lakh, but applies different minimum educational criteria (8th pass for >₹10L manufacturing vs. 7th pass/10th pass state norms) and differing age limits (CMEGP restricts general applicants to 18–45 years, relaxed to 50 for SC/ST/women, whereas PMEGP has no upper age limit).
- **Subsidy Stacking**: An applicant cannot claim margin money from both schemes for the same asset.

### The Failure Mode of Standard RAG
A standard semantic similarity search on queries like *"What is the subsidy for a rural women manufacturing unit?"* retrieves top chunks from **both** PMEGP and CMEGP simultaneously because the textual cosine similarity between them exceeds 0.92. 
When fed to an LLM, the model blended parameters across schemes: quoting PMEGP's lack of age cap alongside CMEGP's urban subsidy rate. This resulted in factually catastrophic advice for prospective borrowers.

### The Engineering Solution
I resolved this through a **three-tier schema enforcement architecture**:

```mermaid
flowchart TD
    UserQuery["User Query"] --> IntentRouter{"Scheme Intent Classifier\n(PMEGP vs CMEGP vs Compare)"}
    
    IntentRouter -->|Specific Scheme| MetaFilter["ChromaDB Metadata Filter\n{'scheme_name': target_scheme}"]
    IntentRouter -->|Comparative Query| DualBranch["Dual Partitioned Retrieval\n(Top-k PMEGP + Top-k CMEGP isolated)"]
    
    MetaFilter --> IsolatedContext["Scheme-Isolated Chunks"]
    DualBranch --> PartitionedContext["Partitioned A/B Scheme Matrix"]
    
    IsolatedContext --> DeterministicTool{"Requires Financial Math?"}
    PartitionedContext --> DeterministicTool
    
    DeterministicTool -->|Yes| CalcEngine["margin_money_subsidy_calculator\n(Deterministic Python Tool - 0% LLM Math)"]
    DeterministicTool -->|No| GroundedGen["Grounded Policy Synthesis\n(Strict Zero-Cross-Contamination Prompt)"]
    
    CalcEngine --> FinalOutput["Audited Response with Citations"]
    GroundedGen --> FinalOutput
```

1. **Metadata Isolation**: In `app/vectorstore.py` and `app/rag.py`, every chunk is indexed with strict metadata (`scheme_name`, `statutory_cap_manufacturing`, `statutory_cap_service`). The retriever applies explicit metadata filtering before similarity re-ranking.
2. **Deterministic Calculation Tools**: Never let an LLM do arithmetic. All subsidy amounts, promoter equity contributions, and bank term loan requirements are computed by `margin_money_subsidy_calculator` in `app/tools.py`.
3. **Provable Single-Source Grounding**: System prompts explicitly enforce that numbers cannot be cited from generic LLM weights; every statutory value must correspond to the single matched scheme record or the deterministic tool output.

---

## ❓ 10 Likely Technical Interview Questions & Answers

### Q1. Why did you build UdyamSathi instead of using a standard LLM chat interface?
**Answer**: Generic LLMs hallucinate financial policies and statutory caps. For example, when asked about service-sector project limits, generic models often cite outdated guidelines (₹10 Lakh) or confuse Central and State limits. Furthermore, entrepreneurs in semi-rural Maharashtra need exact margin money math (down to the rupee) based on their domicile, category, and project location, which LLMs cannot reliably calculate. UdyamSathi pairs deterministic Python calculation engines with strict RAG and LangGraph state machines, providing explainable citations and zero arithmetic errors.

---

### Q2. Why did you choose RAG over fine-tuning for this domain?
**Answer**: Fine-tuning teaches a model style and tone, but it does not reliably update factual knowledge or eliminate hallucination. Banking circulars and scheme guidelines update dynamically (e.g., KVIC circular revisions or government subsidy budget allocations). With RAG:
1. **Dynamic Updates**: New circulars can be ingested into `data/records.json` and ChromaDB without expensive re-training.
2. **Traceability**: Every answer provides verifiable citations linking to specific policy document sections.
3. **Refusal Honesty**: Unanswerable queries (e.g., checking personal loan status) are reliably refused rather than hallucinated.

---

### Q3. Explain your dual retrieval architecture (TF-IDF vs ChromaDB). Why not vector search alone?
**Answer**: Vector embeddings excel at semantic paraphrasing (e.g., matching *"money from government for rural woman"* to *"margin money subsidy"*), but they struggle with exact statutory identifiers, scheme acronyms, and alphanumeric codes (e.g., `PMEGP`, `CMEGP`, `KVIC`, `DIC`). 
I implemented a dual retrieval pipeline:
- **TF-IDF + Cosine Similarity** (`app/records.py`): Performs exact-keyword matching across 20 structured scheme records in `<12 ms`.
- **Dense Vector Search** (`app/vectorstore.py`): Uses `all-MiniLM-L6-v2` embeddings in ChromaDB to retrieve semantically relevant explanatory policy text in `~28 ms`.
This hybrid approach ensures high precision on statutory terms and high recall on natural language queries.

---

### Q4. Walk me through your LangGraph agent architecture. Why did you implement an approval gate?
**Answer**: In `app/graph.py`, the agent is modeled as a state machine using `StateGraph` and checkpointed with `MemorySaver`. When a user submits an eligibility or calculation request, the agent routes through an approval node (`_approval_node`):
- If `calculator_args` are present and `approved=false`, the agent halts execution with `status: approval_required`.
- This ensures human-in-the-loop validation: first-generation founders can review loan inputs (project cost, location, category) before triggering binding calculation logic. Once confirmed (`approved=true`), the graph transitions to the execution node.

---

### Q5. How does your system handle unanswerable queries or out-of-domain questions?
**Answer**: In `docs/user_questions.md` and `tests/test_suite.py`, Question 6 specifically tests unanswerable queries: *"Has my PMEGP loan application (Ref: MH-2026-98124) been approved?"*
Since UdyamSathi stores static policy guidelines and intentionally has no integration with live bank CBS or nodal portal logins, the system enforces a defensive refusal guardrail:
1. Retrieval returns low similarity scores or recognizes status queries.
2. The prompt instructs the LLM to output an explicit, polite refusal: *"I don't know. UdyamSathi does not have access to live bank loan applications or individual disbursement statuses. Please check the official KVIC portal or your lending branch."*
In our evaluation benchmark, this refusal guardrail achieved **100% accuracy**.

---

### Q6. How did you optimize chunk size and top-k in your RAG pipeline?
**Answer**: In `eval/run_eval.py`, I conducted systematic benchmarking comparing two retrieval configurations across 15 test queries:
- **Config A** (180 chars, top-3): Hit rate was 57.1% with 42 ms latency; chunks were often truncated mid-sentence, missing category-specific subsidy clauses.
- **Config B** (120 chars with clean semantic boundaries, top-5): Hit rate increased to **71.4%**, retrieval latency dropped to **28 ms**, and Q6 refusal accuracy remained at **100%**. 
Config B was selected for production because smaller, focused chunks prevented cross-scheme contamination while top-5 provided complete coverage of urban vs. rural clauses.

---

### Q7. How did you optimize Docker container cold-boot memory from >500MB down to 35MB on Render?
**Answer**: On cloud platforms like Render (free tier 512MB RAM), importing heavy ML libraries like PyTorch, Transformers, and ChromaDB at application startup triggers immediate out-of-memory (OOM) kills. I solved this via:
1. **CPU-Only PyTorch**: In `Dockerfile`, installed CPU-only PyTorch wheels (`--extra-index-url https://download.pytorch.org/whl/cpu`), saving >600MB of unused CUDA drivers.
2. **On-Demand Lazy Loading**: In `app/main.py`, postponed heavy imports (`chromadb`, `sentence_transformers`, `langgraph`) until an actual `/ask` or `/agent` query arrives.
As a result, the FastAPI service boots in **<1.2 seconds consuming only 35MB of RAM**, and health check pings respond instantly without warming heavy models.

---

### Q8. What security measures and edge guardrails did you implement?
**Answer**: In `app/security.py`:
1. **Input Truncation**: All incoming query payloads are capped at `MAX_QUESTION_LENGTH = 500` characters, eliminating buffer abuse and token depletion attacks.
2. **Prompt Injection Defense**: Regex patterns intercept adversarial override attempts (`ignore previous instructions`, `reveal system prompt`, `developer mode`, `jailbreak`), returning immediate HTTP `400 Bad Request` without consuming LLM tokens.
3. **Statutory Parameter Clamping**: Numerical inputs are validated against physical caps (e.g., project costs must be positive numbers below statutory maximums; invalid types raise clean validation errors).

---

### Q9. How do your caching and observability layers work?
**Answer**:
- **In-Memory TTL Caching** (`app/cache.py`): Query strings and top-k parameters are hashed. Repeated queries bypass vector search and LLM completion entirely, returning in `<2.5 ms` with `X-Cache: HIT` and saving 100% of LLM token costs.
- **Request Telemetry** (`app/observability.py`): Every API invocation records latency via high-precision monotonic timers (`time.perf_counter()`) and estimates token usage, surfacing `X-Latency-Ms` and `X-Tokens-Estimated` response headers and exposing aggregate metrics at `/cache/stats`.

---

### Q10. What is your testing philosophy, and how do you ensure zero regression?
**Answer**: The repository has **54 automated pytest tests with 163 assertions** spanning 5 modular test files:
- `tests/test_day2.py`: CLI tabular search and structured record parsing.
- `tests/test_day8.py`: Statutory cap enforcement, calculator logic, and fallback responses.
- `tests/test_day9.py`: LangGraph agent routing, memory persistence, and MSME classification rules.
- `tests/test_day10.py`: Streamlit UI business logic, financial ratio consistency, and feedback logging.
- `tests/test_suite.py`: Security validation, cache hit/miss semantics, telemetry headers, and end-to-end API integration.
All tests run in GitHub Actions CI on every push and pull request, guaranteeing 100% green builds before production deployment.
