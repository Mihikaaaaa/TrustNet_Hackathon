"""
TrustNet — AI-Powered Financial Safety & Literacy Companion
Halfathon build. Two modules in one app:
  1. Scam Shield  -> detects fraudulent SMS/call text (Hindi/English/Hinglish)
  2. Money Coach   -> tracks irregular income/expenses + explains money concepts simply

Run:  streamlit run app.py
"""

import re
import json
import streamlit as st
import pandas as pd
from datetime import date
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# =========================================================
# STEP 1: Page config
# =========================================================
st.set_page_config(page_title="TrustNet", page_icon="🛡️", layout="wide")

# =========================================================
# STEP 2: Sidebar — API key + nav (Gemini used only for Money Coach chat)
# =========================================================
st.sidebar.title("🛡️ TrustNet")
st.sidebar.caption("AI-Powered Financial Safety & Literacy Companion")

api_key = st.sidebar.text_input(
    "Google Gemini API Key (for Money Coach chat only)",
    type="password",
    help="Scam Shield works fully offline with NO key. Only the Money Coach chat "
         "assistant needs this. Get a free key at aistudio.google.com/apikey",
)

page = st.sidebar.radio("Go to", ["🏠 Home", "🚨 Scam Shield", "💰 Money Coach"])

st.sidebar.markdown("---")
st.sidebar.caption(
    "Built for financially vulnerable users — gig workers, daily-wage earners, "
    "elderly citizens, first-time smartphone users."
)

