"""Streamlit interface for UdyamSathi scheme discovery and finance estimates."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TOOLS_SPEC = importlib.util.spec_from_file_location(
    "udyamsaathi_tools", ROOT / "app" / "tools.py"
)
if TOOLS_SPEC is None or TOOLS_SPEC.loader is None:
    raise RuntimeError("Unable to load the UdyamSathi calculator module")
TOOLS_MODULE = importlib.util.module_from_spec(TOOLS_SPEC)
TOOLS_SPEC.loader.exec_module(TOOLS_MODULE)
margin_money_subsidy_calculator = TOOLS_MODULE.margin_money_subsidy_calculator

FEEDBACK_PATH = Path("data/ui_feedback.jsonl")

DEFAULT_API_URL = os.getenv(
    "UDYAMSAATHI_API_URL", "https://udyamsaathi-14cw.onrender.com"
).rstrip("/")

st.set_page_config(
    page_title="UdyamSathi — MSME Scheme Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Background Canvas */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 0%, #172554 0%, #0b1120 75%) !important;
        color: #f8fafc !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #080d1a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Hero Banner */
    .hero {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.95) 0%, rgba(30, 58, 138, 0.9) 45%, rgba(6, 95, 70, 0.85) 100%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2.25rem 2.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.2);
    }
    .hero h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: 2.35rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    .hero p {
        color: #93c5fd !important;
        margin: 0.6rem 0 0 0;
        font-size: 1.05rem;
        font-weight: 400;
        line-height: 1.5;
    }
    .hero-badges {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #f8fafc;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        backdrop-filter: blur(8px);
    }
    
    /* High-contrast Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }
    p, span, label {
        color: #e2e8f0;
    }
    .stCaption, caption {
        color: #94a3b8 !important;
    }
    
    /* Cards */
    .card {
        background: #111a33;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.35);
        color: #f8fafc;
    }
    
    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(17, 26, 51, 0.7);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1.25rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 10px;
        padding: 0 18px;
        font-weight: 600;
        font-size: 0.95rem;
        color: #94a3b8 !important;
        background-color: transparent;
        border: none;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #f8fafc !important;
        background-color: rgba(255, 255, 255, 0.05);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4);
    }
    
    /* Status Badges */
    .status-ok {
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.5) 0%, rgba(16, 185, 129, 0.25) 100%);
        color: #34d399 !important;
        border: 1.5px solid #059669;
        border-radius: 12px;
        padding: 0.85rem;
        text-align: center;
        font-weight: 700;
        font-size: 1.15rem;
        letter-spacing: 0.02em;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(5, 150, 105, 0.25);
    }
    .status-no {
        background: linear-gradient(135deg, rgba(159, 18, 57, 0.5) 0%, rgba(244, 63, 94, 0.25) 100%);
        color: #fb7185 !important;
        border: 1.5px solid #e11d48;
        border-radius: 12px;
        padding: 0.85rem;
        text-align: center;
        font-weight: 700;
        font-size: 1.15rem;
        letter-spacing: 0.02em;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(225, 29, 72, 0.25);
    }
    
    /* Telemetry Pills */
    .telemetry-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3);
        font-size: 0.78rem;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 9999px;
        margin-top: 8px;
    }
    
    /* Chat Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #111a33 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 1rem 1.25rem !important;
        margin-bottom: 0.85rem !important;
        color: #f8fafc !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        font-weight: 800 !important;
        color: #38bdf8 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
    }
    
    /* Button enhancements */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.3) !important;
    }
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


def post_json(api_base: str, path: str, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    response = requests.post(f"{api_base}{path}", json=payload, timeout=60)
    response.raise_for_status()
    headers = dict(response.headers)
    return response.json(), headers


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
        pmegp_reasons.append("Applicant must be at least 18 years of age.")
        cmegp_reasons.append("Applicant must be at least 18 years of age.")

    if project_cost > caps[normalized_activity]:
        cap_fmt = f"Rs {caps[normalized_activity]:,.0f}"
        pmegp_reasons.append(f"Project cost exceeds the {cap_fmt} statutory cap for {normalized_activity}.")
        cmegp_reasons.append(f"Project cost exceeds the {cap_fmt} statutory cap for {normalized_activity}.")

    cmegp_upper_age = 50 if is_special else 45
    if age > cmegp_upper_age:
        cmegp_reasons.append(
            f"Age exceeds CMEGP maximum threshold for {category} ({cmegp_upper_age} years)."
        )

    pmegp_qualifies = not pmegp_reasons
    cmegp_qualifies = not cmegp_reasons

    pmegp_calc = margin_calc(
        project_cost,
        normalized_activity,
        normalized_category,
        normalized_area,
        "PMEGP",
    )
    cmegp_calc = margin_calc(
        project_cost,
        normalized_activity,
        normalized_category,
        normalized_area,
        "CMEGP",
    )

    results["PMEGP"] = {
        "qualifies": pmegp_qualifies,
        "reasons": pmegp_reasons or ["Applicant age, sector, and project cost comply with all PMEGP guidelines."],
        "calculation": pmegp_calc if pmegp_qualifies else None,
    }
    results["CMEGP"] = {
        "qualifies": cmegp_qualifies,
        "reasons": cmegp_reasons or ["Applicant age, sector, and project cost comply with all CMEGP guidelines."],
        "calculation": cmegp_calc if cmegp_qualifies else None,
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


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/handshake-heart.png", width=64)
    st.title("UdyamSathi")
    st.caption("AI-Powered Scheme Discovery for Maharashtra")

    st.markdown("---")
    st.subheader("🌐 API Connection")

    api_choice = st.radio(
        "Backend Server",
        ["Production (Render)", "Localhost (Port 8000)", "Custom URL"],
        index=0,
    )

    if api_choice == "Production (Render)":
        active_api = "https://udyamsaathi-14cw.onrender.com"
    elif api_choice == "Localhost (Port 8000)":
        active_api = "http://127.0.0.1:8000"
    else:
        active_api = st.text_input("Enter API Base URL", value=DEFAULT_API_URL).rstrip("/")

    # Check backend connectivity with latency ping
    t0 = time.perf_counter()
    backend_ok = False
    ping_ms = 0.0
    try:
        res = requests.get(f"{active_api}/health", timeout=5)
        ping_ms = (time.perf_counter() - t0) * 1000
        backend_ok = res.status_code == 200 and res.json().get("status") == "ok"
    except (requests.RequestException, ValueError):
        backend_ok = False

    if backend_ok:
        st.success(f"Connected ({ping_ms:.0f} ms)")
    else:
        st.error("API Offline / Unreachable")

    st.markdown("---")
    st.subheader("💡 Example Questions")
    example_prompts = [
        "What is the PMEGP subsidy rate for rural women?",
        "What is the maximum cost for a manufacturing unit under CMEGP?",
        "Can a family apply for two different PMEGP businesses?",
        "What are the 2025 MSME micro enterprise limits?",
        "Has my loan application been approved?",
    ]
    for prompt in example_prompts:
        if st.button(prompt, use_container_width=True):
            st.session_state["queued_prompt"] = prompt

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Built for Maharashtra MSME Development • 2026")


# ==========================================
# MAIN PAGE HEADER
# ==========================================
st.markdown(
    """
    <div class="hero">
      <h1>🌱 UdyamSathi (उद्यमसाथी)</h1>
      <p>Instant government scheme discovery, side-by-side PMEGP vs CMEGP qualification, and policy-grounded financial subsidy estimation.</p>
      <div class="hero-badges">
        <span class="hero-pill">⚡ 20 Official Policy Records</span>
        <span class="hero-pill">🛡️ Zero AI Math (Audited Tool)</span>
        <span class="hero-pill">⏱️ &lt; 2.5ms Cache Latency</span>
        <span class="hero-pill">🎯 54 Pytest Test Suites</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_fit, tab_chat, tab_directory = st.tabs([
    "⚖️ Scheme-Fit Comparator",
    "💬 AI Policy Advisor",
    "📚 Official Scheme Directory",
])


