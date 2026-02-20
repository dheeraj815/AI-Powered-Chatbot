import nltk
import string
import random
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data


def download_nltk_data():
    packages = ['punkt', 'stopwords', 'wordnet',
                'averaged_perceptron_tagger', 'punkt_tab']
    for pkg in packages:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass


download_nltk_data()

lemmatizer = WordNetLemmatizer()

# ─────────────────────────────────────────────
#  KNOWLEDGE BASE  — FAQ / Customer Support
# ─────────────────────────────────────────────
KNOWLEDGE_BASE = {
    "greetings": {
        "patterns": ["hello", "hi", "hey", "good morning", "good afternoon",
                     "good evening", "howdy", "greetings", "sup", "what's up"],
        "responses": [
            "Hey there! 👋 How can I help you today?",
            "Hello! Welcome! What can I do for you?",
            "Hi! Great to see you. What brings you here today?",
        ]
    },
    "farewell": {
        "patterns": ["bye", "goodbye", "see you", "take care", "later",
                     "quit", "exit", "cya", "farewell", "see ya"],
        "responses": [
            "Goodbye! Have a wonderful day! 😊",
            "Take care! Don't hesitate to come back if you need help.",
            "See you later! Hope I was helpful!",
        ]
    },
    "thanks": {
        "patterns": ["thank", "thanks", "thank you", "appreciate", "helpful",
                     "great help", "awesome", "perfect", "wonderful"],
        "responses": [
            "You're welcome! 😊 Anything else I can help with?",
            "Happy to help! Let me know if you need anything else.",
            "Glad I could assist! Is there anything more you need?",
        ]
    },
    "hours": {
        "patterns": ["hours", "open", "opening", "closing", "when", "time",
                     "schedule", "available", "working hours", "business hours"],
        "responses": [
            "🕐 We're available **24/7** through this chat! For phone support, our hours are **Mon–Fri, 9 AM – 6 PM IST**.",
            "Our support team works **Monday to Friday, 9:00 AM – 6:00 PM IST**. But I'm here around the clock! 🌙",
        ]
    },
    "pricing": {
        "patterns": ["price", "pricing", "cost", "how much", "fee", "charge",
                     "plan", "subscription", "payment", "pay", "rate", "affordable"],
        "responses": [
            "💰 We offer three plans:\n\n• **Starter** — ₹999/mo (1 user)\n• **Pro** — ₹2,499/mo (5 users)\n• **Enterprise** — Custom pricing\n\nAll plans include a **14-day free trial**!",
            "Our pricing starts at just ₹999/month. Visit our pricing page or type 'plans' for a full breakdown!",
        ]
    },
    "refund": {
        "patterns": ["refund", "money back", "cancel", "cancellation", "return",
                     "dispute", "chargeback", "reimbursement"],
        "responses": [
            "💸 We offer a **30-day money-back guarantee** — no questions asked. To initiate a refund, email us at **refunds@support.com** or raise a ticket.",
            "Our refund policy: full refund within 30 days of purchase. Just contact our billing team at **billing@support.com**.",
        ]
    },
    "shipping": {
        "patterns": ["shipping", "delivery", "ship", "track", "order", "dispatch",
                     "arrive", "expected", "courier", "package", "parcel"],
        "responses": [
            "📦 Standard delivery: **3–5 business days**. Express: **1–2 days** (extra charge). You can track your order with the tracking ID sent to your email!",
            "Shipping timelines:\n• Standard — 3–5 days\n• Express — 1–2 days\n• International — 7–14 days\n\nNeed help tracking? Share your order ID!",
        ]
    },
    "password": {
        "patterns": ["password", "forgot", "reset", "login", "sign in",
                     "account access", "locked out", "otp", "credentials"],
        "responses": [
            "🔐 To reset your password:\n1. Click **'Forgot Password'** on the login page\n2. Enter your registered email\n3. Check your inbox for a reset link\n\nDidn't receive the email? Check your spam folder!",
            "Password reset is easy! Go to **Settings → Security → Reset Password**, or use the 'Forgot Password' link on the login screen.",
        ]
    },
    "contact": {
        "patterns": ["contact", "reach", "email", "phone", "call", "support",
                     "human", "agent", "representative", "talk to someone"],
        "responses": [
            "📞 You can reach us at:\n\n• **Email:** support@company.com\n• **Phone:** +91-800-123-4567\n• **Live Chat:** Available Mon–Fri, 9 AM–6 PM IST\n\nWant me to raise a support ticket for you?",
            "Need to talk to a human? No problem! Call **+91-800-123-4567** or email **support@company.com**. Average response time is under 2 hours!",
        ]
    },
    "features": {
        "patterns": ["feature", "what can", "capability", "do you offer",
                     "functionality", "option", "service", "product"],
        "responses": [
            "🚀 Here's what we offer:\n\n• ✅ Real-time analytics\n• ✅ Automated reports\n• ✅ Team collaboration tools\n• ✅ API integrations\n• ✅ 24/7 AI chat support\n\nWant details on any specific feature?",
            "Our platform includes analytics, reporting, collaboration, integrations, and much more! Which feature are you most interested in?",
        ]
    },
    "bug": {
        "patterns": ["bug", "error", "broken", "not working", "issue", "problem",
                     "crash", "glitch", "fail", "stuck", "slow", "down"],
        "responses": [
            "😟 Sorry to hear that! Let's fix it:\n\n1. Try **refreshing** the page\n2. **Clear cache** and cookies\n3. Try a **different browser**\n\nIf the issue persists, please describe the error and I'll escalate it to our tech team!",
            "That sounds frustrating! Please share:\n• What were you doing when it happened?\n• Any error message?\n• Your browser/device?\n\nThis helps us resolve it faster! 🔧",
        ]
    },
    "about": {
        "patterns": ["who are you", "what are you", "about you", "your name",
                     "introduce", "tell me about", "who made you", "ai bot"],
        "responses": [
            "🤖 I'm **SupportBot**, your AI-powered customer support assistant! I'm built with Python & NLTK to help with FAQs, troubleshooting, and general queries. How can I help you today?",
            "Hi, I'm **SupportBot**! I'm here to answer your questions about our products, pricing, shipping, and more. Ask me anything! 😊",
        ]
    },
}

