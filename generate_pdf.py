"""Generate a high-polish, professional Demo Day PDF for UdyamSathi using ReportLab."""

import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print 'Page X of Y'."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Top running header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 750, "UdyamSathi (उद्यमसाथी) — Demo Day & Technical Defense Guide")
            self.drawRightString(558, 750, "Sameer Pradeep Jadhav (2124UCEM2051)")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Bottom running footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 35, "Confidential — Prepared for Sanjivani AI Final Evaluation")
        self.drawRightString(558, 35, page_str)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.restoreState()


def build_pdf(filename="docs/UdyamSathi_Demo_Day_Master_Guide.pdf"):
    dirname = os.path.dirname(filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom palette
    primary = colors.HexColor("#1e3a8a")     # Deep Navy
    secondary = colors.HexColor("#0284c7")   # Bright Blue
    dark_neutral = colors.HexColor("#0f172a") # Slate 900
    light_bg = colors.HexColor("#f8fafc")    # Slate 50
    border_color = colors.HexColor("#cbd5e1")# Slate 300

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=primary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=secondary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_neutral,
        spaceAfter=5
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=dark_neutral
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell,
        fontName="Helvetica-Bold",
        textColor=primary
    )

    story = []

    # Title Block
    story.append(Paragraph("UdyamSathi (उद्यमसाथी)", title_style))
    story.append(Paragraph("Demo Day Presentation & Technical Defense Master Guide — 5-Min Live Demo + 3-Min Q&A", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary, spaceAfter=8))

    # Meta Info Table
    meta_data = [
        [
            Paragraph("<b>Presenter:</b> Sameer Pradeep Jadhav (2124UCEM2051)", table_cell),
            Paragraph("<b>Track & Project ID:</b> CSE · SJ-38 Finance", table_cell),
        ],
        [
            Paragraph("<b>Live Cloud URL:</b> <font color='#0284c7'>https://udyamsaathi-14cw.onrender.com</font>", table_cell),
            Paragraph("<b>GitHub:</b> <font color='#0284c7'>sameeeerjadhav/cream-AI</font>", table_cell),
        ],
        [
            Paragraph("<b>Test Suite:</b> 54 Tests (163 Asserts) · 100% Passing", table_cell),
            Paragraph("<b>Tracker Status:</b> ★ 1 Star Awarded (D11 Exceptional Work)", table_cell_bold),
        ]
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1: 3 Mandatory Items
    story.append(Paragraph("1. The 3 Mandatory Items to Bring to Demo Day", h1_style))
    
    mandate_data = [
        [
            Paragraph("<b>Item</b>", table_cell_bold),
            Paragraph("<b>Exact Live Resource</b>", table_cell_bold),
            Paragraph("<b>Key Evaluator Proof Points</b>", table_cell_bold)
        ],
        [
            Paragraph("<b>1. Live URL</b>", table_cell),
            Paragraph("https://udyamsaathi-14cw.onrender.com<br/>• Health: /health<br/>• Swagger Docs: /docs<br/>• Streamlit UI: Local port 8501", table_cell),
            Paragraph("Demonstrates zero-downtime cloud container deployment; returns HTTP 200 OK continuously without warm-up cold-boot lag.", table_cell)
        ],
        [
            Paragraph("<b>2. GitHub README</b>", table_cell),
            Paragraph("github.com/sameeeerjadhav/cream-AI", table_cell),
            Paragraph("Features selling hook, full Mermaid architecture diagram, Streamlit UI screenshot, D1-D12 milestone table, and Config B benchmark results.", table_cell)
        ],
        [
            Paragraph("<b>3. Failure Fixed & Measured</b>", table_cell_bold),
            Paragraph("<b>Render Container OOM Crash</b><br/>• Free tier 512MB RAM ceiling.<br/>• Startup spiked >520MB (502 Gateway).", table_cell),
            Paragraph("<b>Fixed by:</b> CPU-only PyTorch wheels (saving 600MB CUDA binaries) + lazy on-demand module imports in FastAPI.<br/><b>Measured by:</b> Memory dropped from >512MB to <b>35 MB (80%+ reduction)</b>; boot time dropped from 28s to <b>1.2s</b>.", table_cell)
        ]
    ]
    t_mandate = Table(mandate_data, colWidths=[90, 190, 224])
    t_mandate.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e0f2fe")),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor("#fef3c7")), # highlight failure
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_mandate)
    story.append(Spacer(1, 10))

    # Section 2: 5-Minute Live Demo Script
    story.append(Paragraph("2. Second-by-Second 5-Minute Live Demo Script", h1_style))
    
    script_data = [
        [Paragraph("<b>Timestamp</b>", table_cell_bold), Paragraph("<b>Screen & Action</b>", table_cell_bold), Paragraph("<b>Spoken Script (What to Say)</b>", table_cell_bold)],
        [
            Paragraph("<b>[0:00 - 1:00]</b><br/>Hook & Problem", table_cell),
            Paragraph("Show GitHub README header & problem section.", table_cell),
            Paragraph("<i>'Good morning, evaluators. I am Sameer Jadhav. In Maharashtra, thousands of entrepreneurs apply for PMEGP and CMEGP subsidies, but over 40% fail due to complex 40-page circulars. Founders confuse statutory caps (Rs 50L manufacturing vs Rs 20L service) and subsidy rates (15% to 35%). Generic LLMs hallucinate rules and make loan math errors. UdyamSathi solves this with hybrid RAG, LangGraph agents, and deterministic calculation tools.'</i>", table_cell)
        ],
        [
            Paragraph("<b>[1:00 - 2:00]</b><br/>Architecture", table_cell),
            Paragraph("Scroll to Mermaid architecture diagram in README.", table_cell),
            Paragraph("<i>'Our architecture uses: 1) Streamlit UI on FastAPI. 2) Edge security with 500-char limits and prompt-injection defense. 3) Dual retrieval: TF-IDF for exact acronyms (<12ms) plus ChromaDB vector search. 4) A LangGraph agent with an approval gate and deterministic math tools—meaning we never allow an LLM to do financial calculations.'</i>", table_cell)
        ],
        [
            Paragraph("<b>[2:00 - 3:30]</b><br/>Streamlit Live Demo", table_cell),
            Paragraph("Switch to Streamlit UI.<br/>1. Show Comparator.<br/>2. Run calculation query.<br/>3. Show Q6 refusal.", table_cell),
            Paragraph("<i>'Here is the live interface. First, our scheme comparator highlights key differences. Second, I will ask for a Rs 10L rural spice unit under PMEGP: notice the agent pauses with status: approval_required. Once confirmed, our Python tool calculates Rs 3,50,000 (35%) margin money with exact citations. Third, on loan status queries (Q6), our defensive guardrail honestly refuses: I do not have access to live bank CBS systems.'</i>", table_cell)
        ],
        [
            Paragraph("<b>[3:30 - 4:30]</b><br/>Failure & Metric", table_cell_bold),
            Paragraph("Face evaluators directly.", table_cell),
            Paragraph("<i>'A critical failure I fixed was Render Container Memory Crashes. PyTorch GPU drivers spiked boot memory past 520MB on Render's 512MB free tier, crashing with HTTP 502. I fixed this by switching to CPU-only PyTorch wheels and implementing lazy module loading. I measured memory dropping from >512MB to 35MB (80%+ reduction) and boot latency dropping from 28s to 1.2s.'</i>", table_cell)
        ],
        [
            Paragraph("<b>[4:30 - 5:00]</b><br/>Cloud & Wrap", table_cell),
            Paragraph("Show live Render /docs Swagger UI.", table_cell),
            Paragraph("<i>'Here is our public Render deployment responding with HTTP 200 at /health, validated by 54 automated pytest tests in GitHub Actions CI. Thank you, I am ready for questions.'</i>", table_cell)
        ]
    ]
    t_script = Table(script_data, colWidths=[80, 120, 304])
    t_script.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e0f2fe")),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_script)
    story.append(PageBreak())

    # Section 3: The Hardest Technical Problem
    story.append(Paragraph("3. The Hardest Technical Problem (Interview Story)", h1_style))
    story.append(Paragraph(
        "<b>Multi-Scheme Cross-Contamination (PMEGP vs. CMEGP Disambiguation)</b>", h2_style
    ))
    story.append(Paragraph(
        "<b>The Failure:</b> PMEGP (Central) and CMEGP (State) share identical terms: <i>'Margin Money'</i>, <i>'Manufacturing'</i>, <i>'Service'</i>, and <i>'Special Category'</i>. In standard vector search, textual cosine similarity between them exceeded <b>0.92</b>. Naive RAG retrieved chunks from both schemes simultaneously. The LLM blended parameters across schemes: quoting PMEGP's lack of age cap alongside CMEGP's urban subsidy rate, producing factually catastrophic advice.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Three-Tier Engineering Solution:</b><br/>"
        "1. <b>Strict ChromaDB Metadata Filtering:</b> Chunks are isolated with <code>scheme_name</code> metadata tags; retriever filters out foreign schemes prior to re-ranking.<br/>"
        "2. <b>Deterministic Calculation Engine:</b> Subsidies are computed entirely in audited Python (<code>margin_money_subsidy_calculator</code>); the LLM only parses arguments.<br/>"
        "3. <b>Zero-Cross-Contamination Prompting:</b> The system prompt mandates that every numerical value trace directly to the single matched scheme record or the audited calculator output.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Section 4: 12-Day Milestones
    story.append(Paragraph("4. The 12-Day Engineering Journey (D01 – D12 Overview)", h1_style))
    
    milestone_data = [
        [Paragraph("<b>Day</b>", table_cell_bold), Paragraph("<b>Milestone & Focus</b>", table_cell_bold), Paragraph("<b>Key Code Deliverables</b>", table_cell_bold), Paragraph("<b>Outcome / Metric</b>", table_cell_bold)],
        [Paragraph("<b>D01</b>", table_cell), Paragraph("Python Basics & Terminal CLI", table_cell), Paragraph("day01/day01_menu.py, docs/day01_guide.md", table_cell), Paragraph("200+ line guide explaining Python terms", table_cell)],
        [Paragraph("<b>D02</b>", table_cell), Paragraph("Structured Records & CLI Search", table_cell), Paragraph("data/records.json, app/cli.py, test_day2.py", table_cell), Paragraph("20 structured records, 10 unit test suites", table_cell)],
        [Paragraph("<b>D03</b>", table_cell), Paragraph("Data Ingestion & Sanitization", table_cell), Paragraph("app/ingest.py, data/raw/", table_cell), Paragraph("Bank of Maharashtra PDF cleaning & normalization", table_cell)],
        [Paragraph("<b>D04</b>", table_cell), Paragraph("Hybrid Retrieval & Vector Index", table_cell), Paragraph("app/records.py, app/vectorstore.py", table_cell), Paragraph("TF-IDF (<12ms) + ChromaDB MiniLM embeddings", table_cell)],
        [Paragraph("<b>D05</b>", table_cell), Paragraph("LLM Architecture & User Benchmark", table_cell), Paragraph("docs/how_llms_work.md, docs/user_questions.md", table_cell), Paragraph("10 trilingual Qs (EN/MR/HI), Q6 refusal guard", table_cell)],
        [Paragraph("<b>D06</b>", table_cell), Paragraph("Prompt Engineering & Rubric Eval", table_cell), Paragraph("eval/prompt_compare.md, search_results.md", table_cell), Paragraph("4-dimension, 8-point systematic rubric", table_cell)],
        [Paragraph("<b>D07</b>", table_cell), Paragraph("FastAPI Service & Edge Security", table_cell), Paragraph("app/main.py, app/cache.py, app/security.py", table_cell), Paragraph("Cache <2.5ms; 500-char max & prompt-injection regex", table_cell)],
        [Paragraph("<b>D08</b>", table_cell), Paragraph("RAG Benchmark & Chunk Tuning", table_cell), Paragraph("eval/run_eval.py, eval/eval_results.json", table_cell), Paragraph("Config B winner (120c/top-5, 71.4% hit, 28ms)", table_cell)],
        [Paragraph("<b>D09</b>", table_cell), Paragraph("LangGraph Agent & Human-in-Loop", table_cell), Paragraph("app/graph.py, app/agent_loop.py, tools.py", table_cell), Paragraph("Approval gate (approval_required), 12 tests", table_cell)],
        [Paragraph("<b>D10</b>", table_cell), Paragraph("Streamlit Web Dashboard", table_cell), Paragraph("ui/app.py (558 lines), tests/test_day10.py", table_cell), Paragraph("Scheme comparator, live telemetry, 15 UI tests", table_cell)],
        [Paragraph("<b>D11</b>", table_cell_bold), Paragraph("Pytest Suite & Dockerization", table_cell_bold), Paragraph("Dockerfile, docker-compose.yml, tests/", table_cell), Paragraph("<b>★ Star Awarded:</b> 54 pytest tests (163 asserts)", table_cell_bold)],
        [Paragraph("<b>D12</b>", table_cell), Paragraph("Cloud Deployment & CI Automation", table_cell), Paragraph(".github/workflows/ci.yml, render.yaml", table_cell), Paragraph("Render deployment live, 35MB cold-boot memory", table_cell)]
    ]
    t_mile = Table(milestone_data, colWidths=[32, 140, 182, 150])
    t_mile.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e0f2fe")),
        ('BACKGROUND', (0,11), (-1,11), colors.HexColor("#fef3c7")), # D11 star
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_mile)
    story.append(Spacer(1, 8))

    # Section 5: Top 6 Viva Questions
    story.append(Paragraph("5. Top 6 Technical Viva Questions & 20-Second Answers", h1_style))
    
    qa_data = [
        [
            Paragraph("<b>Q1: Why RAG over fine-tuning?</b>", table_cell_bold),
            Paragraph("<i>'Government circulars change regularly. Fine-tuning is slow, expensive, and doesn't eliminate hallucinations. With RAG, updating policies takes seconds by updating documents, and every answer includes transparent citations.'</i>", table_cell)
        ],
        [
            Paragraph("<b>Q2: Why dual search (TF-IDF + ChromaDB)?</b>", table_cell_bold),
            Paragraph("<i>'TF-IDF is keyword-based and ultrafast (<12ms), catching exact acronyms like PMEGP and KVIC. ChromaDB uses embeddings for semantic intent. Combining both gives precision on statutory terms and recall on user queries.'</i>", table_cell)
        ],
        [
            Paragraph("<b>Q3: Why use LangGraph for financial agents?</b>", table_cell_bold),
            Paragraph("<i>'LangGraph provides stateful graph execution with MemorySaver. We implement conditional routing and human-in-the-loop approval gates where execution halts until the user approves parameters before computing loans.'</i>", table_cell)
        ],
        [
            Paragraph("<b>Q4: Why not let the LLM calculate subsidies?</b>", table_cell_bold),
            Paragraph("<i>'LLMs are probabilistic language models prone to rounding and arithmetic errors. In finance, incorrect calculations reject bank applications. Our Python tool performs 100% audited math down to the rupee.'</i>", table_cell)
        ],
        [
            Paragraph("<b>Q5: What is Question 6 (Q6) defensive refusal?</b>", table_cell_bold),
            Paragraph("<i>'When asked for personal loan application tracking, UdyamSathi refuses honestly: I do not have access to live bank core systems. This achieved 100% refusal accuracy in our benchmark, preventing false promises.'</i>", table_cell)
        ],
        [
            Paragraph("<b>Q6: How does in-memory caching optimize production?</b>", table_cell_bold),
            Paragraph("<i>'Repeated queries are hashed in an in-memory TTL cache, returning in <2.5 ms with X-Cache: HIT. This reduces LLM API token expenditure by 100% on identical queries.'</i>", table_cell)
        ]
    ]
    t_qa = Table(qa_data, colWidths=[160, 344])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_qa)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated successfully at {filename}")

if __name__ == "__main__":
    build_pdf()
    build_pdf("UdyamSathi_Demo_Day_Master_Guide.pdf")
