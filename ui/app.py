"""Streamlit interface for UdyamSathi scheme discovery and finance estimates."""

from __future__ import annotations

import importlib.util
import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
TOOLS_SPEC = importlib.util.spec_from_file_location(
    "udyamsaathi_tools", ROOT / "app" / "tools.py"
)
if TOOLS_SPEC is None or TOOLS_SPEC.loader is None:
    raise RuntimeError("Unable to load the UdyamSathi calculator module")
TOOLS_MODULE = importlib.util.module_from_spec(TOOLS_SPEC)
TOOLS_SPEC.loader.exec_module(TOOLS_MODULE)
margin_money_subsidy_calculator = TOOLS_MODULE.margin_money_subsidy_calculator

API_URL = os.getenv("UDYAMSAATHI_API_URL", "http://127.0.0.1:8000").rstrip("/")
FEEDBACK_PATH = Path("data/ui_feedback.jsonl")

st.set_page_config(
    page_title="UdyamSathi",
    page_icon="🌱",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background: #f5f7fb; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .hero {
        background: linear-gradient(135deg, #155eef 0%, #12b76a 100%);
        color: white; border-radius: 18px; padding: 1.35rem 1.5rem;
        margin-bottom: 1rem;
    }
    .hero h1 { color: white; margin: 0; font-size: 2rem; }
    .hero p { color: #eef4ff; margin: 0.25rem 0 0 0; }
    .status-ok {
        background: #ecfdf3; color: #067647; border: 1px solid #abefc6;
        border-radius: 10px; padding: 0.8rem; text-align: center;
        font-weight: 700;
    }
    .status-no {
        background: #fff1f3; color: #b42318; border: 1px solid #fda29b;
        border-radius: 10px; padding: 0.8rem; text-align: center;
        font-weight: 700;
    }
    .caption-text { color: #475467; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def save_feedback(question: str, answer: str, rating: str) -> None:
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "question": question,
        "answer": answer,
        "rating": rating,
    }
    with FEEDBACK_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def post_json(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def scheme_fit(
    age: int,
    category: str,
    area: str,
    activity: str,
    project_cost: float,
) -> dict[str, dict[str, Any]]:
    is_special = category.casefold() in {
        "special category",
        "sc",
        "st",
        "obc",
        "minorities",
        "women",
        "ex-servicemen",
        "transgender",
        "differently abled",
    }
    normalized_category = "special" if is_special else "general"
    normalized_activity = "manufacturing" if activity == "Manufacturing" else "service"
    normalized_area = area.casefold()
    caps = {"manufacturing": 5_000_000.0, "service": 2_000_000.0}

    results: dict[str, dict[str, Any]] = {}
    pmegp_reasons: list[str] = []
    cmegp_reasons: list[str] = []
    if age < 18:
        pmegp_reasons.append("Applicant must be at least 18 years old.")
        cmegp_reasons.append("Applicant must be at least 18 years old.")
    if project_cost > caps[normalized_activity]:
        pmegp_reasons.append(
            f"Project cost exceeds the Rs {caps[normalized_activity]:,.0f} "
            f"{normalized_activity} cap."
        )
        cmegp_reasons.append(
            f"Project cost exceeds the Rs {caps[normalized_activity]:,.0f} "
            f"{normalized_activity} cap."
        )
    cmegp_upper_age = 50 if is_special else 45
    if age > cmegp_upper_age:
        cmegp_reasons.append(
            f"CMEGP age limit is exceeded for this category "
            f"(maximum {cmegp_upper_age})."
        )

    pmegp_qualifies = not pmegp_reasons
    cmegp_qualifies = not cmegp_reasons
    pmegp_calculation = margin_calc(
        project_cost,
        normalized_activity,
        normalized_category,
        normalized_area,
        "PMEGP",
    )
    cmegp_calculation = margin_calc(
        project_cost,
        normalized_activity,
        normalized_category,
        normalized_area,
        "CMEGP",
    )
    results["PMEGP"] = {
        "qualifies": pmegp_qualifies,
        "reasons": pmegp_reasons
        or ["Applicant age and project-cost cap are within the available rules."],
        "calculation": pmegp_calculation if pmegp_qualifies else None,
    }
    results["CMEGP"] = {
        "qualifies": cmegp_qualifies,
        "reasons": cmegp_reasons
        or ["Applicant age and project-cost cap are within the available rules."],
        "calculation": cmegp_calculation if cmegp_qualifies else None,
    }
    return results


def margin_calc(
    project_cost: float,
    activity: str,
    category: str,
    area: str,
    scheme: str,
) -> dict[str, Any] | None:
    if project_cost <= 0:
        return None
    try:
        return margin_money_subsidy_calculator(
            project_cost,
            activity,
            category,
            area,
            scheme,
        )
    except ValueError:
        return None


def render_status(name: str, fit: dict[str, Any]) -> None:
    st.subheader(name)
    if fit["qualifies"]:
        st.markdown('<div class="status-ok">You qualify</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="status-no">Not qualified</div>', unsafe_allow_html=True
        )
    for reason in fit["reasons"]:
        st.markdown(f"- {reason}")
    calculation = fit["calculation"]
    if calculation:
        st.markdown("#### Estimated finance")
        metric_columns = st.columns(3)
        metric_columns[0].metric("Subsidy", f"Rs {calculation['subsidy_amount']:,.0f}")
        metric_columns[1].metric(
            "Your contribution", f"Rs {calculation['own_contribution']:,.0f}"
        )
        metric_columns[2].metric(
            "Bank loan", f"Rs {calculation['bank_loan_amount']:,.0f}"
        )


st.markdown(
    """
    <div class="hero">
      <h1>UdyamSathi</h1>
      <p>Government scheme guidance, subsidy estimates, and PMEGP/CMEGP comparison.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    health = requests.get(f"{API_URL}/health", timeout=5)
    backend_ok = health.ok
except requests.RequestException:
    backend_ok = False

if backend_ok:
    st.success("Live API connected")
else:
    st.error(
        "FastAPI is not reachable. Start it with "
        "`python -m uvicorn app.main:app --reload`."
    )

tab_chat, tab_fit = st.tabs(["💬 Ask UdyamSathi", "⚖️ Scheme-fit table"])

with tab_chat:
    st.caption("Ask about eligibility, subsidy, project limits, or scheme rules.")
    api_mode = st.radio(
        "Answer route",
        ["RAG /ask", "Agent /agent"],
        horizontal=True,
        key="answer_route",
        help="Use /ask for grounded citation search or /agent for the LangGraph route.",
    )
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("citations"):
                with st.expander("Sources"):
                    for index, citation in enumerate(message["citations"], start=1):
                        st.markdown(
                            f"**[{index}] {citation.get('title', 'Source')}** — "
                            f"{citation.get('source', 'unknown')} p.{citation.get('page', 1)}"
                        )

    question = st.chat_input("Ask a UdyamSathi question")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with (
            st.chat_message("assistant"),
            st.spinner("Searching UdyamSathi sources..."),
        ):
            try:
                if api_mode == "RAG /ask":
                    payload = post_json("/ask", {"question": question, "top_k": 5})
                    answer = str(payload.get("answer", "I don't know"))
                    citations = payload.get("citations", [])
                else:
                    payload = post_json(
                        "/agent",
                        {
                            "question": question,
                            "approved": False,
                            "thread_id": "streamlit-session",
                        },
                    )
                    agent_answer = payload.get("answer", {})
                    answer = str(agent_answer.get("answer", "I don't know"))
                    citations = agent_answer.get("citations", [])
                st.markdown(answer)
                if citations:
                    with st.expander("Sources"):
                        for index, citation in enumerate(citations, start=1):
                            st.markdown(
                                f"**[{index}] {citation.get('title', 'Source')}** — "
                                f"{citation.get('source', 'unknown')} p.{citation.get('page', 1)}"
                            )
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "citations": citations,
                        "question": question,
                    }
                )
                feedback_left, feedback_right, _ = st.columns([1, 1, 8])
                if feedback_left.button(
                    "👍 Helpful", key=f"up-{len(st.session_state.messages)}"
                ):
                    save_feedback(question, answer, "thumbs_up")
                    st.toast("Thank you for your feedback!")
                if feedback_right.button(
                    "👎 Not helpful", key=f"down-{len(st.session_state.messages)}"
                ):
                    save_feedback(question, answer, "thumbs_down")
                    st.toast("Feedback saved.")
            except requests.RequestException as error:
                st.error(f"UdyamSathi API request failed: {error}")

with tab_fit:
    st.subheader("Compare PMEGP and CMEGP")
    st.caption(
        "A pre-screening estimate based on the stored scheme rules. Final eligibility depends on the lender."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", min_value=15, max_value=100, value=30)
        category = st.selectbox(
            "Category",
            [
                "General",
                "Special category",
                "Women",
                "SC",
                "ST",
                "OBC",
                "Minorities",
                "Ex-servicemen",
                "Differently abled",
            ],
        )
    with col2:
        area = st.selectbox("Area", ["Rural", "Urban"])
        activity = st.selectbox("Activity", ["Manufacturing", "Service"])
    with col3:
        project_cost_lakh = st.number_input(
            "Project cost (Rs lakh)",
            min_value=0.1,
            max_value=100.0,
            value=10.0,
            step=0.5,
        )
        calculate = st.button(
            "Compare schemes", type="primary", use_container_width=True
        )

    if calculate:
        fit = scheme_fit(
            int(age),
            category,
            area,
            activity,
            float(project_cost_lakh) * 100_000,
        )
        left, right = st.columns(2)
        with left:
            render_status("PMEGP", fit["PMEGP"])
        with right:
            render_status("CMEGP", fit["CMEGP"])