# ─────────────────────────────────────────────
#  FALLBACK RESPONSES
# ─────────────────────────────────────────────
FALLBACK_RESPONSES = [
    "Hmm, I'm not sure I understood that. Could you rephrase? 🤔",
    "I don't have an answer for that yet. Try asking about **pricing, shipping, refunds, hours, or bugs**!",
    "That's outside my expertise! You can reach a human agent at **support@company.com** for complex queries.",
    "I'm still learning! 🧠 Could you ask that differently, or type **'help'** to see what I can assist with.",
]

HELP_TEXT = """
🆘 **Here's what I can help you with:**

| Topic | Example Question |
|-------|-----------------|
| 🕐 Hours | "What are your working hours?" |
| 💰 Pricing | "How much does it cost?" |
| 💸 Refunds | "How do I get a refund?" |
| 📦 Shipping | "When will my order arrive?" |
| 🔐 Password | "I forgot my password" |
| 📞 Contact | "How do I reach support?" |
| 🚀 Features | "What features do you offer?" |
| 🐛 Bug | "Something is not working" |
| 🤖 About | "Who are you?" |
"""


def preprocess(text: str) -> list[str]:
    """Tokenize, lowercase, remove punctuation & stopwords, then lemmatize."""
    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(text.lower())
    tokens = [
        lemmatizer.lemmatize(t)
        for t in tokens
        if t not in string.punctuation and t not in stop_words
    ]
    return tokens


def match_intent(user_tokens: list[str]) -> str | None:
    """Return the best-matching intent key, or None."""
    best_intent = None
    best_score = 0

    for intent, data in KNOWLEDGE_BASE.items():
        score = 0
        for pattern in data["patterns"]:
            pattern_tokens = preprocess(pattern)
            for pt in pattern_tokens:
                if pt in user_tokens:
                    score += 1
        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent if best_score > 0 else None


def get_response(user_message: str) -> dict:
    """
    Returns a dict:
        { "response": str, "intent": str, "confidence": str }
    """
    stripped = user_message.strip().lower()

    # Help shortcut
    if stripped in ("help", "?", "menu", "commands"):
        return {"response": HELP_TEXT, "intent": "help", "confidence": "high"}

    tokens = preprocess(user_message)

    if not tokens:
        return {
            "response": "Please type a message so I can help you! 😊",
            "intent": "empty",
            "confidence": "n/a",
        }

    intent = match_intent(tokens)

    if intent:
        response = random.choice(KNOWLEDGE_BASE[intent]["responses"])
        confidence = "high" if len(tokens) >= 2 else "medium"
    else:
        response = random.choice(FALLBACK_RESPONSES)
        intent = "unknown"
        confidence = "low"

    return {"response": response, "intent": intent, "confidence": confidence}