# ==========================================
# TAB 1: SCHEME-FIT COMPARATOR (SIGNATURE)
# ==========================================
with tab_fit:
    st.markdown("### ⚖️ Side-by-Side Scheme Qualification & Capital Breakdown")
    st.caption(
        "Evaluate your project simultaneously against the Prime Minister Employment Generation Programme (PMEGP) "
        "and Chief Minister Employment Generation Programme (CMEGP)."
    )

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1.2])

        with col1:
            age = st.number_input("Applicant Age", min_value=15, max_value=85, value=28, help="PMEGP min 18; CMEGP 18-45 (relaxed to 50 for special categories)")
            category = st.selectbox(
                "Social Category",
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
                help="Special category applicants receive 10% higher margin money subsidy and lower own contribution requirements.",
            )

        with col2:
            area = st.selectbox("Project Location", ["Rural", "Urban"], help="Rural units qualify for up to 35% subsidy compared to 25% for urban.")
            activity = st.selectbox("Sector / Activity", ["Manufacturing", "Service"], help="Statutory caps: Rs 50 Lakh for Manufacturing; Rs 20 Lakh for Service.")

        with col3:
            project_cost_lakh = st.slider(
                "Project Cost (Rs. in Lakhs)",
                min_value=1.0,
                max_value=60.0,
                value=15.0,
                step=0.5,
                help="Adjust to verify cap compliance and estimated subsidy amounts.",
            )
            cost_in_rupees = float(project_cost_lakh) * 100_000

        st.markdown("</div>", unsafe_allow_html=True)

    # Calculate real-time fit
    fit_data = scheme_fit(
        int(age),
        category,
        area,
        activity,
        cost_in_rupees,
    )

    res_col1, res_col2 = st.columns(2)

    for col, (scheme_name, scheme_info) in zip([res_col1, res_col2], fit_data.items(), strict=False):
        with col:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### {scheme_name}")

            if scheme_info["qualifies"]:
                st.markdown('<div class="status-ok">✅ You Qualify</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-no">❌ Currently Ineligible</div>', unsafe_allow_html=True)

            st.markdown("**Eligibility Criteria Checklist:**")
            for reason in scheme_info["reasons"]:
                icon = "✅" if scheme_info["qualifies"] else "⚠️"
                st.markdown(f"{icon} {reason}")

            calc = scheme_info.get("calculation")
            if calc:
                st.markdown("---")
                st.markdown("#### 💰 Financial Structure")

                m1, m2, m3 = st.columns(3)
                m1.metric("Subsidy Grant", f"₹{calc['subsidy_amount']:,.0f}", help="Government margin money grant")
                m2.metric("Your Contribution", f"₹{calc['own_contribution']:,.0f}", help="Required applicant equity")
                m3.metric("Bank Term Loan", f"₹{calc['bank_loan_amount']:,.0f}", help="Bank finance portion")

                # Visual distribution progress bar
                sub_ratio = calc["subsidy_amount"] / calc["project_cost"]
                own_ratio = calc["own_contribution"] / calc["project_cost"]
                st.caption(f"Financial Ratio: **{sub_ratio * 100:.0f}% Subsidy** | **{own_ratio * 100:.0f}% Own** | **{(1 - sub_ratio - own_ratio) * 100:.0f}% Bank Finance**")
                st.progress(sub_ratio)

            st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 2: AI POLICY ADVISOR (CHAT)
