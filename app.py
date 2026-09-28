import streamlit as st

from chatbot import chatbot_response


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Healthcare Research Assistant",
    page_icon="🏥",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .disclaimer {
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🏥 Healthcare Research & Wellness Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Research health information using public healthcare APIs</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Settings")

    st.write(
        "Enter your USDA FoodData Central API key."
    )

    api_key = st.text_input(
        "USDA API Key",
        value="DEMO_KEY",
        type="password"
    )

    st.divider()

    st.header("💡 Example Questions")

    st.write(
        "🦠 Show COVID-19 statistics for India."
    )

    st.write(
        "🥗 How much protein is in chickpeas?"
    )

    st.write(
        "💊 Search medicine paracetamol."
    )

    st.write(
        "📊 Compare rice and oats."
    )


# ============================================================
# CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask a healthcare research question..."
)


# ============================================================
# PROCESS USER QUESTION
# ============================================================

if user_input:

    # Display user message

    with st.chat_message("user"):

        st.markdown(user_input)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )


    # Generate chatbot response

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching healthcare data..."
        ):

            response = chatbot_response(
                user_input,
                api_key
            )

        st.markdown(response)


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="disclaimer">

    ⚠️ <b>Healthcare Disclaimer</b><br><br>

    This chatbot provides general educational and research
    information only. It does not diagnose medical conditions,
    prescribe medicines, or replace advice from a qualified
    healthcare professional.

    </div>
    """,
    unsafe_allow_html=True
)