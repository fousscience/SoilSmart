# frontend/streamlit_app.py
from dotenv import load_dotenv
import os

load_dotenv()  # ✅ Charge les variables du fichier .env
API_URL = os.getenv("API_URL", "http://localhost:8000")  # ✅ Valeur par défaut en local

import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="SoilSmart par MaliAgriculture",
    page_icon="🌱",
    layout="wide"
)

# --- Custom CSS for better UI ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* --- General --- */
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}
.main {
    background-color: #F9F9F6;
    color: #333333;
}

/* --- Sidebar (Desktop) --- */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 0.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

/* --- Header Zone for Mobile --- */
.mobile-header {
    display: none;
    text-align: center;
    background-color: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    padding: 1rem 0.5rem;
    margin-bottom: 1rem;
}

.mobile-header img {
    width: 80px;
}
.mobile-header h1 {
    color: #4CAF50;
    font-size: 1.4rem;
    margin-bottom: 0.25rem;
}

/* --- Buttons --- */
.stButton>button {
    border-radius: 10px;
    border: 2px solid #4CAF50;
    background-color: #4CAF50;
    color: white;
    padding: 12px 28px;
    transition: all 0.3s ease;
    font-weight: 600;
    font-size: 1rem;
    width: 100%;
    box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
}
.stButton>button:hover {
    background-color: #FFFFFF;
    color: #4CAF50;
    border-color: #4CAF50;
    transform: translateY(-2px);
}

/* --- Cards --- */
.report-card, .language-section {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
}

/* --- Mobile Responsive --- */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { display: none; } /* Cache la sidebar */
    .mobile-header { display: block; } /* Montre l’en-tête mobile */
    .main { padding: 0.5rem; }
    .stButton>button {
        font-size: 0.9rem;
        padding: 10px 18px;
    }
}
/* --- Responsive Sidebar Text & Buttons --- */
@media (max-width: 600px) {
    [data-testid="stSidebar"] h3 {
        font-size: 1.2rem !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label {
        font-size: 0.85rem !important;
    }
    [data-testid="stSidebar"] .stButton>button {
        font-size: 0.9rem !important;
        padding: 10px 16px !important;
    }
    [data-testid="stFileUploader"] {
        padding: 0.8rem !important;
    }
}

</style>
""", unsafe_allow_html=True)


# --- Sidebar --- #
# --- Sidebar améliorée --- #
with st.sidebar:
    
    st.markdown("<h1 style='text-align: left; color: #4CAF50; font-weight: 700; margin-bottom: 2rem;'>🌱 SoilSmart-AI</h1>", unsafe_allow_html=True)
    st.markdown("_Analyse, Interprétation et Recommandations Intelligentes_")
    
    st.markdown("---")
    uploaded_file = st.file_uploader(
        "#### Téléverser un résultat d'analyse (PDF)",
        type=["pdf"],
        help="Chargez ici le fichier PDF contenant les résultats d’analyse du sol."
    )

    if uploaded_file is not None:
        st.success(f"✅ Fichier chargé : **{uploaded_file.name}**")

    st.markdown("---")
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px;">
        <img src="https://maliagriculture.com/gallery/logo%20n1.jpg?ts=1757619351" width="50">
        <div>
            <strong>© 2025 MaliAgriculture.com</strong><br>
            🌱 AI solution for Agriculture.
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- Main Page --- #
st.markdown("<h1 style='text-align: center; color: #4CAF50; font-weight: 700; margin-bottom: 2rem;'>🌱 Rapport d'Analyse automatique de Sol</h1>", unsafe_allow_html=True)

if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'show_summaries' not in st.session_state:
    st.session_state.show_summaries = {'wo': False, 'bm': False}
if 'current_file_id' not in st.session_state:
    st.session_state.current_file_id = None


def reset_report_state():
    st.session_state.report_data = None
    st.session_state.show_summaries = {'wo': False, 'bm': False}


if uploaded_file:
    file_bytes = uploaded_file.getvalue()
    file_id = f"{uploaded_file.name}-{len(file_bytes)}"

    if st.session_state.current_file_id != file_id:
        reset_report_state()
        st.session_state.current_file_id = file_id

    if st.session_state.report_data is None:
        with st.spinner("Analyse complète en cours (FR, WO, BM)... Ceci peut prendre jusqu'à 1 minute."):
            files = {"file": (uploaded_file.name, file_bytes, "application/pdf")}
            try:
                response = requests.post(f"{API_URL}/analyze", files=files, timeout=240)
                if response.status_code == 200:
                    st.session_state.report_data = response.json()
                else:
                    st.error(f"Erreur de l'API: {response.text}")
                    st.session_state.report_data = {"error": True}
            except requests.exceptions.RequestException as e:
                st.error(f"Erreur de connexion à l'API: {e}")
                st.session_state.report_data = {"error": True}
else:
    if st.session_state.report_data is not None or st.session_state.current_file_id is not None:
        reset_report_state()
        st.session_state.current_file_id = None

# Display the report if it exists and there's no error
if st.session_state.report_data and not st.session_state.report_data.get("error"):
    data = st.session_state.report_data
    
    # Main French Report content
    with st.container():
        st.markdown(data["report"], unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Summaries Section in a styled card
    st.markdown("""
    <div class="language-section">
        <h2>🌐 Résumés dans d'autres langues</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🇸🇳 Afficher le résumé en Wolof"):
            st.session_state.show_summaries['wo'] = not st.session_state.show_summaries['wo']

    with col2:
        if st.button("🇲🇱 Afficher le résumé en Bambara"):
            st.session_state.show_summaries['bm'] = not st.session_state.show_summaries['bm']

    # Display revealed summaries
    if st.session_state.show_summaries['wo']:
        with st.expander("📖 Résumé en Wolof", expanded=True):
            st.markdown(data.get("summary_wo", "Résumé non disponible."))
    
    if st.session_state.show_summaries['bm']:
        with st.expander("📖 Résumé en Bambara", expanded=True):
            st.markdown(data.get("summary_bm", "Résumé non disponible."))
else:
    st.markdown("""
    <div style="background-color: #FFFFFF; border-radius: 12px; padding: 3rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-top: 2rem;">
        <h3 style="color: #795548; margin-bottom: 1rem;">📄 Commencez votre analyse</h3>
        <p style="color: #666; font-size: 1.1rem;">Veuillez téléverser un fichier PDF pour commencer l'analyse de votre sol.</p>
    </div>
    """, unsafe_allow_html=True)
