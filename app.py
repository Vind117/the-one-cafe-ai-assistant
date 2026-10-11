import os
import streamlit as st
from google import genai

# Page Config
st.set_page_config(
    page_title="Siti - THE ONE Cafe Assistant",
    page_icon="☕",
    layout="centered"
)

# Custom Styling (WhatsApp-inspired clean theme)
st.markdown("""
    <style>
    .stApp {
        background-color: #efeae2;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
    }
    .tool-badge {
        background-color: #e1f5fe;
        border-left: 4px solid #0288d1;
        padding: 8px 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.85rem;
        color: #01579b;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("☕ THE ONE Cafe — AI Customer Assistant")
st.caption("Powered by Gemini 3.8 Flash • Automatic Function Calling • Online")

# Gemini Client Initialization (Securely load from environment variables)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# =====================================================================
# 🛠️ BACKEND TOOLS / FUNCTION DEFINITIONS
# =====================================================================

def check_table_availability(date: str, time: str, party_size: int) -> str:
    """
    Checks table availability at THE ONE Cafe for reservations.
    Args:
        date: Reservation date (e.g., 'tomorrow', '2026-10-12').
        time: Requested time (e.g., '1:00 PM', '13:00').
        party_size: Number of guests.
    """
    if party_size > 12:
        return f"FULL: Tables for {party_size} require special booking via phone."
    return f"AVAILABLE: Table for {party_size} guests on {date} at {time} is open for reservation at THE ONE Cafe."

def calculate_delivery_fee(distance_km: float) -> str:
    """
    Calculates delivery fee based on distance from THE ONE Cafe.
    Args:
        distance_km: Distance in kilometers from THE ONE Cafe.
    """
    if distance_km > 10:
        return "OUT_OF_RANGE: THE ONE Cafe only delivers within a 10km radius."
    elif distance_km <= 3:
        return "FEE: RM 3.00 (Standard Local Delivery)"
    else:
        fee = 3.00 + ((distance_km - 3) * 1.00)
        return f"FEE: RM {fee:.2f} (Calculated for {distance_km}km distance)"

# =====================================================================
# 📋 SYSTEM INSTRUCTION
# =====================================================================

SYSTEM_INSTRUCTION = """
You are 'Siti', a friendly customer support and order assistant for 'THE ONE Cafe' in Malaysia.

KEY INFORMATION ABOUT THE ONE Cafe:
- Business: Premium artisan lifestyle cafe serving signature specialty coffee, fusion brunch, gourmet pastries, and premium lunch sets.
- Operating Hours: Tuesday to Sunday, 9:00 AM – 11:00 PM (Closed on Mondays).
- Popular Menu Items: The One Signature Latte, Truffle Fries, Smoked Salmon Croissant, Nasi Lemak Royale, Matcha Lava Cake.
- Services: Dine-in, takeaways, and local delivery within 10km.
- Reservations: Accepted for tables of 4 or more.

TOOL USAGE INSTRUCTIONS:
- Whenever a user asks for table booking or reservations, USE the `check_table_availability` tool to verify.
- Whenever a user asks about delivery costs or provides a distance/location, USE the `calculate_delivery_fee` tool.

TONE AND COMMUNICATION STYLE:
- Speak in a warm, welcoming Malaysian conversational style (mixture of English, Bahasa Melayu, and Manglish).
- Understand local terms like 'boss', 'lah', 'makan', 'bungkus', 'kopi', 'meja', 'pukul berapa'.
- Use polite honorifics like 'Encik', 'Puan', 'Boss', or 'Kak/Abg' naturally.
- Keep replies concise with helpful emojis.
"""

# Initialize a persistent chat session with automatic function calling enabled
if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-3.8-flash",
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.7,
            "tools": [check_table_availability, calculate_delivery_fee]
        }
    )

# Session State for UI Message History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hai boss! 👋 Welcome to THE ONE Cafe! Apa Siti boleh bantu hari ni?"}
    ]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Handler
if prompt := st.chat_input("Ketik mesej di sini..."):
    # Render user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process AI Response using the chat session (handles AFC automatically)
    with st.chat_message("assistant"):
        with st.spinner("Siti sedang menaip..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                bot_reply = response.text
            except Exception as e:
                bot_reply = f"Maaf boss, Siti error sikit: {e}"

            st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})