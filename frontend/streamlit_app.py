# frontend/streamlit_app.py
import os
import sys
import warnings
import logging
from io import BytesIO

import streamlit as st
import requests
import markdown
from dotenv import load_dotenv

# --- 🔇 Suppression des warnings et logs inutiles ---
warnings.filterwarnings("ignore")
logging.getLogger("streamlit").setLevel(logging.ERROR)
logging.getLogger("weasyprint").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)
os.environ["G_MESSAGES_DEBUG"] = "none"
os.environ["PYTHONWARNINGS"] = "ignore"

# --- Chargement des variables d'environnement ---
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- Suppression silencieuse des erreurs stderr ---
def _suppress_stderr():
    class _Ctx:
        def __enter__(self):
            self._stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")
        def __exit__(self, exc_type, exc, tb):
            try:
                sys.stderr.close()
            finally:
                sys.stderr = self._stderr
    return _Ctx()

# --- Configuration de la page ---
st.set_page_config(
    page_title="SoilSmart par MaliAgriculture",
    page_icon="🌱",
    layout="wide"
)

# --- Custom CSS global ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.main { background-color: #F9F9F6; color: #333333; }
[data-testid="stSidebar"] {
    background-color: #FFFFFF; border-radius: 15px; padding: 1.5rem; margin: 0.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08); overflow-y: auto; max-height: 90vh;
}
.mobile-header {
    display: none; text-align: center; background-color: #FFFFFF;
    border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    padding: 1rem 0.5rem; margin-bottom: 1rem;
}
.mobile-header img { width: 80px; }
.mobile-header h1 { color: #4CAF50; font-size: 1.4rem; margin-bottom: 0.25rem; }
.stButton>button {
    border-radius: 10px; border: 2px solid #4CAF50;
    background-color: #4CAF50; color: white;
    padding: 12px 28px; font-weight: 600; font-size: 1rem; width: 100%;
    box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2); transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #FFFFFF; color: #4CAF50; border-color: #4CAF50;
    transform: translateY(-2px);
}
.report-card, .language-section {
    background-color: #FFFFFF; border-radius: 12px;
    padding: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
}
@media (max-width: 768px) {
    [data-testid="stSidebar"] { display: none !important; }
    .mobile-header { display: block; }
    .main { margin-left: 0 !important; padding: 0.5rem; }
}
</style>
""", unsafe_allow_html=True)

# --- En-tête mobile ---
st.markdown("""
<div class="mobile-header">
    <img src="https://maliagriculture.com/gallery/logo%20n1.jpg?ts=1757619351">
    <h1>🌱 SoilSmart-AI</h1>
