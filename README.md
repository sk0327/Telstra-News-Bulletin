# 📡 Client Intel Monitor

A weekly news monitoring agent for **Telstra** and **StarHub** — built with Python, Groq, and Streamlit.

## Features
- Fetches latest news from Google News RSS feeds for each client
- Uses Groq (Llama 3.3 70B) to summarise top articles into structured briefs
- Generates a combined executive digest across both clients
- Three brief tones: Executive, Analyst, Quick Scan
- Clean terminal-inspired dark UI

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

## Usage
1. Enter your **Groq API key** in the sidebar (get one free at https://console.groq.com)
2. Choose LLM model and brief tone
3. Click **RUN DIGEST**

## Deploy to Streamlit Cloud
1. Push this repo to GitHub
2. Go to https://share.streamlit.io → New app
3. Select your repo and `app.py`
4. Add `GROQ_API_KEY` as a secret (optional — users can also enter it in the sidebar)

## File Structure
```
app.py            ← main Streamlit application
requirements.txt  ← Python dependencies
README.md         ← this file
```
