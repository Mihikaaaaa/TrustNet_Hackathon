# TrustNet — AI-Powered Financial Safety & Literacy Companion

Halfathon build. Two modules, one Streamlit app.

## Setup (5 minutes)

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Get a free Gemini API key (only needed for Money Coach chat)
1. Go to https://aistudio.google.com/apikey
2. Sign in, click "Create API key"
3. Paste it into the sidebar when the app is running

Scam Shield needs **no key at all** — it runs on a local ML classifier.

## Demo script for judges (2–3 minutes)

1. **Home** — 30 seconds explaining the two-sided problem (scams + no literacy tools).
2. **Scam Shield**:
   - Paste a scam example: `Aapka KYC turant update karein warna account block ho jayega, link par click karein`
     → shows HIGH RISK + lists exactly which words triggered it (urgency, KYC, threat, link).
   - Paste a normal message: `Meeting kal subah 10 baje hai office mein`
     → shows LOOKS SAFE.
   - Point out: it explains *why*, so the user learns the pattern, not just gets a black-box popup.
3. **Money Coach**:
   - Add 2–3 income/expense entries (e.g. Income ₹400 "daily wage", Expense ₹150 "food").
   - Show the auto-suggested micro-savings goal based on average daily income.
   - Ask the chat: `What is EMI?` → shows a plain-language answer with a real-life example, no jargon.

## What to say if judges ask "why not just use ChatGPT for both?"
- Scam Shield is a **local trained classifier** — instant, works offline, no API cost per message,
  and gives structured, explainable signals (not just free-text from an LLM).
- Money Coach uses an LLM specifically for the conversational/explanatory layer, where free-text,
  context-aware answers actually help — while the tracker and savings-goal math are deterministic,
  not hallucinated.
- Together they close the loop: protect money first (Scam Shield), then grow understanding of it
  (Money Coach) — one app, one target user, both sides of the problem.

## Possible "next steps" to mention if there's a Q&A
- Add a real labeled scam-SMS dataset (e.g. public Kaggle spam datasets) to strengthen the classifier.
- Add voice input for low-literacy users (speech-to-text for both modules).
- SMS/call integration via Android permissions for real-time on-device flagging.