</div>
""", unsafe_allow_html=True)

# --- Barre latérale ---
with st.sidebar:
    st.markdown("<h1 style='color: #4CAF50; font-weight: 700;'>🌱 Soil Smart</h1>", unsafe_allow_html=True)
    st.markdown("_Innovation au service de vos sols et cultures_")
    st.markdown("---")
    sidebar_uploaded_file = st.file_uploader(
        "#### Téléverser un résultat d'analyse (PDF)",
        type=["pdf"],
        key="sidebar_uploader"
    )
    if sidebar_uploaded_file:
        st.success(f"✅ Fichier chargé : **{sidebar_uploaded_file.name}**")
    st.markdown("---")
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px;">
        <img src="https://maliagriculture.com/gallery/logo%20n1.jpg?ts=1757619351" width="50">
        <div>
            <strong>© 2025 MaliAgriculture.com</strong><br>
            Smart Solutions for Agriculture
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Titre principal ---
st.markdown("<h1 style='text-align: center; color: #4CAF50; font-weight: 700;'>Rapport d’Analyse Agronomique et Recommandations Stratégiques</h1>", unsafe_allow_html=True)

# --- Initialisation session ---
if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'show_summaries' not in st.session_state:
    st.session_state.show_summaries = {'wo': False, 'bm': False}
if 'current_file_id' not in st.session_state:
    st.session_state.current_file_id = None

def reset_report_state():
    st.session_state.report_data = None
    st.session_state.show_summaries = {'wo': False, 'bm': False}

# --- Upload du fichier ---
if not st.session_state.report_data or st.session_state.report_data.get("error"):
    st.markdown("""
    <div style="background-color:#FFFFFF;border-radius:12px;padding:3rem;text-align:center;
    box-shadow:0 4px 12px rgba(0,0,0,0.08);margin-top:2rem;">
        <h3 style="color:#795548;">Commencez votre analyse</h3>
        <p style="color:#666;">Veuillez téléverser un fichier PDF pour commencer l'analyse de votre sol.</p>
    </div>
    """, unsafe_allow_html=True)
    body_uploaded_file = st.file_uploader("Téléverser un fichier PDF", type=["pdf"], key="body_uploader", label_visibility="collapsed")
else:
    body_uploaded_file = None

uploaded_file = sidebar_uploaded_file or body_uploaded_file

if uploaded_file:
    file_bytes = uploaded_file.getvalue()
    file_id = f"{uploaded_file.name}-{len(file_bytes)}"

    # 🧠 Empêche le rechargement inutile du même rapport
    if st.session_state.report_data is not None and st.session_state.current_file_id == file_id:
        st.stop()

    if st.session_state.current_file_id != file_id:
        reset_report_state()
        st.session_state.current_file_id = file_id

    if st.session_state.report_data is None:
        with st.spinner("Analyse complète en cours (FR, WO, BM)..."):
            try:
                response = requests.post(f"{API_URL}/analyze", files={"file": (uploaded_file.name, file_bytes, "application/pdf")}, timeout=240)
                if response.status_code == 200:
                    st.session_state.report_data = response.json()
                else:
                    st.error(f"Erreur de l'API: {response.text}")
                    st.session_state.report_data = {"error": True}
            except requests.exceptions.RequestException as e:
                st.error(f"Erreur de connexion à l'API: {e}")
                st.session_state.report_data = {"error": True}
else:
    if st.session_state.current_file_id and not st.session_state.report_data:
        reset_report_state()
        st.session_state.current_file_id = None

# --- Affichage du rapport ---
if st.session_state.report_data and not st.session_state.report_data.get("error"):
    data = st.session_state.report_data
    report_html = data["report"]
    st.markdown(report_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Résumés multilingues ---
    st.markdown('<div class="language-section"><h2>Résumés dans d\'autres langues</h2></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Résumé en Wolof"):
            st.session_state.show_summaries['wo'] = not st.session_state.show_summaries['wo']
    with col2:
        if st.button("Résumé en Bambara"):
            st.session_state.show_summaries['bm'] = not st.session_state.show_summaries['bm']

    if st.session_state.show_summaries['wo']:
        with st.expander("Résumé en Wolof", expanded=True):
            st.markdown(data.get("summary_wo", "Résumé non disponible."))
    if st.session_state.show_summaries['bm']:
        with st.expander("Résumé en Bambara", expanded=True):
            st.markdown(data.get("summary_bm", "Résumé non disponible."))

    # --- Téléchargement PDF ---
    try:
        from weasyprint import HTML
        md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
        report_html_converted = md.convert(report_html)
        pdf_html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8">
        <style>@page{{size:A4;margin:2cm;}}body{{font-family:'DejaVu Sans',Arial;line-height:1.8;}}</style>
        </head><body>{report_html_converted}</body></html>
        """
        with _suppress_stderr():
            pdf_bytes = HTML(string=pdf_html, base_url=".").write_pdf()
        st.download_button(
            label="⬇️ Télécharger le rapport en PDF",
            data=pdf_bytes,
            file_name="rapport_soilsmart.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except ImportError:
        st.warning("⚠️ WeasyPrint n'est pas installé. Ajoutez 'weasyprint' et 'cairocffi' dans requirements.txt.")
    except Exception as e:
        st.error(f"❌ Erreur PDF: {str(e)[:200]}")
        st.info("💡 Utilisez Ctrl+P pour enregistrer en PDF si le problème persiste.")
