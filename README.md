# UdyamSathi

## Project Card

| Area | Details |
|---|---|
| **Product** | UdyamSathi is an AI-powered government scheme discovery and subsidy assistance platform. |
| **User** | People in Maharashtra who want to start or expand a small business and need help understanding government support. |
| **Problem** | Information about PMEGP and CMEGP eligibility, subsidy rates, project limits, contributions, documents and applications can be difficult to find and understand. |
| **Solution** | UdyamSathi explains suitable schemes in simple language, checks basic eligibility, estimates subsidy and finance, compares schemes, and guides users through the application process. |
| **Data source** | Official scheme information, including the [PMEGP](https://bankofmaharashtra.bank.in/pmegp) and [CMEGP](https://bankofmaharashtra.bank.in/cmegp) pages from Bank of Maharashtra. |

## Product goal

UdyamSathi helps users make informed decisions about government schemes. It does not guarantee subsidy approval, loan sanction or final eligibility. Important scheme information should always be verified against the latest official source.

## Initial scope

- Discover PMEGP and CMEGP based on a user's business idea and details.
- Explain eligibility conditions and missing information.
- Estimate subsidy, own contribution and bank finance.
- Compare schemes and prepare document checklists.
- Provide clear application guidance and official links.

## Day 2 records CLI

The sample dataset contains 20 records: 10 schemes, 3 MSME classification
limits for 2025, and 7 PMEGP sub-rules. Use Python's standard library to
explore them:

```powershell
python -m app.cli
python -m app.cli --search subsidy
python -m app.cli --count
python -m app.cli --get scheme-pmegp
```

Create the local virtual environment with `python -m venv .venv` if needed.
The environment is intentionally ignored by Git.

## Day 3 data pipeline

Install the downloader dependency and fetch the official scheme documents:

```powershell
python -m pip install -r requirements.txt
python -m app.fetch
python -m app.ingest
```

Documents are saved under `data/raw/`. The ingest step skips malformed files,
reports the error, and writes cleaned records to `data/records.json`.

## How to run

Install the API and analysis dependencies, then start the FastAPI service:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The service provides `GET /health`, `GET /records?limit=`, `GET
/records/{id}`, `GET /search?q=`, and `POST /questions`. Interactive API
documentation is available at `http://127.0.0.1:8000/docs`.

Run the pandas exploration script separately:

```powershell
python -m analysis.explore
```

Build the persistent semantic index and query it:

```powershell
python -c "from app.vectorstore import index_documents; print(index_documents())"
```

Use `GET /search/semantic?q=...` for embedding-based search. Chroma data is
stored locally under `data/chroma/` and is intentionally ignored by Git.

Checkpoint materials:

- [How LLMs work](docs/how_llms_work.md)
- [UdyamSathi user questions](docs/user_questions.md)

## LLM chat

Copy `.env.example` to `.env`, set `LLM_PROVIDER` and the matching provider
API key, then start the service. The `POST /chat` endpoint returns `answer`,
`confidence`, and `follow_up`. Never commit `.env` or an API key.
