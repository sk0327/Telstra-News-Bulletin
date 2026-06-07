import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from groq import Groq
import time

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Client Intel Monitor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0a0e17;
    color: #c9d1e0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0d1220;
    border-right: 1px solid #1e2a3a;
}
[data-testid="stSidebar"] * {
    color: #c9d1e0 !important;
}

/* Main background */
.stApp { background-color: #0a0e17; }

/* Header strip */
.header-strip {
    background: linear-gradient(90deg, #0d1220 0%, #0f1e35 50%, #0d1220 100%);
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.header-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px;
    font-weight: 600;
    color: #4fc3f7;
    letter-spacing: 1px;
}
.header-sub {
    font-size: 12px;
    color: #5a7a9a;
    font-family: 'IBM Plex Mono', monospace;
    margin-top: 4px;
}
.header-badge {
    background: #0d2137;
    border: 1px solid #1a4a6a;
    border-radius: 4px;
    padding: 6px 12px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #4fc3f7;
}

/* Client cards */
.client-section {
    background: #0d1220;
    border: 1px solid #1e2a3a;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.client-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #1e2a3a;
}
.client-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #4fc3f7;
    box-shadow: 0 0 8px #4fc3f7;
}
.client-name {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 14px;
    font-weight: 600;
    color: #4fc3f7;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.client-country {
    font-size: 11px;
    color: #5a7a9a;
    margin-left: auto;
    font-family: 'IBM Plex Mono', monospace;
}

/* News items */
.news-item {
    background: #0a1628;
    border-left: 3px solid #1a4a6a;
    border-radius: 0 6px 6px 0;
    padding: 12px 16px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.news-item:hover { border-left-color: #4fc3f7; }
.news-title {
    font-size: 13px;
    font-weight: 500;
    color: #d0dff0;
    margin-bottom: 4px;
}
.news-meta {
    font-size: 11px;
    color: #3d5a7a;
    font-family: 'IBM Plex Mono', monospace;
}
.news-summary {
    font-size: 12px;
    color: #7a9ab8;
    margin-top: 6px;
    line-height: 1.5;
}

/* Summary box */
.ai-summary-box {
    background: #061428;
    border: 1px solid #1a4a6a;
    border-radius: 8px;
    padding: 16px 20px;
    margin-top: 16px;
}
.ai-summary-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #4fc3f7;
    letter-spacing: 2px;
    margin-bottom: 8px;
    text-transform: uppercase;
}
.ai-summary-text {
    font-size: 13px;
    color: #a0c0d8;
    line-height: 1.7;
}

/* Pipeline steps */
.pipeline {
    display: flex;
    gap: 0;
    margin-bottom: 24px;
    flex-wrap: wrap;
}
.step {
    flex: 1;
    min-width: 100px;
    background: #0d1220;
    border: 1px solid #1e2a3a;
    padding: 12px 10px;
    text-align: center;
    position: relative;
}
.step:first-child { border-radius: 8px 0 0 8px; }
.step:last-child  { border-radius: 0 8px 8px 0; }
.step-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 18px;
    font-weight: 600;
    color: #1e3a5a;
}
.step-label {
    font-size: 11px;
    color: #5a7a9a;
    margin-top: 2px;
}
.step.active .step-num { color: #4fc3f7; }
.step.active .step-label { color: #4fc3f7; }
.step.done .step-num { color: #2ecc71; }
.step.done .step-label { color: #2ecc71; }

/* Buttons */
.stButton > button {
    background: #0d2137 !important;
    color: #4fc3f7 !important;
    border: 1px solid #1a4a6a !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
    width: 100%;
}
.stButton > button:hover {
    background: #1a3a5a !important;
    border-color: #4fc3f7 !important;
    box-shadow: 0 0 16px rgba(79,195,247,0.2) !important;
}

/* Input fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0d1220 !important;
    border: 1px solid #1e2a3a !important;
    border-radius: 6px !important;
    color: #c9d1e0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label {
    color: #5a7a9a !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* Divider */
hr { border-color: #1e2a3a !important; }

/* Metric cards */
.metric-row { display: flex; gap: 12px; margin-bottom: 20px; }
.metric-card {
    flex: 1;
    background: #0d1220;
    border: 1px solid #1e2a3a;
    border-radius: 8px;
    padding: 14px 18px;
    text-align: center;
}
.metric-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    color: #4fc3f7;
}
.metric-lbl {
    font-size: 11px;
    color: #5a7a9a;
    margin-top: 2px;
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Expander override */
details { background: #0d1220 !important; }
summary { color: #4fc3f7 !important; font-family: 'IBM Plex Mono', monospace !important; }

/* Hide Streamlit branding */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
CLIENTS = {
   "Telstra": {
    "country": "🇦🇺 Australia",
    "dot_color": "#4fc3f7",
    "feeds": [
        "https://news.google.com/rss/search?q=Telstra+site:telstra.com.au&hl=en-AU&gl=AU&ceid=AU:en",
        "https://news.google.com/rss/search?q=Telstra+media+release+site:telstra.com.au&hl=en-AU&gl=AU&ceid=AU:en",
    ],
       
    },
    "StarHub": {
        "country": "🇸🇬 Singapore",
        "dot_color": "#f06292",
        "feeds": [
            "https://news.google.com/rss/search?q=StarHub+Singapore+telecom&hl=en-SG&gl=SG&ceid=SG:en",
            "https://news.google.com/rss/search?q=StarHub+5G+Singapore&hl=en&gl=SG&ceid=SG:en",
        ],
        "keywords": ["StarHub", "Singapore telecom", "SG telco", "StarHub earnings"],
    },
}


def fetch_rss_articles(client_name: str, max_items: int = 10) -> list[dict]:
    """Fetch articles from Google News RSS for a client."""
    articles = []
    seen = set()
    for feed_url in CLIENTS[client_name]["feeds"]:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:max_items]:
                title = entry.get("title", "")
                if title in seen:
                    continue
                seen.add(title)
                articles.append({
                    "title": title,
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", "")[:300],
                    "source": entry.get("source", {}).get("title", "Google News"),
                })
        except Exception as e:
            st.warning(f"Feed error for {client_name}: {e}")
    return articles[:max_items]


def groq_summarize(client_name: str, articles: list[dict], api_key: str, model: str, tone: str) -> str:
    """Use Groq to summarise news articles into a client intel brief."""
    if not articles:
        return "No articles found for this client this week."

    client = Groq(api_key=api_key)
    articles_text = "\n\n".join([
        f"[{i+1}] {a['title']}\nSource: {a['source']} | {a['published']}\n{a['summary']}"
        for i, a in enumerate(articles)
    ])

    tone_instructions = {
        "Executive Brief": "Be concise, strategic, and high-level. Focus on business implications.",
        "Analyst Deep-Dive": "Be thorough and analytical. Highlight trends, risks, and opportunities.",
        "Quick Scan": "Be very brief. Use short bullet points. Maximum 4 lines.",
    }

    prompt = f"""You are an enterprise client intelligence analyst. 
Analyse the following recent news about {client_name} and produce a structured weekly brief.

{tone_instructions.get(tone, "")}

Format your response as:
**📌 Key Developments** (2–3 bullet points on most important news)
**📈 Business Impact** (1–2 sentences on what this means strategically)
**⚠️ Watch Points** (1 bullet on risks or items to monitor)

Keep the total response under 200 words. Be specific — name products, numbers, dates where present.

NEWS ARTICLES:
{articles_text}"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.4,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Groq API error: {e}"


def groq_combined_digest(telstra_summary: str, starhub_summary: str, api_key: str, model: str) -> str:
    """Generate a combined executive digest."""
    client = Groq(api_key=api_key)
    prompt = f"""You are a senior account manager preparing a Monday morning team briefing.

Based on these two client intel summaries, write a 3–4 sentence combined executive digest 
that highlights the most important cross-client themes, contrasts, or actions needed this week.

TELSTRA BRIEF:
{telstra_summary}

STARHUB BRIEF:
{starhub_summary}

Start directly with the content. No preamble. Be direct and actionable."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family: IBM Plex Mono, monospace; font-size: 11px; 
                color: #4fc3f7; letter-spacing: 2px; margin-bottom: 20px;
                text-transform: uppercase; border-bottom: 1px solid #1e2a3a; padding-bottom: 12px;'>
        ⚙ Configuration
    </div>
    """, unsafe_allow_html=True)

    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get your free API key at console.groq.com"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    model_choice = st.selectbox(
        "LLM Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
        index=0,
    )

    tone_choice = st.selectbox(
        "Brief Tone",
        ["Executive Brief", "Analyst Deep-Dive", "Quick Scan"],
        index=0,
    )

    max_articles = st.slider("Articles per client", 3, 10, 6)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family: IBM Plex Mono, monospace; font-size: 10px; 
                color: #3d5a7a; line-height: 1.6;'>
    PIPELINE<br>
    ① Fetch Google News RSS<br>
    ② Parse & deduplicate<br>
    ③ Groq LLM summarise<br>
    ④ Format digest<br>
    ⑤ Deliver in-app<br>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family: IBM Plex Mono, monospace; font-size: 10px; color: #2a4a6a;'>
    CLIENT INTEL MONITOR v1.0<br>
    Powered by Groq + Streamlit
    </div>
    """, unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
now = datetime.now()
st.markdown(f"""
<div class="header-strip">
    <div>
        <div class="header-title">📡 CLIENT INTEL MONITOR</div>
        <div class="header-sub">Telstra · StarHub · Automated Weekly Brief</div>
    </div>
    <div class="header-badge">
        WK {now.strftime('%V')} · {now.strftime('%a %d %b %Y')}
    </div>
</div>
""", unsafe_allow_html=True)


# ── Run Button ────────────────────────────────────────────────────────────────
col_btn, col_info = st.columns([1, 3])
with col_btn:
    run_btn = st.button("⚡ RUN DIGEST", use_container_width=True)
with col_info:
    if not groq_api_key:
        st.markdown("""
        <div style='font-family: IBM Plex Mono, monospace; font-size: 12px; 
                    color: #f0a500; padding: 10px; background: #1a1000; 
                    border: 1px solid #3a2800; border-radius: 6px; margin-top: 4px;'>
            ⚠ Enter your Groq API key in the sidebar to run the agent
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='font-family: IBM Plex Mono, monospace; font-size: 12px; 
                    color: #2ecc71; padding: 10px; background: #001a0a; 
                    border: 1px solid #004a1a; border-radius: 6px; margin-top: 4px;'>
            ✓ API key set · Ready to fetch news and generate summaries
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ── Main Logic ────────────────────────────────────────────────────────────────
if run_btn:
    if not groq_api_key:
        st.error("Please enter your Groq API key in the sidebar.")
        st.stop()

    results = {}
    summaries = {}

    # Pipeline progress
    progress_container = st.empty()
    status_text = st.empty()

    for step_i, (step_label, step_detail) in enumerate([
        ("Trigger", "Initialising agent run..."),
        ("Fetch News", "Collecting articles from RSS feeds..."),
        ("AI Summarize", "Running Groq LLM summarisation..."),
        ("Format", "Assembling digest..."),
        ("Deliver", "Rendering output..."),
    ]):
        progress_container.progress((step_i + 1) / 5)
        status_text.markdown(f"""
        <div style='font-family: IBM Plex Mono, monospace; font-size: 12px; color: #4fc3f7;'>
            STEP {step_i+1}/5 · {step_label.upper()} · {step_detail}
        </div>
        """, unsafe_allow_html=True)

        if step_i == 1:
            # Fetch articles
            for client in CLIENTS:
                with st.spinner(f"Fetching {client} news..."):
                    results[client] = fetch_rss_articles(client, max_articles)

        elif step_i == 2:
            # Summarise
            for client in CLIENTS:
                with st.spinner(f"Summarising {client} with Groq..."):
                    summaries[client] = groq_summarize(
                        client, results[client], groq_api_key, model_choice, tone_choice
                    )

        time.sleep(0.3)

    progress_container.empty()
    status_text.empty()

    # ── Metrics ───────────────────────────────────────────────────────────────
    total_articles = sum(len(v) for v in results.values())
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-val">{total_articles}</div>
            <div class="metric-lbl">Articles Fetched</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">2</div>
            <div class="metric-lbl">Clients Covered</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{model_choice.split('-')[0].upper()}</div>
            <div class="metric-lbl">LLM Model</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{tone_choice.split()[0]}</div>
            <div class="metric-lbl">Brief Style</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Combined Executive Digest ─────────────────────────────────────────────
    if all(k in summaries for k in CLIENTS):
        with st.spinner("Generating combined executive digest..."):
            combined = groq_combined_digest(
                summaries["Telstra"], summaries["StarHub"], groq_api_key, model_choice
            )
        st.markdown(f"""
        <div style='background: #060f1e; border: 1px solid #1a4a6a; border-radius: 10px; 
                    padding: 20px 24px; margin-bottom: 24px;'>
            <div style='font-family: IBM Plex Mono, monospace; font-size: 10px; 
                        color: #4fc3f7; letter-spacing: 3px; margin-bottom: 12px;'>
                ▶ COMBINED EXECUTIVE DIGEST — WEEK {now.strftime('%V')}
            </div>
            <div style='font-size: 14px; color: #b0cce0; line-height: 1.8;'>
                {combined.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Per-Client Sections ───────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    cols = {"Telstra": col1, "StarHub": col2}

    for client_name, col in cols.items():
        info = CLIENTS[client_name]
        articles = results.get(client_name, [])
        summary = summaries.get(client_name, "")

        with col:
            st.markdown(f"""
            <div class="client-section">
                <div class="client-header">
                    <div class="client-dot" style="background:{info['dot_color']}; box-shadow: 0 0 8px {info['dot_color']};"></div>
                    <div class="client-name" style="color:{info['dot_color']}">{client_name}</div>
                    <div class="client-country">{info['country']}</div>
                </div>
            """, unsafe_allow_html=True)

            if summary:
                st.markdown(f"""
                <div class="ai-summary-box">
                    <div class="ai-summary-label">▸ AI Intel Brief</div>
                    <div class="ai-summary-text">{summary.replace(chr(10), '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Articles expander
            with st.expander(f"📰 {len(articles)} source articles"):
                for art in articles:
                    pub = art.get("published", "")[:16] if art.get("published") else ""
                    title = art.get("title", "No title")
                    source = art.get("source", "")
                    link = art.get("link", "#")
                    snippet = art.get("summary", "")[:180]
                    st.markdown(f"""
                    <div class="news-item">
                        <div class="news-title">
                            <a href="{link}" target="_blank" style="color:#d0dff0; text-decoration:none;">
                                {title}
                            </a>
                        </div>
                        <div class="news-meta">{source} · {pub}</div>
                        {"<div class='news-summary'>" + snippet + "...</div>" if snippet else ""}
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='text-align:center; font-family: IBM Plex Mono, monospace; 
                font-size: 11px; color: #2a4a6a; margin-top: 32px; padding-top: 20px;
                border-top: 1px solid #1e2a3a;'>
        DIGEST GENERATED · {now.strftime('%Y-%m-%d %H:%M:%S')} · MODEL: {model_choice}
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Empty State ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style='text-align: center; padding: 60px 20px;'>
        <div style='font-size: 48px; margin-bottom: 16px;'>📡</div>
        <div style='font-family: IBM Plex Mono, monospace; font-size: 16px; 
                    color: #4fc3f7; margin-bottom: 10px;'>
            AGENT STANDING BY
        </div>
        <div style='font-size: 13px; color: #3d5a7a; max-width: 420px; 
                    margin: 0 auto; line-height: 1.7;'>
            Configure your Groq API key in the sidebar, then click 
            <strong style='color:#4fc3f7'>RUN DIGEST</strong> to fetch the latest 
            Telstra and StarHub news and generate AI-powered intelligence briefs.
        </div>
    </div>

    <div style='display: flex; gap: 16px; max-width: 700px; margin: 0 auto; flex-wrap: wrap;'>
    """ + "".join([f"""
        <div style='flex: 1; min-width: 200px; background: #0d1220; border: 1px solid #1e2a3a; 
                    border-radius: 10px; padding: 20px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>{icon}</div>
            <div style='font-family: IBM Plex Mono, monospace; font-size: 12px; 
                        color: #4fc3f7; margin-bottom: 6px;'>{label}</div>
            <div style='font-size: 11px; color: #3d5a7a;'>{desc}</div>
        </div>
    """ for icon, label, desc in [
        ("🌐", "LIVE NEWS FEED", "Google News RSS for Telstra & StarHub"),
        ("🤖", "GROQ LLM", "Fast inference with llama-3.3-70b"),
        ("📋", "STRUCTURED BRIEFS", "Key developments, impact & watch points"),
    ]]) + "</div>", unsafe_allow_html=True)
