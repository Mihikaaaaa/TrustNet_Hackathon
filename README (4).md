# 🛡️ TrustNet

**AI-Powered Financial Safety & Literacy Companion**

TrustNet protects India's financially vulnerable — gig workers, daily-wage earners, elderly citizens, and first-time smartphone users — from scams, while teaching them to grow their money. Two problems, one app, one closed loop: **Protect → Educate → Grow**.

---

## ✨ Why TrustNet?

Financially vulnerable users face a two-sided crisis:

- 📵 They're prime targets for **fake KYC updates, OTP theft, and fraudulent loan calls**.
- 📉 Budgeting apps assume a fixed monthly salary — they break down for **irregular, daily, or seasonal income**.
- 🗣️ Financial terms like EMI, credit score, and interest are explained in **English jargon**, excluding Hindi/Hinglish-first users.
- 🧩 Existing apps solve only one side — scam detectors don't teach financial habits, and savings apps don't protect against fraud.

**TrustNet closes both loops in a single, offline-first, bilingual app.**

---

## 🧩 Features

### 🚨 Scam Shield
Real-time, explainable scam detection for SMS and call transcripts — in **Hindi, English, and Hinglish**.

- Paste any message and get an instant **risk score**: ✅ Safe · 🟡 Be Careful · ⚠️ High Risk
- **Explainable, not a black box** — see exactly *why* a message was flagged:
  - ⏱️ Urgency pressure
  - 🔑 OTP / bank / KYC requests
  - 🎁 Too-good-to-be-true money offers
  - ⚠️ Threats of account suspension
  - 🔗 Suspicious links or call-to-action
- **Runs fully offline** — no API key, no internet call, zero per-message cost.
- Includes a "🎓 Learn from this" tip so users get smarter with every flagged message.

### 💰 Money Coach
A financial companion built for **irregular income**, not fixed monthly salaries.

- 📒 **Track income & expenses** day by day, even with fluctuating gig/daily wages.
- 🎯 Get a **realistic micro-savings goal**, calculated from your actual average daily income (not a fantasy budget).
- 📊 Visual breakdown of income vs. expenses.
- 💬 **Ask Money Coach** anything — *"What is EMI?"*, *"Credit score kya hota hai?"* — answered in plain language, in whichever language you asked, with real-life examples (auto driver, vegetable seller, daily-wage worker) and zero jargon.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Scam Shield (Guard)** | TF-IDF + Naive Bayes classifier, trained on hand-curated Hindi/English/Hinglish scam vs. genuine messages, layered with rule-based keyword signals for explainability |
| **Money Coach (Coach)** | Google Gemini (`gemini-2.0-flash`) via LangChain, for plain-language conversational finance coaching |
| **Frontend** | [Streamlit](https://streamlit.io) — lightweight, mobile-friendly, runs smoothly on low-end phones |
| **Data** | Pandas — for tracking income/expense entries and computing savings goals |

---

## 🚀 Getting Started

### 1. Clone & install dependencies

```bash
pip install streamlit pandas scikit-learn langchain-google-genai
```

### 2. Run the app

```bash
streamlit run app.py
```

### 3. (Optional) Add a Gemini API key

Scam Shield works **completely offline** with no key required. To use the **Money Coach chat**, get a free API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey) and paste it into the sidebar.

---

## 🗂️ App Structure

```
app.py
├── Sidebar          → navigation + optional Gemini API key input
├── 🏠 Home          → overview of both modules
├── 🚨 Scam Shield   → paste a message → get risk score + plain-language explanation
└── 💰 Money Coach
    ├── 📒 Track Income & Expenses → daily entries, balance, suggested savings goal
    └── 💬 Ask Money Coach         → chat assistant for financial questions
```

---

## 🎯 Design Principles

- **Explainable, not black-box** — every scam flag shows its reasoning.
- **Built for irregular income** — savings goals scale with real daily earnings.
- **Bilingual by design** — Hindi, English, and Hinglish, not English-only.
- **Offline-first protection** — Scam Shield needs no internet or API key.
- **Jargon-free coaching** — financial concepts explained the way a neighbor would.
- **One closed loop** — protection and literacy live in a single trusted app.

---

## 🗺️ Roadmap

- **Phase 1 — Prototype (current):** Functional Scam Shield + Money Coach, fully demoable.
- **Phase 2 — Dataset Hardening:** Expand training data with public scam-SMS datasets.
- **Phase 3 — Feature Depth:** On-device SMS/call integration, savings streaks, personalized nudges.
- **Phase 4 — Partnerships:** Pilot with gig platforms and microfinance NGOs to reach real first-time smartphone users.

---

## 👥 Team — Nexgencoders

| Name | Role |
|---|---|
| Mihika Srivastava | Team Lead |
| Pranav Dua | AI/Backend Architect |
| Jyoti Shokeen | Frontend Developer |
| Akash Acharya | Data Strategist |
| Tanmay Saraf | Project Coordinator & UI/UX |

---

## 📜 Theme & Category

**Theme:** AI for Real-World Impact
**Category:** FinTech / Financial Inclusion

> *A practical, student-driven prototype with a clear path to scalable social impact in financial inclusion.*
