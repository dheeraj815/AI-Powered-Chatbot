import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
from chatbot_engine import get_response, KNOWLEDGE_BASE
from database import (
    init_db, log_message, fetch_all_logs,
    fetch_intent_stats, fetch_total_stats, clear_all_logs
)

# ──────────────────────────────────────────────
#  PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="SupportBot AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
#  CUSTOM CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

/* ── Root Variables ─────────────────────── */
:root {
    --bg:         #0d0f1a;
    --surface:    #13172a;
    --surface2:   #1a1f35;
    --accent:     #4f8cff;
    --accent2:    #a78bfa;
    --green:      #34d399;
    --orange:     #fb923c;
    --text:       #e2e8f0;
    --muted:      #64748b;
    --border:     rgba(79,140,255,0.15);
    --glow:       0 0 24px rgba(79,140,255,0.25);
    --radius:     16px;
}

/* ── Global ─────────────────────────────── */
html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Sidebar ─────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif !important; }

/* ── Header ─────────────────────────────── */
.hero-header {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
    background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
    border-radius: var(--radius);
    border: 1px solid var(--border);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at center, rgba(79,140,255,0.08) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4f8cff 0%, #a78bfa 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.5px;
}
.hero-sub {
    color: var(--muted) !important;
    font-size: 0.95rem;
    margin-top: 0.3rem;
}
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: var(--green);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--green);
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── Chat Messages ───────────────────────── */
.chat-user {
    display: flex;
    justify-content: flex-end;
    margin: 0.5rem 0;
}
.chat-user .bubble {
    background: linear-gradient(135deg, var(--accent), #6d9fff);
    color: #fff !important;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 72%;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 4px 15px rgba(79,140,255,0.3);
}
.chat-bot {
    display: flex;
    justify-content: flex-start;
    margin: 0.5rem 0;
}
.chat-bot .bubble {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text) !important;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 72%;
    font-size: 0.95rem;
    line-height: 1.6;
}
.avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
    margin: 0 8px;
}
.avatar-bot { background: linear-gradient(135deg, var(--accent), var(--accent2)); }
.avatar-user { background: linear-gradient(135deg, var(--green), #22c55e); order: 2; }

/* ── Intent Badge ───────────────────────── */
.badge {
    display: inline-block;
    font-size: 0.68rem;
    padding: 2px 8px;
    border-radius: 20px;
    font-weight: 600;
    margin-top: 4px;
    letter-spacing: 0.5px;
}
.badge-high   { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.badge-medium { background: rgba(251,146,60,0.15); color: #fb923c; border: 1px solid rgba(251,146,60,0.3); }
.badge-low    { background: rgba(248,113,113,0.15); color: #f87171; border: 1px solid rgba(248,113,113,0.3); }

/* ── Metric Cards ───────────────────────── */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem;
    text-align: center;
}
.metric-val {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--accent);
}
.metric-label { font-size: 0.8rem; color: var(--muted); margin-top: 4px; }

/* ── Input ───────────────────────────────── */
[data-testid="stChatInput"] textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: var(--glow) !important;
}

/* ── Buttons ─────────────────────────────── */
.stButton button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
}

/* ── Tabs ─────────────────────────────────*/
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600;
}

/* ── Table ───────────────────────────────── */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ── Scrollbar ───────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* ── Divider ─────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
#  INIT
# ──────────────────────────────────────────────
init_db()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_badges" not in st.session_state:
    st.session_state.show_badges = True