# ==========================================
with tab_chat:
    st.markdown("### 💬 Ask UdyamSathi")
    st.caption("Ask questions about government circulars, eligibility, educational requirements, or subsidy procedures.")

    route_col, _ = st.columns([2, 3])
    with route_col:
        api_mode = st.radio(
            "Orchestration Mode",
            ["Grounded RAG (/ask)", "LangGraph Agent (/agent)"],
            horizontal=True,
            help="RAG searches official Bank of Maharashtra document chunks with strict citations. LangGraph agent routes calculations and manages approval states.",
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if message.get("telemetry"):
                    st.markdown(
                        f"<div class='telemetry-pill'>⚡ Latency: {message['telemetry'].get('latency', 'N/A')} ms | "
                        f"Tokens: {message['telemetry'].get('tokens', 'N/A')} | "
                        f"Cache: {message['telemetry'].get('cache', 'N/A')}</div>",
                        unsafe_allow_html=True,
                    )
                if message.get("citations"):
                    with st.expander("📄 Source Citations"):
                        for idx, cit in enumerate(message["citations"], start=1):
                            st.markdown(
                                f"**[{idx}] {cit.get('title', 'Official Source')}**\n\n"
                                f"Document: `{cit.get('source', 'unknown')}` | Page: `{cit.get('page', 1)}`"
                            )

    # Handle queued prompt from sidebar or new chat input
    user_input = st.chat_input("Ask a question about MSME schemes in Maharashtra...")
    if st.session_state.get("queued_prompt"):
        user_input = st.session_state.pop("queued_prompt")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"), st.spinner("Analyzing official policy sources..."):
            try:
                t_start = time.perf_counter()
                if api_mode == "Grounded RAG (/ask)":
                    payload, headers = post_json(active_api, "/ask", {"question": user_input, "top_k": 5})
                    answer = str(payload.get("answer", "I don't know"))
                    citations = payload.get("citations", [])
                else:
                    payload, headers = post_json(
                        active_api,
                        "/agent",
                        {
                            "question": user_input,
                            "approved": False,
                            "thread_id": "streamlit-web-session",
                        },
                    )
                    agent_ans = payload.get("answer", {})
                    answer = str(agent_ans.get("answer", "I don't know"))
                    citations = agent_ans.get("citations", [])

                latency_str = headers.get("x-latency-ms", f"{(time.perf_counter() - t_start) * 1000:.1f}")
                tokens_str = headers.get("x-tokens-estimated", "N/A")
                cache_str = headers.get("x-cache", "MISS")

                st.markdown(answer)

                st.markdown(
                    f"<div class='telemetry-pill'>⚡ Latency: {latency_str} ms | "
                    f"Tokens: {tokens_str} | "
                    f"Cache: {cache_str}</div>",
                    unsafe_allow_html=True,
                )

                if citations:
                    with st.expander("📄 Source Citations"):
                        for idx, cit in enumerate(citations, start=1):
                            st.markdown(
                                f"**[{idx}] {cit.get('title', 'Official Source')}**\n\n"
                                f"Document: `{cit.get('source', 'unknown')}` | Page: `{cit.get('page', 1)}`"
                            )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "citations": citations,
                        "telemetry": {
                            "latency": latency_str,
                            "tokens": tokens_str,
                            "cache": cache_str,
                        },
                    }
                )

                fb_col1, fb_col2, _ = st.columns([1, 1, 8])
                if fb_col1.button("👍 Helpful", key=f"thumb-up-{len(st.session_state.messages)}"):
                    save_feedback(user_input, answer, "thumbs_up")
                    st.toast("Thank you for your feedback!")
                if fb_col2.button("👎 Not helpful", key=f"thumb-down-{len(st.session_state.messages)}"):
                    save_feedback(user_input, answer, "thumbs_down")
                    st.toast("Feedback recorded.")

            except requests.RequestException as err:
                st.error(f"API Request Failed: {err}")


