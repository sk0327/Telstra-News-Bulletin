import streamlit as st
import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime
from groq import Groq
import time

# ── Page Config ───────────────────────────────────────────────────────────────
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
[data-testid="stSidebar"] {
    background-color: #0d1220;
    border-right: 1px solid #1e2a3a;
}
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
.stApp { background-color: #0a0e17; }

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
.client-name {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.client-country {
    font-size: 11px;
    color: #5a7a9a;
    margin-left: auto;
    font-family: 'IBM Plex Mono', monospace;
}
.news-item {
    background: #0a1628;
    border-left: 3px solid #1a4a6a;
    border-radius: 0 6px 6px 0;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.news-item:hover { border-left-color: #4fc3f7; }
.news-title { font-size: 13px; font-weight: 500; color: #d0dff0; margin-bottom: 4px; }
.news-meta { font-size: 11px; color: #3d5a7a; font-family: 'IBM Plex Mono', monospace; }
.news-summary { font-size: 12px; color: #7a9ab8; margin-top: 6px; line-height: 1.5; }
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
.ai-summary-text { font-size: 13px; color: #a0c0d8; line-height: 1.7; }
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
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0d1220 !important;
    border: 1px solid #1e2a3a !important;
    border-radius: 6px !important;
    color: #c9d1e0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label,
.stMultiSelect label, .stCheckbox label {
    color: #5a7a9a !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
hr { border-color: #1e2a3a !important; }
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
details { background: #0d1220 !important; }
summary { color: #4fc3f7 !important; font-family: 'IBM Plex Mono', monospace !important; }
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Load API Key from secrets ──────────────────────────────────────────────────
groq_api_key = st.secrets["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

"]

# ── Client Definitions ─────────────────────────────────────────────────────────
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
    },
    "MEASAT": {
        "country": "🇲🇾 Malaysia",
        "dot_color": "#a78bfa",
        "feeds": [
            "https://news.google.com/rss/search?q=MEASAT+satellite+Malaysia&hl=en-MY&gl=MY&ceid=MY:en",
            "https://news.google.com/rss/search?q=MEASAT+telecom+broadcast&hl=en&gl=MY&ceid=MY:en",
        ],
    },
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def parse_pub_date(pub_str: str):
    """Parse RSS published date string to datetime, return None on failure."""
    if not pub_str:
        return None
    try:
        return parsedate_to_datetime(pub_str).replace(tzinfo=None)
    except Exception:
        try:
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%SZ"):
                try:
                    return datetime.strptime(pub_str[:25], fmt[:len(pub_str[:25])]).replace(tzinfo=None)
                except Exception:
                    continue
        except Exception:
            return None


def fetch_rss_articles(client_name: str, max_items: int = 10) -> list[dict]:
    """Fetch and return articles sorted newest → oldest."""
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
                pub_str = entry.get("published", "")
                pub_dt = parse_pub_date(pub_str)
                articles.append({
                    "title": title,
                    "link": entry.get("link", ""),
                    "published": pub_str,
                    "published_dt": pub_dt,
                    "summary": entry.get("summary", "")[:300],
                    "source": entry.get("source", {}).get("title", "Google News"),
                })
        except Exception as e:
            st.warning(f"Feed error for {client_name}: {e}")

    # Sort newest → oldest (articles without dates go to bottom)
    articles.sort(key=lambda x: x["published_dt"] or datetime.min, reverse=True)
    return articles[:max_items]


def filter_by_date(articles: list[dict], month: int | None, year: int | None) -> list[dict]:
    """Filter articles by year and/or month."""
    filtered = []
    for art in articles:
        dt = art.get("published_dt")
        if dt is None:
            continue
        if year and dt.year != year:
            continue
        if month and dt.month != month:
            continue
        filtered.append(art)
    return filtered


def groq_summarize(client_name: str, articles: list[dict], api_key: str, model: str, tone: str) -> str:
    if not articles:
        return "No articles found for this client in the selected period."
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


def groq_combined_digest(summaries: dict, api_key: str, model: str) -> str:
    client = Groq(api_key=api_key)
    briefs_text = "\n\n".join([f"{name} BRIEF:\n{text}" for name, text in summaries.items()])
    client_list = " · ".join(summaries.keys())
    prompt = f"""You are a senior account manager preparing a Monday morning team briefing.

Based on these client intel summaries for {client_list}, write a 3–4 sentence combined executive digest
that highlights the most important cross-client themes, contrasts, or actions needed this week.

{briefs_text}

Start directly with the content. No preamble. Be direct and actionable."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family: IBM Plex Mono, monospace; font-size: 11px;
                color: #4fc3f7; letter-spacing: 2px; margin-bottom: 20px;
                text-transform: uppercase; border-bottom: 1px solid #1e2a3a; padding-bottom: 12px;'>
        ⚙ Settings
    </div>
    """, unsafe_allow_html=True)

    # ── Company selector ──────────────────────────────────────────────────────
    selected_clients = st.multiselect(
        "Select Clients",
        options=list(CLIENTS.keys()),
        default=list(CLIENTS.keys()),
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Date filters ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style='font-family: IBM Plex Mono, monospace; font-size: 10px;
                color: #4fc3f7; letter-spacing: 2px; margin-bottom: 10px; text-transform: uppercase;'>
        Date Filter
    </div>
    """, unsafe_allow_html=True)

    now = datetime.now()
    year_options = ["All"] + list(range(now.year, now.year - 4, -1))
    selected_year = st.selectbox("Year", year_options, index=0)

    month_names = ["All", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    selected_month_name = st.selectbox("Month", month_names, index=0)

    filter_year  = None if selected_year == "All" else int(selected_year)
    filter_month = None if selected_month_name == "All" else month_names.index(selected_month_name)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Model / tone ──────────────────────────────────────────────────────────
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
    ② Sort newest → oldest<br>
    ③ Apply date filter<br>
    ④ Groq LLM summarise<br>
    ⑤ Deliver in-app<br>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family: IBM Plex Mono, monospace; font-size: 10px; color: #2a4a6a;'>
    CLIENT INTEL MONITOR v2.0<br>
    Powered by Groq + Streamlit
    </div>
    """, unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────
client_subtitle = " · ".join(selected_clients) if selected_clients else "No clients selected"
st.markdown(f"""
<div class="header-strip">
    <div>
        <div class="header-title">📡 CLIENT INTEL MONITOR</div>
        <div class="header-sub">{client_subtitle} · Automated Weekly Brief</div>
    </div>
    <div class="header-badge">
        WK {now.strftime('%V')} · {now.strftime('%a %d %b %Y')}
    </div>
</div>
""", unsafe_allow_html=True)


# ── Run Button ─────────────────────────────────────────────────────────────────
col_btn, col_info = st.columns([1, 3])
with col_btn:
    run_btn = st.button("⚡ RUN DIGEST", use_container_width=True)
with col_info:
    if not selected_clients:
        st.markdown("""
        <div style='font-family: IBM Plex Mono, monospace; font-size: 12px;
                    color: #f0a500; padding: 10px; background: #1a1000;
                    border: 1px solid #3a2800; border-radius: 6px; margin-top: 4px;'>
            ⚠ Select at least one client from the sidebar
        </div>
        """, unsafe_allow_html=True)
    else:
        filter_label = []
        if filter_year:  filter_label.append(str(filter_year))
        if filter_month: filter_label.append(month_names[filter_month])
        date_info = " · FILTER: " + " ".join(filter_label) if filter_label else " · NO DATE FILTER"
        st.markdown(f"""
        <div style='font-family: IBM Plex Mono, monospace; font-size: 12px;
                    color: #2ecc71; padding: 10px; background: #001a0a;
                    border: 1px solid #004a1a; border-radius: 6px; margin-top: 4px;'>
            ✓ API key loaded · {len(selected_clients)} client(s) selected{date_info}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ── Main Logic ─────────────────────────────────────────────────────────────────
if run_btn:
    if not selected_clients:
        st.error("Please select at least one client from the sidebar.")
        st.stop()

    results   = {}
    summaries = {}

    progress_container = st.empty()
    status_text        = st.empty()

    steps = [
        ("Trigger",      "Initialising agent run..."),
        ("Fetch News",   "Collecting articles from RSS feeds..."),
        ("Filter",       "Applying date filter & sorting..."),
        ("AI Summarize", "Running Groq LLM summarisation..."),
        ("Deliver",      "Rendering output..."),
    ]

    for step_i, (step_label, step_detail) in enumerate(steps):
        progress_container.progress((step_i + 1) / len(steps))
        status_text.markdown(f"""
        <div style='font-family: IBM Plex Mono, monospace; font-size: 12px; color: #4fc3f7;'>
            STEP {step_i+1}/{len(steps)} · {step_label.upper()} · {step_detail}
        </div>
        """, unsafe_allow_html=True)

        if step_i == 1:
            for client in selected_clients:
                with st.spinner(f"Fetching {client} news..."):
                    results[client] = fetch_rss_articles(client, max_articles)

        elif step_i == 2:
            for client in selected_clients:
                results[client] = filter_by_date(results[client], filter_month, filter_year)

        elif step_i == 3:
            for client in selected_clients:
                with st.spinner(f"Summarising {client} with Groq..."):
                    summaries[client] = groq_summarize(
                        client, results[client], groq_api_key, model_choice, tone_choice
                    )

        time.sleep(0.3)

    progress_container.empty()
    status_text.empty()

    # ── Metrics ───────────────────────────────────────────────────────────────
    total_articles = sum(len(v) for v in results.values())
    filter_str = " ".join(filter(None, [
        month_names[filter_month] if filter_month else None,
        str(filter_year) if filter_year else None
    ])) or "ALL TIME"

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-val">{total_articles}</div>
            <div class="metric-lbl">Articles Fetched</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{len(selected_clients)}</div>
            <div class="metric-lbl">Clients Covered</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{filter_str}</div>
            <div class="metric-lbl">Date Filter</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{tone_choice.split()[0]}</div>
            <div class="metric-lbl">Brief Style</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Combined Executive Digest (only if 2+ clients) ────────────────────────
    if len(summaries) >= 2:
        with st.spinner("Generating combined executive digest..."):
            combined = groq_combined_digest(summaries, groq_api_key, model_choice)
        st.markdown(f"""
        <div style='background: #060f1e; border: 1px solid #1a4a6a; border-radius: 10px;
                    padding: 20px 24px; margin-bottom: 24px;'>
            <div style='font-family: IBM Plex Mono, monospace; font-size: 10px;
                        color: #4fc3f7; letter-spacing: 3px; margin-bottom: 12px;'>
                ▶ COMBINED EXECUTIVE DIGEST — WEEK {now.strftime('%V')} · {filter_str}
            </div>
            <div style='font-size: 14px; color: #b0cce0; line-height: 1.8;'>
                {combined.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Per-Client Sections ───────────────────────────────────────────────────
    num_cols = min(len(selected_clients), 3)
    cols = st.columns(num_cols)

    for i, client_name in enumerate(selected_clients):
        info     = CLIENTS[client_name]
        articles = results.get(client_name, [])
        summary  = summaries.get(client_name, "")

        with cols[i % num_cols]:
            st.markdown(f"""
            <div class="client-section">
                <div class="client-header">
                    <div style='width:10px;height:10px;border-radius:50%;
                                background:{info["dot_color"]};
                                box-shadow:0 0 8px {info["dot_color"]};'></div>
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

            with st.expander(f"📰 {len(articles)} source articles — newest first"):
                if not articles:
                    st.markdown("""
                    <div style='font-family:IBM Plex Mono,monospace;font-size:12px;color:#3d5a7a;padding:12px;'>
                        No articles found for the selected date range.
                    </div>
                    """, unsafe_allow_html=True)
                for art in articles:
                    dt   = art.get("published_dt")
                    pub  = dt.strftime("%d %b %Y") if dt else art.get("published", "")[:16]
                    title   = art.get("title", "No title")
                    source  = art.get("source", "")
                    link    = art.get("link", "#")
                    snippet = art.get("summary", "")[:180]
                    st.markdown(f"""
                    <div class="news-item">
                        <div class="news-title">
                            <a href="{link}" target="_blank" style="color:#d0dff0;text-decoration:none;">
                                {title}
                            </a>
                        </div>
                        <div class="news-meta">{source} · {pub}</div>
                        {"<div class='news-summary'>" + snippet + "...</div>" if snippet else ""}
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='text-align:center;font-family:IBM Plex Mono,monospace;
                font-size:11px;color:#2a4a6a;margin-top:32px;padding-top:20px;
                border-top:1px solid #1e2a3a;'>
        DIGEST GENERATED · {now.strftime('%Y-%m-%d %H:%M:%S')} · MODEL: {model_choice} · FILTER: {filter_str}
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Empty State ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center;padding:60px 20px;'>
        <div style='font-size:48px;margin-bottom:16px;'>📡</div>
        <div style='font-family:IBM Plex Mono,monospace;font-size:16px;
                    color:#4fc3f7;margin-bottom:10px;'>
            AGENT STANDING BY
        </div>
        <div style='font-size:13px;color:#3d5a7a;max-width:420px;
                    margin:0 auto;line-height:1.7;'>
            Select clients and optional date filters in the sidebar,
            then click <strong style='color:#4fc3f7'>RUN DIGEST</strong> to generate
            AI-powered intelligence briefs.
        </div>
    </div>
    <div style='display:flex;gap:16px;max-width:800px;margin:0 auto;flex-wrap:wrap;'>
    """ + "".join([f"""
        <div style='flex:1;min-width:180px;background:#0d1220;border:1px solid #1e2a3a;
                    border-radius:10px;padding:20px;text-align:center;'>
            <div style='font-size:24px;margin-bottom:8px;'>{icon}</div>
            <div style='font-family:IBM Plex Mono,monospace;font-size:12px;
                        color:{color};margin-bottom:6px;'>{label}</div>
            <div style='font-size:11px;color:#3d5a7a;'>{desc}</div>
        </div>
    """ for icon, label, color, desc in [
        ("🇦🇺", "TELSTRA",  "#4fc3f7", "Australia · Telecom & NBN"),
        ("🇸🇬", "STARHUB",  "#f06292", "Singapore · 5G & Broadband"),
        ("🇲🇾", "MEASAT",   "#a78bfa", "Malaysia · Satellite & Broadcast"),
        ("📅", "DATE FILTER", "#4fc3f7", "Filter by month & year"),
    ]]) + "</div>", unsafe_allow_html=True)
