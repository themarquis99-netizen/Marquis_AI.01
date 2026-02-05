import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
# Initialisation de l'historique s'il n'existe pas
if "history" not in st.session_state:
    st.session_state.history = []

def add_to_history(user_msg, ai_msg):
    st.session_state.history.append({"user": user_msg, "ai": ai_msg})
# Configuration de la page
st.set_page_config(page_title="Marquis AI - My English Coach", page_icon="🇬🇧")

# Design CSS pour coller à ton screenshot
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stButton>button { border-radius: 50px; background-color: #2ECC71; color: white; }
    .user-box { background-color: white; border-radius: 15px; padding: 15px; border-left: 5px solid #3498DB; margin-bottom: 10px; }
    .ai-box { background-color: #E8F6F3; border-radius: 15px; padding: 15px; border-left: 5px solid #2ECC71; }
    </style>
    """, unsafe_allow_html=True)

st.title("Marquis AI 🎙️")
st.subheader("My English Coach")

# Initialisation Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Barre latérale pour les réglages (comme sur ton design)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/197/197374.png", width=100) # Drapeau UK
    accent = st.selectbox("Accent", ["British (Liam)", "American (Aria)"])
    level = st.selectbox("Level", ["A2 - Beginner", "B1 - Intermediate", "B2 - Upper Intermediate"])

# Zone d'enregistrement
st.write("### Tap to Speak & Practice")
audio = mic_recorder(start_prompt="Click to Record", stop_prompt="Stop", key="recorder")

if audio:
    audio_bio = io.BytesIO(audio['bytes'])
    audio_bio.name = "audio.wav"
    
    # 1. Transcription (Whisper sur Groq)
    transcript = client.audio.transcriptions.create(
        file=audio_bio,
        model="whisper-large-v3",
        response_format="text"
    )
    
    # ... après la génération de la réponse de l'IA ...
add_to_history(transcript, response_text)

# Affichage de la conversation actuelle
st.markdown(f'<div class="user-box"><b>You:</b> {transcript}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="ai-box"><b>Marquis AI:</b> {response_text}</div>', unsafe_allow_html=True)

# Section Historique en bas de page
with st.expander("📜 View Conversation History"):
    for chat in reversed(st.session_state.history[:-1]): # Affiche les anciens messages
        st.write(f"**You:** {chat['user']}")
        st.write(f"**Marquis:** {chat['ai']}")
        st.divider()

    # 2. IA Conversationnelle (Llama 3 sur Groq)
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": f"You are Liam, a friendly English coach. Level: {level}. Correct mistakes politely at the end."},
            {"role": "user", "content": transcript}
        ]
    )
    
    response_text = chat_completion.choices[0].message.content
    st.markdown(f'<div class="ai-box"><b>Marquis AI (Liam):</b><br>{response_text}</div>', unsafe_allow_html=True)

    # 3. Voix (gTTS)
    tld = 'co.uk' if "British" in accent else 'com'
    tts = gTTS(text=response_text, lang='en', tld=tld)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp)