# ==========================================
# TAB 3: SCHEME DIRECTORY
# ==========================================
with tab_directory:
    st.markdown("### 📚 Official MSME Policy & Limits Directory")
    st.caption("Browse structured data extracted directly from Bank of Maharashtra official publications.")

    search_term = st.text_input("🔍 Search schemes by keyword", placeholder="e.g. mudra, manufacturing, women, education")

    try:
        records_resp = requests.get(f"{active_api}/records?limit=50", timeout=10)
        if records_resp.ok:
            all_records = records_resp.json()
            if search_term.strip():
                filtered = [
                    r for r in all_records
                    if search_term.casefold() in str(r).casefold()
                ]
            else:
                filtered = all_records

            st.write(f"Showing **{len(filtered)}** matching official records:")
            for item in filtered:
                with st.expander(f"📌 {item.get('scheme_name', 'Scheme Record')}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Max Project Cost:** `{item.get('max_project_cost', 'N/A')}`")
                        st.markdown(f"**Subsidy (General):** `{item.get('subsidy_general', 'N/A')}`")
                        st.markdown(f"**Subsidy (Special):** `{item.get('subsidy_special', 'N/A')}`")
                    with c2:
                        st.markdown(f"**Applicant Contribution:** `{item.get('own_contribution', 'N/A')}`")
                        st.markdown(f"**Category:** `{item.get('category', 'scheme')}`")
                        st.markdown(f"**Record ID:** `{item.get('id', 'N/A')}`")
                    st.markdown("---")
                    st.markdown(f"**Eligibility Details:**\n\n{item.get('eligibility', 'N/A')}")
        else:
            st.warning("Could not fetch records list from the backend API.")
    except (requests.RequestException, ValueError) as exc:
        st.info(f"Connect to a live backend to explore the full directory: {exc}")