# ──────────────────────────────────────────────
#  SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
        <div style='font-family:Syne,sans-serif; font-size:1.4rem; font-weight:800;
                    background: linear-gradient(135deg,#4f8cff,#a78bfa);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
            🤖 SupportBot
        </div>
        <div style='color:#64748b; font-size:0.8rem;'>NLP-Powered Assistant</div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    st.markdown("**⚙️ Settings**")
    st.session_state.show_badges = st.toggle(
        "Show Intent Badges", value=st.session_state.show_badges)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(f"""
    **🔑 Session**
    <br><code style='color:#4f8cff; background: rgba(79,140,255,0.1);
    padding:2px 8px; border-radius:4px;'>#{st.session_state.session_id}</code>
    """, unsafe_allow_html=True)
    st.caption(f"Messages this session: **{len(st.session_state.messages)}**")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**💡 Quick Topics**")
    topics = {
        "💰 Pricing": "What are your pricing plans?",
        "📦 Shipping": "How long does delivery take?",
        "🔐 Password": "I forgot my password",
        "📞 Contact": "How can I reach support?",
        "💸 Refund": "I want a refund",
        "🐛 Bug Report": "Something is not working",
    }
    for label, prompt in topics.items():
        if st.button(label, use_container_width=True, key=f"quick_{label}"):
            st.session_state["prefill"] = prompt
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.rerun()

# ──────────────────────────────────────────────
#  MAIN LAYOUT — Tabs
# ──────────────────────────────────────────────
tab_chat, tab_dashboard, tab_logs = st.tabs(
    ["💬 Chat", "📊 Analytics", "📋 Logs"])

# ════════════════════════════════════════════════
#  TAB 1 — CHAT
# ════════════════════════════════════════════════
with tab_chat:
    # Hero header
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">🤖 SupportBot AI</div>
        <div class="hero-sub">
            <span class="status-dot"></span>Online · NLTK-Powered · Customer Support Assistant
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-bot" style="margin-bottom:1rem;">
            <div class="avatar avatar-bot">🤖</div>
            <div>
                <div class="bubble">
                    👋 Hello! I'm <strong>SupportBot</strong>, your AI customer support assistant!<br><br>
                    I can help you with <strong>pricing, shipping, refunds, passwords, bug reports</strong>, and more.<br><br>
                    Type <strong>help</strong> to see all topics, or just ask away! 😊
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Render message history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-user">
                <div class="bubble">{msg["content"]}</div>
                <div class="avatar avatar-user">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            badge_html = ""
            if st.session_state.show_badges and msg.get("intent"):
                conf = msg.get("confidence", "low")
                badge_cls = f"badge-{conf}"
                badge_html = f'<br><span class="badge {badge_cls}">🎯 {msg["intent"]} · {conf}</span>'
            st.markdown(f"""
            <div class="chat-bot">
                <div class="avatar avatar-bot">🤖</div>
                <div>
                    <div class="bubble">{msg["content"]}{badge_html}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Chat Input ──
    prefill_val = st.session_state.pop("prefill", "")
    user_input = st.chat_input("Type your message here...", key="chat_input")

    if prefill_val:
        user_input = prefill_val

    if user_input:
        # Save & display user message
        st.session_state.messages.append(
            {"role": "user", "content": user_input})
        log_message(st.session_state.session_id, "user", user_input)

        # Get bot response
        result = get_response(user_input)
        response_text = result["response"]
        intent = result["intent"]
        confidence = result["confidence"]

        # Save & log bot response
        st.session_state.messages.append({
            "role": "bot",
            "content": response_text,
            "intent": intent,
            "confidence": confidence,
        })
        log_message(
            st.session_state.session_id, "bot",
            response_text, intent, confidence
        )
        st.rerun()

# ════════════════════════════════════════════════
#  TAB 2 — ANALYTICS DASHBOARD
# ════════════════════════════════════════════════
with tab_dashboard:
    st.markdown("""
    <div style='font-family:Syne,sans-serif; font-size:1.5rem; font-weight:800;
                margin-bottom:1rem; color:#e2e8f0;'>
        📊 Analytics Dashboard
    </div>
    """, unsafe_allow_html=True)

    stats = fetch_total_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{stats['total_messages']}</div>
            <div class="metric-label">Total Messages</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color:#a78bfa;">{stats['total_sessions']}</div>
            <div class="metric-label">Total Sessions</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color:#34d399;">{stats['user_messages']}</div>
            <div class="metric-label">User Messages</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color:#fb923c;">{stats['bot_messages']}</div>
            <div class="metric-label">Bot Responses</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Intent Distribution Chart
    intent_data = fetch_intent_stats()
    if intent_data:
        st.markdown("**🎯 Intent Distribution**")
        df_intent = pd.DataFrame(intent_data)
        df_intent.columns = ["Intent", "Count"]
        st.bar_chart(df_intent.set_index("Intent"),
                     color="#4f8cff", use_container_width=True)
    else:
        st.info("💡 Start chatting to see analytics here!")

    # Knowledge base coverage
    st.markdown("**📚 Knowledge Base Coverage**")
    kb_data = []
    for intent, data in KNOWLEDGE_BASE.items():
        kb_data.append({
            "Intent": intent.title(),
            "Patterns": len(data["patterns"]),
            "Responses": len(data["responses"]),
        })
    df_kb = pd.DataFrame(kb_data)
    st.dataframe(df_kb, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════
#  TAB 3 — LOGS
# ════════════════════════════════════════════════
with tab_logs:
    st.markdown("""
    <div style='font-family:Syne,sans-serif; font-size:1.5rem; font-weight:800;
                margin-bottom:1rem; color:#e2e8f0;'>
        📋 Interaction Logs
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("All user interactions are logged to SQLite for analysis.")
    with col2:
        if st.button("🗑️ Clear All Logs", type="secondary"):
            clear_all_logs()
            st.success("Logs cleared!")
            st.rerun()

    logs = fetch_all_logs()
    if logs:
        df_logs = pd.DataFrame(logs)
        df_logs = df_logs[["timestamp", "session_id",
                           "role", "message", "intent", "confidence"]]
        df_logs.columns = ["Timestamp", "Session",
                           "Role", "Message", "Intent", "Confidence"]

        # Color role column
        def highlight_role(val):
            if val == "user":
                return "background-color: rgba(79,140,255,0.1); color: #4f8cff"
            return "background-color: rgba(167,139,250,0.1); color: #a78bfa"

        st.dataframe(
            df_logs.style.applymap(highlight_role, subset=["Role"]),
            use_container_width=True,
            height=450,
            hide_index=True,
        )

        # Download
        csv = df_logs.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Logs as CSV",
            data=csv,
            file_name=f"chat_logs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
    else:
        st.info("💡 No logs yet. Start chatting to generate logs!")

# ──────────────────────────────────────────────
#  Footer
# ──────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; margin-top:3rem; color:#334155; font-size:0.78rem;'>
    Built with 🐍 Python · NLTK · Streamlit · SQLite &nbsp;|&nbsp; SupportBot v1.0
</div>
""", unsafe_allow_html=True)