# =========================================================
# STEP 3: Shared helper — extract_json (used for Money Coach structured replies)
# =========================================================
def extract_json(raw_text):
    """Pull the first {...} JSON block out of an LLM response and parse it."""
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def get_llm():
    """Lazy import + init so the app runs even if langchain_google_genai isn't
    needed (Scam Shield doesn't need it, keeps startup fast)."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=0.4,
    )


# =========================================================
# STEP 4: Scam Shield — training data (Hindi / English / Hinglish, mixed)
# Small hand-built dataset so the whole thing runs instantly, offline, no API.
# =========================================================
SCAM_SAMPLES = [
    # --- SCAM (label 1) ---
    "Your KYC will be blocked today. Update immediately by clicking this link or your account will be suspended",
    "Aapka bank account block ho jayega, turant KYC update karein is link par click karke",
    "Congratulations! You have won Rs 25,00,000 lottery. Share your OTP to claim the prize now",
    "URGENT: Your SBI account has been suspended. Verify your account number and OTP immediately",
    "Aapko RBI se loan approve hua hai bina kisi document ke, sirf processing fee bhejein",
    "Dear customer your ATM card is blocked, call this number and share your PIN and OTP to reactivate",
    "Last warning: pay Rs 499 now or your electricity connection will be cut today",
    "Free recharge of Rs 1000 only for next 10 minutes, click link and enter your bank details",
    "Aapka parcel customs mein ruka hai, custom duty turant pay karein is link se",
    "Income tax refund of Rs 15,750 is pending, share your OTP and account number to receive it",
    "Job offer: work from home, earn Rs 5000 daily, pay Rs 999 registration fee first to start",
    "Your account will be permanently closed in 2 hours. Verify now by sharing OTP",
    "Aap lottery jeet gaye hain, apna Aadhaar number aur OTP turant bhejein claim ke liye",
    "This is bank official, we need your CVV and OTP to stop unauthorized transaction happening right now",
    "Click here to update PAN card link to avoid account freeze, response required within 1 hour",
    "Sir aapka loan sirf 1 ghante mein approve, koi documents nahi chahiye, bas advance fee bhejo",
    "Your credit card is about to expire, share the CVV number to renew instantly",
    "Emergency: your child's school fee payment failed, click this link and pay immediately",
    "Aap select huye hain free gold coin scheme mein, apna bank details aur OTP share karein",
    "We noticed suspicious login, verify identity now or account gets deleted permanently within 24 hours",
    "Turant apna UPI PIN batayein warna aapka wallet lock ho jayega abhi ke abhi",
    "Aapka SIM card kal band ho jayega, KYC verify karne ke liye yeh link kholein aur OTP dein",
    "You are pre-approved for instant personal loan of 5 lakh, no paperwork, just share Aadhaar OTP",
    "Bank se call kar raha hoon, aapke account mein fraud transaction hua hai, OTP bataiye rokne ke liye",
    "Limited time offer, double your money in 3 days, invest now and share your account password",
]

LEGIT_SAMPLES = [
    # --- LEGIT (label 0) ---
    "Your OTP for login is 482913. Do not share this OTP with anyone including bank staff",
    "Aapka salary is month ke 5 tareekh ko account mein credit ho gaya hai",
    "Reminder: your electricity bill of Rs 850 is due on 15th, pay via official app to avoid late fee",
    "Thank you for your payment of Rs 200, your recharge is successful, valid till next month",
    "Meeting kal subah 10 baje office mein hai, please samay par pahunchiye",
    "Your order has been shipped and will be delivered by tomorrow evening",
    "Aaj ka mausam accha hai, chaliye market chalte hain shaam ko",
    "Your monthly bank statement is now available in the mobile app, please review",
    "Bhai kal chai peene chalein kya, mujhe kuch baat karni hai",
    "Your appointment with the doctor is confirmed for 4 PM on Friday",
    "Congratulations on completing your training, certificate will be mailed to you next week",
    "Aapka ration card ready hai, ration dukaan se collect kar sakte hain",
    "Please find attached the invoice for last month's work, let me know if you have questions",
    "Water supply will be interrupted tomorrow from 10 AM to 2 PM for maintenance work",
    "Ma, khana kha liya, aap bhi khana kha lena time se",
    "Your gas cylinder booking is confirmed, delivery expected within 2 days",
    "School reopens on Monday after the holidays, please send the fee receipt with your child",
    "Just checking in, how are you feeling today, call me when free",
    "Your train PNR is confirmed, seat number 34, coach S5, departure at 6 AM",
    "Naya mobile recharge plan 199 mein 2GB per day mila hai, official website par dekh lo",
    "Aaj shaam ganv se return honge, station pe le lena mujhe",
    "Your salary slip for this month has been generated, download from the HR portal",
    "Diwali ki shubhkamnayein, family ke sath accha time bitao",
    "Please review the attached document and share feedback by Friday",
]

RISK_KEYWORDS = {
    "urgency": ["urgent", "immediately", "turant", "abhi", "last warning", "24 hours", "1 hour",
                "2 hours", "10 minutes", "right now", "within", "expire", "today", "warna"],
    "otp_bank": ["otp", "cvv", "pin", "kyc", "aadhaar", "upi pin", "account number", "bank",
                 "atm card", "credit card", "debit card"],
    "money_bait": ["lottery", "won", "prize", "free", "double your money", "gift", "cashback",
                   "gold coin", "jeet gaye", "processing fee", "registration fee", "advance fee"],
    "threat": ["blocked", "suspended", "freeze", "closed", "band ho jayega", "block ho jayega",
               "deleted", "cut", "stop"],
    "action_link": ["click", "link", "call this number", "share", "bhejein", "batayein", "dein"],
}


@st.cache_resource
def train_scam_classifier():
    texts = SCAM_SAMPLES + LEGIT_SAMPLES
    labels = [1] * len(SCAM_SAMPLES) + [0] * len(LEGIT_SAMPLES)
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)
    X = vectorizer.fit_transform(texts)
    model = MultinomialNB()
    model.fit(X, labels)
    return vectorizer, model


def explain_signals(message):
    """Plain-language signal explanation — this is what teaches the user,
    not just a black-box score."""
    msg_lower = message.lower()
    found = {}
    for category, keywords in RISK_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in msg_lower]
        if hits:
            found[category] = hits

    unregistered_pattern = bool(re.search(r"\b(this number|unknown number|call this)\b", msg_lower))
    return found, unregistered_pattern


CATEGORY_LABELS = {
    "urgency": "⏱️ Urgency pressure (rushing you to act fast)",
    "otp_bank": "🔑 Asking for OTP / bank / KYC details",
    "money_bait": "🎁 Too-good-to-be-true money offer",
    "threat": "⚠️ Threat of account being blocked/closed",
    "action_link": "🔗 Pushing you to click a link or share info",
}


# =========================================================
# STEP 5: PAGE — Home
# =========================================================
if page == "🏠 Home":
    st.title("🛡️ TrustNet")
    st.subheader("AI-Powered Financial Safety & Literacy Companion")
    st.write(
        "Financially vulnerable users — gig workers, daily-wage earners, elderly citizens, "
        "first-time smartphone users — face two problems at once: they're prime targets for "
        "scams, and they lack financial tools built for irregular income. TrustNet solves both "
        "in one place."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🚨 Scam Shield")
        st.write(
            "Paste any SMS or call transcript. TrustNet flags it as risky or safe, and "
            "**explains why** — urgency language, OTP/bank requests, fake prizes, threats — "
            "so users learn to spot scams themselves over time."
        )
    with col2:
        st.markdown("### 💰 Money Coach")
        st.write(
            "Log daily/weekly income and expenses even if they're irregular. Get a realistic "
            "micro-savings goal, and ask questions like 'what is EMI?' in plain Hindi/English/"
            "Hinglish — no jargon."
        )

    st.info("Use the sidebar to switch between modules. Scam Shield needs no API key at all.")

# =========================================================
# STEP 6: PAGE — Scam Shield
# =========================================================
elif page == "🚨 Scam Shield":
    st.title("🚨 Scam Shield")
    st.caption("Real-time, explainable scam SMS/call detection — works fully offline, no API key needed.")

    vectorizer, model = train_scam_classifier()

    message = st.text_area(
        "Paste the SMS or call transcript here (Hindi / English / Hinglish all work):",
        height=120,
        placeholder="e.g. Aapka KYC turant update karein warna account block ho jayega, link par click karein",
    )

    if st.button("🔍 Check this message", type="primary"):
        if not message.strip():
            st.warning("Please paste a message first.")
        else:
            X_input = vectorizer.transform([message])
            proba = model.predict_proba(X_input)[0]
            scam_score = proba[1] * 100

            signals, unregistered = explain_signals(message)

            st.markdown("---")
            if scam_score >= 60:
                st.error(f"### ⚠️ HIGH RISK — {scam_score:.0f}% likely a scam")
            elif scam_score >= 30:
                st.warning(f"### 🟡 BE CAREFUL — {scam_score:.0f}% risk score")
            else:
                st.success(f"### ✅ LOOKS SAFE — {scam_score:.0f}% risk score")

            st.progress(min(int(scam_score), 100))

            st.markdown("#### Why this score? (plain-language explanation)")
            if signals:
                for category, hits in signals.items():
                    st.write(f"- {CATEGORY_LABELS[category]} — found: *{', '.join(hits)}*")
            else:
                st.write("- No major scam signals found in this message.")

            if unregistered:
                st.write("- 📵 Message tells you to call an unfamiliar number directly.")

            st.markdown("#### 🎓 Learn from this")
            if scam_score >= 60:
                st.write(
                    "Real banks and government services **never** ask for your OTP, CVV, or PIN "
                    "over SMS or call. If you're unsure, hang up and call the number printed on "
                    "your bank card or passbook — never a number given in the message."
                )
            else:
                st.write(
                    "This message doesn't show strong scam patterns, but always stay cautious "
                    "with any message asking for money or personal details."
                )

    with st.expander("ℹ️ How does this work?"):
        st.write(
            "A small ML classifier (TF-IDF + Naive Bayes) trained on labeled scam vs. genuine "
            "messages scores the text, while a keyword-signal layer explains *why* — urgency "
            "words, OTP/bank/KYC references, fake prize offers, and threat language. Both English "
            "and Hindi/Hinglish keywords are covered."
        )

# =========================================================
# STEP 7: PAGE — Money Coach
# =========================================================
elif page == "💰 Money Coach":
    st.title("💰 Money Coach")
    st.caption("Built for irregular income — gig work, daily wages, seasonal earnings.")

    if "entries" not in st.session_state:
        st.session_state.entries = []

    tab1, tab2 = st.tabs(["📒 Track Income & Expenses", "💬 Ask Money Coach"])

    # ---- Tab 1: tracker ----
    with tab1:
        st.markdown("#### Add today's entry")
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        with c1:
            entry_date = st.date_input("Date", value=date.today())
        with c2:
            entry_type = st.selectbox("Type", ["Income", "Expense"])
        with c3:
            amount = st.number_input("Amount (₹)", min_value=0, step=10)
        with c4:
            note = st.text_input("Note", placeholder="e.g. auto fare / daily wage")

        if st.button("➕ Add entry"):
            st.session_state.entries.append(
                {"date": str(entry_date), "type": entry_type, "amount": amount, "note": note}
            )
            st.success("Entry added.")

        if st.session_state.entries:
            df = pd.DataFrame(st.session_state.entries)
            st.dataframe(df, use_container_width=True)

            total_income = df.loc[df["type"] == "Income", "amount"].sum()
            total_expense = df.loc[df["type"] == "Expense", "amount"].sum()
            balance = total_income - total_expense

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Income", f"₹{total_income:.0f}")
            m2.metric("Total Expense", f"₹{total_expense:.0f}")
            m3.metric("Balance", f"₹{balance:.0f}")

            income_days = max(df.loc[df["type"] == "Income", "date"].nunique(), 1)
            avg_daily_income = total_income / income_days
            suggested_saving = round(avg_daily_income * 0.10, -1)  # ~10%, rounded to nearest 10

            st.markdown("#### 🎯 Suggested micro-savings goal")
            st.write(
                f"Based on your average daily income of about ₹{avg_daily_income:.0f}, try saving "
                f"**₹{suggested_saving:.0f} per earning day**. That's small enough to not hurt your "
                f"daily needs, but it adds up over time."
            )

            st.bar_chart(df.groupby("type")["amount"].sum())
        else:
            st.info("No entries yet. Add your first income or expense above.")

    # ---- Tab 2: chat ----
    with tab2:
        st.markdown("Ask anything — *'What is EMI?'*, *'Should I take a loan for a new phone?'*, "
                     "*'Credit score kya hota hai?'*")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for role, text in st.session_state.chat_history:
            with st.chat_message(role):
                st.write(text)

        user_q = st.chat_input("Type your question in Hindi, English, or Hinglish...")

        if user_q:
            if not api_key:
                st.warning("Please enter your Gemini API key in the sidebar to chat with Money Coach.")
            else:
                st.session_state.chat_history.append(("user", user_q))
                with st.chat_message("user"):
                    st.write(user_q)

                # Give the model context of the user's own tracked finances if available
                money_context = ""
                if st.session_state.entries:
                    df = pd.DataFrame(st.session_state.entries)
                    money_context = (
                        f"User's tracked totals — Income: ₹{df.loc[df['type']=='Income','amount'].sum():.0f}, "
                        f"Expense: ₹{df.loc[df['type']=='Expense','amount'].sum():.0f}."
                    )

                prompt = f"""You are Money Coach, part of TrustNet — a financial literacy assistant
for gig workers, daily-wage earners, elderly users, and first-time smartphone users in India.

Rules:
- Reply in the SAME language style the user used (Hindi / English / Hinglish).
- NO financial jargon. If a term like EMI, credit score, interest is needed, explain it simply
  with a real-life example (auto driver, vegetable seller, daily wage worker).
- Keep answers short (3-5 sentences), warm, and practical.
- If relevant, gently mention a related scam-safety tip (e.g. never share OTP for a "loan").

{money_context}

User's question: {user_q}

Respond ONLY in plain text (no JSON, no markdown headers)."""

                try:
                    llm = get_llm()
                    response = llm.invoke(prompt)
                    reply_text = response.content.strip()
                except Exception as e:
                    reply_text = f"Sorry, I couldn't reach the AI service right now. ({e})"

                st.session_state.chat_history.append(("assistant", reply_text))
                with st.chat_message("assistant"):
                    st.write(reply_text)
