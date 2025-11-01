# frontend/streamlit_app.py
from dotenv import load_dotenv
import os
import streamlit as st
import requests
import markdown

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- Page Configuration ---
st.set_page_config(
    page_title="SoilSmart par MaliAgriculture",
    page_icon="🌱",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* --- General --- */
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.main { background-color: #F9F9F6; color: #333333; }

/* --- Sidebar --- */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 0.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    overflow-y: auto;
    max-height: 90vh;
}

/* --- Mobile Header --- */
.mobile-header {
    display: none;
    text-align: center;
    background-color: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    padding: 1rem 0.5rem;
    margin-bottom: 1rem;
}
.mobile-header img { width: 80px; }
.mobile-header h1 { color: #4CAF50; font-size: 1.4rem; margin-bottom: 0.25rem; }
.mobile-header .mobile-uploader { margin-top: 0.5rem; }

/* --- Buttons --- */
.stButton>button {
    border-radius: 10px; border: 2px solid #4CAF50;
    background-color: #4CAF50; color: white;
    padding: 12px 28px; font-weight: 600;
    font-size: 1rem; width: 100%;
    box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #FFFFFF; color: #4CAF50; border-color: #4CAF50;
    transform: translateY(-2px);
}

/* --- Cards --- */
.report-card, .language-section {
    background-color: #FFFFFF; border-radius: 12px;
    padding: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
}

/* --- Mobile Responsive --- */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { display: none !important; }
    .mobile-header { display: block; }
    .main { margin-left: 0 !important; padding: 0.5rem; }
    .stButton>button { font-size: 0.9rem; padding: 10px 18px; }
    [data-testid="stFileUploader"] { width: 100% !important; padding: 0.8rem !important; }
}
</style>
""", unsafe_allow_html=True)

# --- Mobile Header with uploader ---
st.markdown("""
<div class="mobile-header">
    <img src="https://maliagriculture.com/gallery/logo%20n1.jpg?ts=1757619351">
    <h1>🌱 SoilSmart-AI</h1>
</div>
""", unsafe_allow_html=True)

# --- Sidebar (Desktop) ---
with st.sidebar:
    st.markdown("<h1 style='color: #4CAF50; font-weight: 700;'>🌱 Soil Smart</h1>", unsafe_allow_html=True)
    st.markdown("_Innovation au service de vos sols et cultures_")
    st.markdown("---")
    sidebar_uploaded_file = st.file_uploader(
        "#### Téléverser un résultat d'analyse (PDF)",
        type=["pdf"],
        key="sidebar_uploader"
    )
    if sidebar_uploaded_file is not None:
        st.success(f"✅ Fichier chargé : **{sidebar_uploaded_file.name}**")
    st.markdown("---")
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px;">
        <img src="https://maliagriculture.com/gallery/logo%20n1.jpg?ts=1757619351" width="50">
        <div>
            <strong>© 2025 MaliAgriculture.com</strong><br>
            🌱 Smart Solution for Agriculture.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Main Page ---
st.markdown("<h1 style='text-align: center; color: #4CAF50; font-weight: 700;'>🌱 Rapport d’Analyse Agronomique et Recommandations Stratégiques</h1>", unsafe_allow_html=True)

# --- Session state ---
if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'show_summaries' not in st.session_state:
    st.session_state.show_summaries = {'wo': False, 'bm': False}
if 'current_file_id' not in st.session_state:
    st.session_state.current_file_id = None

def reset_report_state():
    st.session_state.report_data = None
    st.session_state.show_summaries = {'wo': False, 'bm': False}

# --- Show uploader if no report exists ---
if not st.session_state.report_data or st.session_state.report_data.get("error"):
    st.markdown("""
    <div style="background-color: #FFFFFF; border-radius: 12px; padding: 3rem 3rem 2rem 3rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-top: 2rem;">
        <h3 style="color: #795548; margin-bottom: 1rem;">📄 Commencez votre analyse</h3>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">Veuillez téléverser un fichier PDF pour commencer l'analyse de votre sol.</p>
    </div>
    """, unsafe_allow_html=True)
    
    body_uploaded_file = st.file_uploader(
        "Téléverser un fichier PDF",
        type=["pdf"],
        key="body_uploader",
        label_visibility="collapsed"
    )
else:
    body_uploaded_file = None

# --- Upload handling ---
# Determine which file to use (sidebar takes priority if both exist)
if sidebar_uploaded_file:
    uploaded_file = sidebar_uploaded_file
elif body_uploaded_file:
    uploaded_file = body_uploaded_file
else:
    uploaded_file = None

if uploaded_file:
    file_bytes = uploaded_file.getvalue()
    file_id = f"{uploaded_file.name}-{len(file_bytes)}"
    if st.session_state.current_file_id != file_id:
        reset_report_state()
        st.session_state.current_file_id = file_id
    if st.session_state.report_data is None:
        with st.spinner("Analyse complète en cours (FR, WO, BM)..."):
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
    # No file uploaded, reset state if needed
    if st.session_state.current_file_id is not None and not st.session_state.report_data:
        reset_report_state()
        st.session_state.current_file_id = None

# --- Display report and download PDF ---
if st.session_state.report_data and not st.session_state.report_data.get("error"):
    data = st.session_state.report_data
    report_html = data["report"]

    st.markdown(report_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Résumés dans d'autres langues
    st.markdown('<div class="language-section"><h2>🌐 Résumés dans d\'autres langues</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇸🇳 Afficher le résumé en Wolof"):
            st.session_state.show_summaries['wo'] = not st.session_state.show_summaries['wo']
    with col2:
        if st.button("🇲🇱 Afficher le résumé en Bambara"):
            st.session_state.show_summaries['bm'] = not st.session_state.show_summaries['bm']

    if st.session_state.show_summaries['wo']:
        with st.expander("📖 Résumé en Wolof", expanded=True):
            st.markdown(data.get("summary_wo", "Résumé non disponible."))
    if st.session_state.show_summaries['bm']:
        with st.expander("📖 Résumé en Bambara", expanded=True):
            st.markdown(data.get("summary_bm", "Résumé non disponible."))

    # --- Bouton téléchargement PDF ---
    try:
        from weasyprint import HTML
        
        # Convert Markdown to HTML (the report is in Markdown format)
        md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
        report_html_converted = md.convert(report_html)
        
        # Wrap converted HTML in a complete HTML document with proper CSS
        # Use system fonts instead of @import for better WeasyPrint compatibility
        pdf_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    margin: 2cm;
                    size: A4;
                }}
                body {{
                    font-family: 'DejaVu Sans', 'Arial', 'Helvetica', sans-serif;
                    color: #333333;
                    line-height: 1.8;
                    padding: 10px;
                    font-size: 11pt;
                }}
                h1 {{
                    color: #4CAF50;
                    font-size: 22pt;
                    font-weight: bold;
                    margin-top: 1.5em;
                    margin-bottom: 0.8em;
                    page-break-after: avoid;
                }}
                h2 {{
                    color: #4CAF50;
                    font-size: 18pt;
                    font-weight: bold;
                    margin-top: 1.3em;
                    margin-bottom: 0.6em;
                    page-break-after: avoid;
                }}
                h3 {{
                    color: #4CAF50;
                    font-size: 14pt;
                    font-weight: bold;
                    margin-top: 1.1em;
                    margin-bottom: 0.5em;
                    page-break-after: avoid;
                }}
                h4 {{
                    color: #666;
                    font-size: 12pt;
                    font-weight: bold;
                    margin-top: 1em;
                    margin-bottom: 0.4em;
                }}
                p {{
                    margin-bottom: 1em;
                    text-align: justify;
                }}
                ul, ol {{
                    margin-left: 2em;
                    margin-bottom: 1em;
                }}
                li {{
                    margin-bottom: 0.5em;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 1.5em 0;
                    page-break-inside: avoid;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: left;
                    font-size: 10pt;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .report-card {{
                    background-color: #f5f5f5;
                    padding: 1.5em;
                    margin-bottom: 1.5em;
                    border-left: 4px solid #4CAF50;
                }}
                strong {{
                    font-weight: bold;
                    color: #000;
                }}
                em {{
                    font-style: italic;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 5px;
                    font-family: 'Courier New', monospace;
                    font-size: 10pt;
                }}
                .page-break {{
                    page-break-before: always;
                }}
            </style>
        </head>
        <body>
            {report_html_converted}
        </body>
        </html>
        """
        
        pdf_bytes = HTML(string=pdf_html).write_pdf()
        st.download_button(
            label="⬇️ Télécharger le rapport en PDF",
            data=pdf_bytes,
            file_name="rapport_soilsmart.pdf",
            mime="application/pdf"
        )
    except (ImportError, OSError) as e:
        st.info("💡 Le téléchargement PDF n'est pas disponible sur ce système. Vous pouvez utiliser la fonction d'impression de votre navigateur pour sauvegarder le rapport.")
        # Uncomment to see detailed error: st.error(f"Erreur: {e}")
